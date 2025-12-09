"""
EDMGP Data Refinery - Command Line Interface
Test interface for the core processing logic (before Streamlit UI)
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple
import numpy as np

# Import our modules
from ingestion import FileIngester, FilePair
from audio_processing import AlignedSlicer, AudioProcessor, MIDIProcessor
from metadata import MetadataGenerator, TrackMetadata
from export import ExportSession
import config


class DataRefineryApp:
    """Main application class for data processing"""
    
    def __init__(self):
        self.ingester: Optional[FileIngester] = None
        self.slicer = AlignedSlicer()
        self.metadata_gen = MetadataGenerator()
        self.export_session: Optional[ExportSession] = None
        
    def ingest_directory(
        self,
        source_dir: str,
        vocal_rights: str = "Exclusive"
    ):
        """
        Ingest and pair files from source directory
        
        Args:
            source_dir: Source directory path
            vocal_rights: Vocal rights setting
        """
        print("\n" + "="*60)
        print("STEP 1: INGESTION & AUTO-PAIRING")
        print("="*60)
        
        self.ingester = FileIngester(source_dir, vocal_rights)
        self.ingester.scan_files()
        self.ingester.auto_pair_files()
        
        print(self.ingester.get_pairing_report())
    
    def process_track(
        self,
        output_dir: str,
        track_title: str,
        genre: str,
        bpm: Optional[float],
        key: str,
        vocal_rights: str,
        energy_level: int,
        mood: list,
        start_bars: float = 0,
        end_bars: Optional[float] = None,
        stem_labels: Optional[dict] = None
    ):
        """
        Process a complete track with all stems
        
        Args:
            output_dir: Output directory
            track_title: Original track name
            genre: Genre tag
            bpm: BPM (None to auto-detect)
            key: Musical key
            vocal_rights: Vocal rights setting
            energy_level: Energy level (1-5)
            mood: List of mood tags
            start_bars: Start position in bars
            end_bars: End position in bars (None = full duration)
            stem_labels: Dictionary mapping audio filenames to (group, instrument, layer)
        """
        if self.ingester is None or not self.ingester.pairs:
            print("❌ No files ingested. Run ingest_directory() first.")
            return
        
        print("\n" + "="*60)
        print("STEP 2: PROCESSING & EXPORT")
        print("="*60)
        
        # Start export session
        self.export_session = ExportSession(output_dir)
        batch_path = self.export_session.start_batch()
        
        # Generate UID
        uid = self.metadata_gen.get_next_uid(Path(output_dir))
        
        # Get BPM from first MIDI if not provided
        if bpm is None:
            for pair in self.ingester.pairs:
                if pair.midi:
                    midi_proc = MIDIProcessor()
                    midi_info = midi_proc.get_midi_info(pair.midi.path)
                    bpm = midi_info.tempo
                    print(f"✓ Using BPM from MIDI: {bpm:.1f}")
                    break
            
            # Still no BPM? Detect from first audio
            if bpm is None:
                audio_proc = AudioProcessor()
                first_pair = self.ingester.pairs[0]
                audio, sr = audio_proc.load_audio(first_pair.audio.path)
                bpm = audio_proc.detect_bpm(audio, sr)
                print(f"✓ Detected BPM from audio: {bpm:.1f}")
        
        # Create track directory
        track_path = self.export_session.start_track(uid, genre, bpm, key)
        
        # Process each stem
        audio_count = 0
        midi_count = 0
        
        for i, pair in enumerate(self.ingester.pairs):
            print(f"\nProcessing stem {i+1}/{len(self.ingester.pairs)}: {pair.audio.filename}")
            
            # Get stem labels (from provided dict or use defaults)
            if stem_labels and pair.audio.filename in stem_labels:
                group, instrument, layer = stem_labels[pair.audio.filename]
            else:
                # Default labels (would come from UI in full app)
                group = "Drums"  # Default (using taxonomy format)
                instrument = "Kick"
                layer = "Main"
                print(f"  ⚠ Using default labels: {group}/{instrument}/{layer}")
            
            # Normalize labels to match taxonomy format
            group = config.normalize_group(group)
            instrument = config.normalize_instrument(instrument)
            layer = config.normalize_layer(layer)
            
            # Determine end bars if not specified
            if end_bars is None:
                # Default to 16 bars for demo
                current_end_bars = 16
            else:
                current_end_bars = end_bars
            
            # Slice audio and MIDI
            try:
                sliced_audio, sample_rate, sliced_midi = self.slicer.slice_pair(
                    pair.audio.path,
                    pair.midi.path if pair.midi else None,
                    start_bars,
                    current_end_bars,
                    tempo=bpm
                )
                
                # Export stem
                self.export_session.export_stem(
                    sliced_audio,
                    sample_rate,
                    sliced_midi,
                    uid,
                    group,
                    instrument,
                    layer
                )
                
                audio_count += 1
                if sliced_midi:
                    midi_count += 1
                    
            except Exception as e:
                print(f"  ❌ Error processing stem: {e}")
                continue
        
        # Generate and export metadata
        metadata = self.metadata_gen.create_metadata(
            uid=uid,
            original_title=track_title,
            bpm=bpm,
            key=key,
            genre=genre,
            audio_count=audio_count,
            midi_count=midi_count,
            vocal_rights=vocal_rights,
            energy_level=energy_level,
            mood=mood
        )
        
        # Validate metadata
        errors = self.metadata_gen.validate_metadata(metadata)
        if errors:
            print("\n⚠ Metadata validation warnings:")
            for error in errors:
                print(f"  - {error}")
        
        # Finalize track
        self.export_session.finalize_track(metadata)
        
        print(f"\n✅ TRACK EXPORT COMPLETE")
        print(f"Output location: {track_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="EDMGP Data Refinery - Audio/MIDI Dataset Processing Tool"
    )
    
    parser.add_argument(
        "source_dir",
        help="Source directory containing audio and MIDI files"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="Clean_Dataset_Staging",
        help="Output directory (default: Clean_Dataset_Staging)"
    )
    
    parser.add_argument(
        "-t", "--title",
        default="Untitled",
        help="Track title"
    )
    
    parser.add_argument(
        "-g", "--genre",
        default="trap",
        choices=[g.lower() for g in config.GENRES],
        help="Genre"
    )
    
    parser.add_argument(
        "-b", "--bpm",
        type=float,
        help="BPM (auto-detect if not specified)"
    )
    
    parser.add_argument(
        "-k", "--key",
        default="Cmin",
        help="Musical key (e.g., Fmin, Gmaj)"
    )
    
    parser.add_argument(
        "-v", "--vocal-rights",
        default="Exclusive",
        choices=["Exclusive", "Royalty_Free"],
        help="Vocal rights setting"
    )
    
    parser.add_argument(
        "-e", "--energy",
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help="Energy level (1-5)"
    )
    
    parser.add_argument(
        "-m", "--mood",
        nargs="+",
        default=["dark"],
        help="Mood tags (max 2)"
    )
    
    parser.add_argument(
        "--start-bars",
        type=float,
        default=0,
        help="Start position in bars"
    )
    
    parser.add_argument(
        "--end-bars",
        type=float,
        default=16,
        help="End position in bars"
    )
    
    args = parser.parse_args()
    
    # Create app instance
    app = DataRefineryApp()
    
    # Ingest files
    app.ingest_directory(args.source_dir, args.vocal_rights)
    
    # Process track
    app.process_track(
        output_dir=args.output,
        track_title=args.title,
        genre=args.genre,
        bpm=args.bpm,
        key=args.key,
        vocal_rights=args.vocal_rights,
        energy_level=args.energy,
        mood=args.mood[:2],  # Max 2 moods
        start_bars=args.start_bars,
        end_bars=args.end_bars
    )


if __name__ == "__main__":
    main()
