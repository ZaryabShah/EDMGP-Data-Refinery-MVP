"""
Metadata generation and validation module
Generates JSON metadata files according to schema
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import config


@dataclass
class StemMetadata:
    """Metadata for individual stem"""
    group: str
    instrument: str
    layer: str
    is_mono: bool
    original_filename: str


@dataclass
class TrackMetadata:
    """Complete track metadata matching the schema"""
    uid: str
    original_track_title: str
    bpm: float
    key: str
    time_signature: str
    genre: str
    file_count: Dict[str, int]
    tags: Dict[str, Any]
    tech_specs: Dict[str, Any]
    processing_log: Dict[str, str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self, output_path: Path):
        """Save metadata to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class MetadataGenerator:
    """Generates metadata for processed tracks"""
    
    def __init__(self):
        self.current_uid = 0
    
    def generate_uid(self, base_number: Optional[int] = None) -> str:
        """
        Generate a unique identifier
        
        Args:
            base_number: Optional base number (otherwise auto-increment)
            
        Returns:
            UID string (e.g., "GP_00001")
        """
        if base_number is not None:
            number = base_number
        else:
            self.current_uid += 1
            number = self.current_uid
        
        return f"{config.UID_PREFIX}_{number:0{config.UID_PADDING}d}"
    
    def get_next_uid(self, output_root: Path) -> str:
        """
        Get the next available UID by scanning existing output
        
        Args:
            output_root: Root output directory
            
        Returns:
            Next available UID
        """
        max_uid = 0
        
        if output_root.exists():
            # Scan for existing UIDs
            for batch_dir in output_root.iterdir():
                if not batch_dir.is_dir():
                    continue
                
                for track_dir in batch_dir.iterdir():
                    if not track_dir.is_dir():
                        continue
                    
                    # Extract UID from directory name (e.g., "GP_00001_...")
                    dir_name = track_dir.name
                    if dir_name.startswith(config.UID_PREFIX + "_"):
                        try:
                            uid_part = dir_name.split('_')[1]
                            uid_num = int(uid_part)
                            max_uid = max(max_uid, uid_num)
                        except (IndexError, ValueError):
                            continue
        
        self.current_uid = max_uid
        return self.generate_uid()
    
    def create_metadata(
        self,
        uid: str,
        original_title: str,
        original_folder: str,
        bpm: float,
        key: str,
        genre_parent: str,
        genre_sub: str,
        audio_count: int,
        midi_count: int,
        vocal_rights: str,
        energy_level: int,
        mood: List[str],
        stems_manifest: List[Dict[str, Any]] = None,
        sample_rate: int = config.DEFAULT_SAMPLE_RATE,
        bit_depth: int = config.DEFAULT_BIT_DEPTH,
        time_signature: str = "4/4",
        contains_ai: bool = False,
        app_version: str = "v1.1"
    ) -> Dict[str, Any]:
        """
        Create complete track metadata (Schema V2)
        
        Args:
            uid: Unique identifier
            original_title: Original track name
            original_folder: Original folder name
            bpm: Tempo in BPM
            key: Musical key (e.g., "Fmin")
            genre_parent: Parent genre category
            genre_sub: Sub-genre
            audio_count: Number of audio files
            midi_count: Number of MIDI files
            vocal_rights: "exclusive" or "royalty_free"
            energy_level: Energy level (1-5)
            mood: List of mood tags
            stems_manifest: List of stem metadata dictionaries
            sample_rate: Sample rate
            bit_depth: Bit depth
            time_signature: Time signature
            contains_ai: Whether track contains AI-generated content
            app_version: Application version
            
        Returns:
            Dictionary matching metadata schema v2
        """
        metadata = {
            "uid": uid,
            "original_folder_name": original_folder,
            "global_attributes": {
                "genre_parent": genre_parent.lower().replace(" ", "_"),
                "genre_sub": genre_sub.lower().replace(" ", "_"),
                "bpm": bpm,
                "key": key,
                "energy_level": energy_level,
                "moods": [m.lower() for m in mood],
                "vocal_rights": vocal_rights.lower(),
                "contains_ai": contains_ai
            },
            "stems_manifest": stems_manifest if stems_manifest else [],
            "processing_info": {
                "date_processed": datetime.now().strftime("%Y-%m-%d"),
                "app_version": app_version
            }
        }
        
        return metadata
    
    def validate_metadata_v2(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Validate metadata against schema v2
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate UID format
        uid = metadata.get("uid", "")
        if not uid.startswith(config.UID_PREFIX + "_"):
            errors.append(f"UID must start with '{config.UID_PREFIX}_'")
        
        # Validate global attributes
        attrs = metadata.get("global_attributes", {})
        
        # Validate BPM range
        bpm = attrs.get("bpm", 0)
        if not (40 <= bpm <= 300):
            errors.append(f"BPM {bpm} is outside valid range (40-300)")
        
        # Validate genre
        genre_parent = attrs.get("genre_parent", "")
        if genre_parent not in config.PARENT_GENRES:
            errors.append(f"Genre parent '{genre_parent}' not in taxonomy")
        
        # Validate vocal rights
        vocal_rights = attrs.get("vocal_rights", "")
        if vocal_rights not in ["exclusive", "royalty_free"]:
            errors.append(f"vocal_rights must be 'exclusive' or 'royalty_free'")
        
        # Validate energy level
        energy = attrs.get("energy_level", 0)
        if not (1 <= energy <= 5):
            errors.append(f"energy_level must be 1-5")
        
        # Validate mood tags
        moods = attrs.get("moods", [])
        if len(moods) > 2:
            errors.append("Maximum 2 mood tags allowed")
        
        return errors


class StemValidator:
    """Validates stem labeling and processing rules (V2: Config-driven)"""
    
    def __init__(self):
        """Initialize validator with config-driven rules"""
        # Load mono/stereo rules from config
        self.force_mono_instruments = set(config.FORCE_MONO_INSTRUMENTS)
        self.keep_stereo_groups = set(config.KEEP_STEREO_GROUPS)
        self.keep_stereo_instruments = set(config.KEEP_STEREO_INSTRUMENTS)
        self.midi_required_groups = set(config.REQUIRE_MIDI_GROUPS)
    
    def should_force_mono(self, group: str, instrument: str) -> bool:
        """
        Determine if a stem should be forced to mono
        
        Args:
            group: Stem group
            instrument: Stem instrument
            
        Returns:
            True if should be mono
        """
        # Check force mono instruments
        if instrument in self.force_mono_instruments:
            return True
        
        # Lead vocals should be mono
        if group == "Vocal" and instrument == "Lead":
            return True
        
        # Snare main should be mono
        if group == "Drums" and instrument == "Snare":
            return True
        
        return False
    
    def should_keep_stereo(self, group: str, instrument: str) -> bool:
        """
        Determine if a stem should keep stereo
        
        Args:
            group: Stem group
            instrument: Stem instrument
            
        Returns:
            True if should keep stereo
        """
        # FX and Mix groups stay stereo
        if group in self.keep_stereo_groups:
            return True
        
        # Specific instruments stay stereo
        if instrument in self.keep_stereo_instruments:
            return True
        
        return False
    
    def requires_midi(self, group: str) -> bool:
        """
        Check if a group requires MIDI pairing
        
        Args:
            group: Stem group
            
        Returns:
            True if MIDI is required
        """
        return group in self.midi_required_groups
    
    def validate_stem(
        self,
        group: str,
        instrument: str,
        layer: str,
        has_midi: bool,
        is_mono: bool
    ) -> List[str]:
        """
        Validate stem configuration
        
        Args:
            group: Stem group
            instrument: Stem instrument
            layer: Stem layer
            has_midi: Whether MIDI is present
            is_mono: Whether audio is mono
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Check MIDI requirement
        if self.requires_midi(group) and not has_midi:
            warnings.append(f"⚠ {group} stems typically require MIDI pairing")
        
        # Check mono/stereo rules
        should_be_mono = self.should_force_mono(group, instrument)
        should_be_stereo = self.should_keep_stereo(group, instrument)
        
        if should_be_mono and not is_mono:
            warnings.append(f"⚠ {instrument} should be MONO")
        
        if should_be_stereo and is_mono:
            warnings.append(f"⚠ {instrument} should be STEREO")
        
        # Validate group/instrument combination
        if group in config.INSTRUMENTS:
            if instrument not in config.INSTRUMENTS[group]:
                warnings.append(f"⚠ '{instrument}' is not a standard option for {group}")
        
        # Validate layer
        if layer not in config.LAYERS:
            warnings.append(f"⚠ '{layer}' is not a standard layer type")
        
        return warnings
    
    # V2: Keep static methods for backwards compatibility
    @staticmethod
    def should_force_mono_static(group: str, instrument: str) -> bool:
        """Static version for backwards compatibility"""
        validator = StemValidator()
        return validator.should_force_mono(group, instrument)
    
    @staticmethod
    def should_keep_stereo_static(group: str, instrument: str) -> bool:
        """Static version for backwards compatibility"""
        validator = StemValidator()
        return validator.should_keep_stereo(group, instrument)
    
    @staticmethod
    def requires_midi_static(group: str) -> bool:
        """Static version for backwards compatibility"""
        validator = StemValidator()
        return validator.requires_midi(group)


if __name__ == "__main__":
    # Test metadata generation
    generator = MetadataGenerator()
    
    metadata = generator.create_metadata(
        uid="GP_00001",
        original_title="Fall Down",
        bpm=140,
        key="Fmin",
        genre="trap",
        audio_count=12,
        midi_count=4,
        vocal_rights="royalty_free",
        energy_level=5,
        mood=["aggressive", "dark"]
    )
    
    # Validate
    errors = generator.validate_metadata(metadata)
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Metadata is valid")
    
    # Print JSON
    print("\nGenerated metadata:")
    print(json.dumps(metadata.to_dict(), indent=2))
