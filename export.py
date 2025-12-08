"""
File export and renaming system
Handles output directory structure and file organization
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import config
from metadata import TrackMetadata, MetadataGenerator, StemValidator
from audio_processing import AudioProcessor


class FileExporter:
    """Handles file export with proper naming and directory structure"""
    
    def __init__(self, output_root: str = None):
        """
        Initialize file exporter
        
        Args:
            output_root: Root output directory (defaults to Clean_Dataset_Staging)
        """
        if output_root is None:
            output_root = config.OUTPUT_ROOT
        
        self.output_root = Path(output_root)
        self.audio_processor = AudioProcessor()
        self.metadata_generator = MetadataGenerator()
    
    def create_batch_directory(self, date: Optional[str] = None) -> Path:
        """
        Create batch directory for current processing session
        
        Args:
            date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Path to batch directory
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        batch_name = f"{config.BATCH_PREFIX}_{date}"
        batch_path = self.output_root / batch_name
        
        batch_path.mkdir(parents=True, exist_ok=True)
        
        return batch_path
    
    def create_track_directory(
        self,
        batch_path: Path,
        uid: str,
        genre: str,
        bpm: float,
        key: str
    ) -> Path:
        """
        Create track directory with naming schema
        
        Args:
            batch_path: Parent batch directory
            uid: Unique identifier
            genre: Genre tag
            bpm: BPM value
            key: Musical key
            
        Returns:
            Path to track directory
        """
        # Format: GP_00001_TechHouse_126_Fmin
        track_name = f"{uid}_{genre}_{int(bpm)}_{key}"
        track_path = batch_path / track_name
        
        # Create subdirectories
        track_path.mkdir(parents=True, exist_ok=True)
        (track_path / "Audio").mkdir(exist_ok=True)
        (track_path / "MIDI").mkdir(exist_ok=True)
        (track_path / "Metadata").mkdir(exist_ok=True)
        (track_path / "Masters").mkdir(exist_ok=True)
        
        return track_path
    
    def generate_audio_filename(
        self,
        uid: str,
        group: str,
        instrument: str,
        layer: str
    ) -> str:
        """
        Generate audio filename according to schema
        
        Args:
            uid: Unique identifier
            group: Stem group
            instrument: Stem instrument
            layer: Stem layer
            
        Returns:
            Filename (without path)
        """
        # Convert to lowercase for consistency
        group = group.lower()
        instrument = instrument.lower().replace(' ', '_')
        layer = layer.lower()
        
        return config.AUDIO_FILENAME_SCHEMA.format(
            uid=uid,
            group=group,
            instrument=instrument,
            layer=layer
        )
    
    def generate_midi_filename(
        self,
        uid: str,
        group: str,
        instrument: str
    ) -> str:
        """
        Generate MIDI filename according to schema
        
        Args:
            uid: Unique identifier
            group: Stem group
            instrument: Stem instrument
            
        Returns:
            Filename (without path)
        """
        group = group.lower()
        instrument = instrument.lower().replace(' ', '_')
        
        return config.MIDI_FILENAME_SCHEMA.format(
            uid=uid,
            group=group,
            instrument=instrument
        )
    
    def export_audio(
        self,
        audio_data,
        sample_rate: int,
        track_path: Path,
        uid: str,
        group: str,
        instrument: str,
        layer: str,
        force_mono: bool = False
    ) -> Path:
        """
        Export audio file with proper naming
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            track_path: Track directory path
            uid: Unique identifier
            group: Stem group
            instrument: Stem instrument
            layer: Stem layer
            force_mono: Force conversion to mono
            
        Returns:
            Path to exported file
        """
        # Check if should be mono
        if force_mono or StemValidator.should_force_mono(group, instrument):
            audio_data = self.audio_processor.convert_to_mono(audio_data)
        
        # Generate filename
        filename = self.generate_audio_filename(uid, group, instrument, layer)
        output_path = track_path / "Audio" / filename
        
        # Save audio
        self.audio_processor.save_audio(
            audio_data,
            sample_rate,
            output_path,
            bit_depth=config.DEFAULT_BIT_DEPTH
        )
        
        return output_path
    
    def export_midi(
        self,
        midi_data,
        track_path: Path,
        uid: str,
        group: str,
        instrument: str
    ) -> Path:
        """
        Export MIDI file with proper naming
        
        Args:
            midi_data: PrettyMIDI object
            track_path: Track directory path
            uid: Unique identifier
            group: Stem group
            instrument: Stem instrument
            
        Returns:
            Path to exported file
        """
        filename = self.generate_midi_filename(uid, group, instrument)
        output_path = track_path / "MIDI" / filename
        
        # Save MIDI
        midi_data.write(str(output_path))
        
        return output_path
    
    def export_metadata(
        self,
        metadata: TrackMetadata,
        track_path: Path
    ) -> Path:
        """
        Export metadata JSON file
        
        Args:
            metadata: TrackMetadata object
            track_path: Track directory path
            
        Returns:
            Path to exported file
        """
        filename = config.METADATA_FILENAME.format(uid=metadata.uid)
        output_path = track_path / "Metadata" / filename
        
        # Save metadata
        metadata.to_json(output_path)
        
        return output_path
    
    def copy_master_files(
        self,
        source_files: List[Path],
        track_path: Path
    ):
        """
        Copy master/mixdown files to Masters directory
        
        Args:
            source_files: List of source file paths
            track_path: Track directory path
        """
        masters_dir = track_path / "Masters"
        
        for source_file in source_files:
            if source_file.exists():
                dest_file = masters_dir / source_file.name
                shutil.copy2(source_file, dest_file)
    
    def get_export_summary(self, track_path: Path) -> Dict[str, int]:
        """
        Get summary of exported files
        
        Args:
            track_path: Track directory path
            
        Returns:
            Dictionary with file counts
        """
        summary = {
            "audio": 0,
            "midi": 0,
            "metadata": 0,
            "masters": 0
        }
        
        audio_dir = track_path / "Audio"
        if audio_dir.exists():
            summary["audio"] = len(list(audio_dir.glob("*.wav")))
        
        midi_dir = track_path / "MIDI"
        if midi_dir.exists():
            summary["midi"] = len(list(midi_dir.glob("*.mid")))
        
        metadata_dir = track_path / "Metadata"
        if metadata_dir.exists():
            summary["metadata"] = len(list(metadata_dir.glob("*.json")))
        
        masters_dir = track_path / "Masters"
        if masters_dir.exists():
            summary["masters"] = len(list(masters_dir.glob("*")))
        
        return summary


