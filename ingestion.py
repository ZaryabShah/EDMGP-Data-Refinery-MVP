"""
Audio and MIDI file ingestion and pairing module
Handles file discovery, fuzzy matching, and vocal filtering
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from rapidfuzz import fuzz
import config


@dataclass(frozen=True)
class AudioFile:
    """Represents an audio file with its properties"""
    path: Path
    filename: str
    normalized_name: str = ""
    
    def __post_init__(self):
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, 'normalized_name', self._normalize_filename(self.filename))
    
    @staticmethod
    def _normalize_filename(filename: str) -> str:
        """Normalize filename for fuzzy matching"""
        # Remove extension
        name = Path(filename).stem
        # Convert to lowercase
        name = name.lower()
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        # Remove extra spaces
        name = ' '.join(name.split())
        return name


@dataclass(frozen=True)
class MIDIFile:
    """Represents a MIDI file with its properties"""
    path: Path
    filename: str
    normalized_name: str = ""
    
    def __post_init__(self):
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, 'normalized_name', self._normalize_filename(self.filename))
    
    @staticmethod
    def _normalize_filename(filename: str) -> str:
        """Normalize filename for fuzzy matching"""
        name = Path(filename).stem
        name = name.lower()
        name = name.replace('_', ' ').replace('-', ' ')
        name = ' '.join(name.split())
        return name


@dataclass
class FilePair:
    """Represents a paired audio and MIDI file"""
    audio: AudioFile
    midi: Optional[MIDIFile] = None
    match_score: float = 0.0
    is_vocal: bool = False
    group: Optional[str] = None


class FileIngester:
    """Handles file ingestion and auto-pairing"""
    
    def __init__(self, source_directory: str, vocal_rights: str = "Exclusive"):
        """
        Initialize the file ingester
        
        Args:
            source_directory: Path to the source directory containing audio/MIDI files
            vocal_rights: "Exclusive" or "Royalty_Free" (affects vocal filtering)
        """
        self.source_dir = Path(source_directory)
        self.vocal_rights = vocal_rights
        self.audio_files: List[AudioFile] = []
        self.midi_files: List[MIDIFile] = []
        self.pairs: List[FilePair] = []
        
    def scan_files(self) -> Tuple[List[AudioFile], List[MIDIFile]]:
        """
        Scan the source directory for audio and MIDI files (recursive and case-insensitive)
        V1.1: Now fully recursive with case-insensitive extension matching
        
        Returns:
            Tuple of (audio_files, midi_files)
        """
        audio_files = []
        midi_files = []
        
        # Walk through directory recursively (including all subfolders)
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()  # Case-insensitive extension check
                
                # Check for audio files
                if ext in config.SUPPORTED_AUDIO_FORMATS:
                    audio_file = AudioFile(
                        path=file_path,
                        filename=file
                    )
                    audio_files.append(audio_file)
                
                # Check for MIDI files (case-insensitive: .mid, .MID, .midi, .MIDI)
                elif ext in config.SUPPORTED_MIDI_FORMATS:
                    midi_file = MIDIFile(
                        path=file_path,
                        filename=file
                    )
                    midi_files.append(midi_file)
        
        self.audio_files = audio_files
        self.midi_files = midi_files
        
        print(f"✓ Found {len(audio_files)} audio file(s)")
        print(f"✓ Found {len(midi_files)} MIDI file(s)")
        
        return audio_files, midi_files
    
    def is_vocal_file(self, audio_file: AudioFile) -> bool:
        """
        Determine if an audio file is a vocal stem
        
        Args:
            audio_file: AudioFile to check
            
        Returns:
            True if the file appears to be a vocal
        """
        normalized = audio_file.normalized_name.lower()
        
        for keyword in config.VOCAL_KEYWORDS:
            if keyword.replace('_', ' ') in normalized:
                return True
        
        return False
    
    def flag_vocal_files(self) -> List[int]:
        """
        Flag vocal files in pairs list (V1.1 - for visual highlighting)
        
        Returns:
            List of indices in self.pairs that contain vocal files
        """
        vocal_indices = []
        for idx, pair in enumerate(self.pairs):
            if self.is_vocal_file(pair.audio):
                vocal_indices.append(idx)
        return vocal_indices
    
    def remove_pair_by_index(self, index: int) -> bool:
        """
        Remove a pair from the pairs list by index (V1.1 - manual deletion)
        
        Args:
            index: Index of pair to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        if 0 <= index < len(self.pairs):
            del self.pairs[index]
            return True
        return False
    
    def find_best_midi_match(self, audio_file: AudioFile) -> Optional[Tuple[MIDIFile, float]]:
        """
        Find the best MIDI match for an audio file using fuzzy matching
        
        Args:
            audio_file: AudioFile to match
            
        Returns:
            Tuple of (best_match, score) or None if no good match found
        """
        if not self.midi_files:
            return None
        
        best_match = None
        best_score = 0.0
        
        for midi_file in self.midi_files:
            # Use token sort ratio for better matching with reordered words
            score = fuzz.token_sort_ratio(
                audio_file.normalized_name,
                midi_file.normalized_name
            )
            
            if score > best_score:
                best_score = score
                best_match = midi_file
        
        # Only return if score meets threshold
        if best_score >= config.FUZZY_MATCH_THRESHOLD:
            return (best_match, best_score)
        
        return None
    
    def auto_pair_files(self) -> List[FilePair]:
        """
        Automatically pair audio and MIDI files using fuzzy matching
        
        Returns:
            List of FilePair objects
        """
        pairs = []
        used_midi_files = set()
        
        for audio_file in self.audio_files:
            # Check if it's a vocal file
            is_vocal = self.is_vocal_file(audio_file)
            
            # If Royalty_Free vocals, skip vocal stems
            if self.vocal_rights == "Royalty_Free" and is_vocal:
                print(f"⚠ Skipping vocal file (Royalty_Free mode): {audio_file.filename}")
                continue
            
            # Try to find matching MIDI
            midi_match = None
            match_score = 0.0
            
            match_result = self.find_best_midi_match(audio_file)
            if match_result:
                midi_file, match_score = match_result
                if midi_file not in used_midi_files:
                    midi_match = midi_file
                    used_midi_files.add(midi_file)
            
            # Create pair
            pair = FilePair(
                audio=audio_file,
                midi=midi_match,
                match_score=match_score,
                is_vocal=is_vocal
            )
            
            pairs.append(pair)
        
        self.pairs = pairs
        
        # Print pairing results
        print(f"\n✓ Created {len(pairs)} file pair(s)")
        paired_count = sum(1 for p in pairs if p.midi is not None)
        print(f"  - {paired_count} with MIDI")
        print(f"  - {len(pairs) - paired_count} without MIDI")
        
        return pairs
    
    def validate_pairs(self) -> List[str]:
        """
        Validate pairs according to grouping rules
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        for pair in self.pairs:
            # For now, we can't validate groups since they're assigned later
            # This will be called after group assignment in the UI
            pass
        
        return warnings
    
    def get_pairing_report(self) -> str:
        """
        Generate a human-readable pairing report
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("\n" + "="*60)
        report.append("FILE PAIRING REPORT")
        report.append("="*60)
        
        for i, pair in enumerate(self.pairs, 1):
            report.append(f"\n{i}. {pair.audio.filename}")
            if pair.midi:
                report.append(f"   ↳ MIDI: {pair.midi.filename} (Match: {pair.match_score:.0f}%)")
            else:
                report.append(f"   ↳ MIDI: None")
            
            if pair.is_vocal:
                report.append(f"   ⚠ Detected as VOCAL")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test with sample data
    import sys
    
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = r"c:\Users\zarya\Desktop\Python\Music_upwork_Josh\EDMGP_developer_kit\EDMGP_developer_kit\Raw_input_sample"
    
    print(f"Scanning directory: {source_dir}\n")
    
    ingester = FileIngester(source_dir, vocal_rights="Exclusive")
    ingester.scan_files()
    ingester.auto_pair_files()
    
    print(ingester.get_pairing_report())