class ExportSession:
    """Manages a complete export session"""
    
    def __init__(self, output_root: str = None):
        """
        Initialize export session
        
        Args:
            output_root: Root output directory
        """
        self.exporter = FileExporter(output_root)
        self.batch_path = None
        self.track_path = None
        self.exported_files = []
    
    def start_batch(self, date: Optional[str] = None) -> Path:
        """
        Start a new batch
        
        Args:
            date: Batch date (defaults to today)
            
        Returns:
            Batch directory path
        """
        self.batch_path = self.exporter.create_batch_directory(date)
        print(f"✓ Created batch directory: {self.batch_path.name}")
        return self.batch_path
    
    def start_track(
        self,
        uid: str,
        genre: str,
        bpm: float,
        key: str
    ) -> Path:
        """
        Start a new track export
        
        Args:
            uid: Unique identifier
            genre: Genre
            bpm: BPM
            key: Musical key
            
        Returns:
            Track directory path
        """
        if self.batch_path is None:
            self.start_batch()
        
        self.track_path = self.exporter.create_track_directory(
            self.batch_path,
            uid,
            genre,
            bpm,
            key
        )
        
        print(f"✓ Created track directory: {self.track_path.name}")
        return self.track_path
    
    def export_stem(
        self,
        audio_data,
        sample_rate: int,
        midi_data,
        uid: str,
        group: str,
        instrument: str,
        layer: str
    ):
        """
        Export a complete stem (audio + MIDI)
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            midi_data: PrettyMIDI object (or None)
            uid: Unique identifier
            group: Stem group
            instrument: Stem instrument
            layer: Stem layer
        """
        if self.track_path is None:
            raise ValueError("No track started. Call start_track() first.")
        
        # Export audio
        audio_path = self.exporter.export_audio(
            audio_data, sample_rate, self.track_path,
            uid, group, instrument, layer
        )
        self.exported_files.append(audio_path)
        print(f"  ✓ Exported audio: {audio_path.name}")
        
        # Export MIDI if present
        if midi_data is not None:
            midi_path = self.exporter.export_midi(
                midi_data, self.track_path,
                uid, group, instrument
            )
            self.exported_files.append(midi_path)
            print(f"  ✓ Exported MIDI: {midi_path.name}")
    
    def finalize_track(self, metadata: TrackMetadata):
        """
        Finalize track export by saving metadata
        
        Args:
            metadata: TrackMetadata object
        """
        if self.track_path is None:
            raise ValueError("No track started.")
        
        # Export metadata
        metadata_path = self.exporter.export_metadata(metadata, self.track_path)
        print(f"  ✓ Exported metadata: {metadata_path.name}")
        
        # Get summary
        summary = self.exporter.get_export_summary(self.track_path)
        print(f"\n✓ Track export complete:")
        print(f"  - {summary['audio']} audio file(s)")
        print(f"  - {summary['midi']} MIDI file(s)")
        print(f"  - {summary['metadata']} metadata file(s)")
        
        # Reset track
        self.track_path = None


if __name__ == "__main__":
    # Test export system
    exporter = FileExporter()
    
    # Test filename generation
    audio_fn = exporter.generate_audio_filename("GP_00001", "drums", "kick", "main")
    print(f"Audio filename: {audio_fn}")
    
    midi_fn = exporter.generate_midi_filename("GP_00001", "bass", "sub")
    print(f"MIDI filename: {midi_fn}")
