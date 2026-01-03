"""
Configuration file for EDMGP Data Refinery App
Contains all taxonomies, validation rules, and constants
V2: Loads taxonomy from external JSON file for dynamic updates
"""

import json
from pathlib import Path

# V2: Load taxonomy from external JSON file
TAXONOMY_PATH = Path(__file__).parent / "taxonomy_config.json"

try:
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        _TAXONOMY = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(
        f"taxonomy_config.json not found at {TAXONOMY_PATH}. "
        "Please ensure the file exists in the project root."
    )

# TAXONOMY DEFINITIONS (Loaded from taxonomy_config.json)

# Parent/Child Genre Structure
PARENT_GENRES = _TAXONOMY["parent_genres"]
SUB_GENRES = _TAXONOMY["sub_genres"]

# Track Attributes
ENERGY_LEVELS = _TAXONOMY["energy_levels"]
MOODS = _TAXONOMY["moods"]
VOCAL_RIGHTS = _TAXONOMY["vocal_rights"]

# STEM LABELING TAXONOMY
GROUPS = _TAXONOMY["groups"]
INSTRUMENTS = _TAXONOMY["instruments"]
LAYERS = _TAXONOMY["layers"]

# PROCESSING RULES (Loaded from JSON)
FORCE_MONO_INSTRUMENTS = _TAXONOMY["force_mono_instruments"]
KEEP_STEREO_GROUPS = _TAXONOMY["keep_stereo_groups"]
KEEP_STEREO_INSTRUMENTS = _TAXONOMY["keep_stereo_instruments"]

# Groups that REQUIRE MIDI pairing (melodic content)
REQUIRE_MIDI_GROUPS = _TAXONOMY["midi_required_groups"]
OPTIONAL_MIDI_GROUPS = _TAXONOMY["midi_optional_groups"]

# AUDIO SPECS
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_BIT_DEPTH = 24
SUPPORTED_AUDIO_FORMATS = [".wav", ".wave"]
SUPPORTED_MIDI_FORMATS = [".mid", ".midi"]

# OUTPUT STRUCTURE
OUTPUT_ROOT = "Clean_Dataset_Staging"
BATCH_PREFIX = "Batch"
UID_PREFIX = "GP"
UID_PADDING = 5  # GP_00001

# FILENAME SCHEMAS
AUDIO_FILENAME_SCHEMA = "{uid}_{group}_{instrument}_{layer}.wav"
MIDI_FILENAME_SCHEMA = "{uid}_midi_{group}_{instrument}.mid"
METADATA_FILENAME = "{uid}_info.json"

# FUZZY MATCHING THRESHOLD (0-100)
FUZZY_MATCH_THRESHOLD = 70

# VOCAL FILTERING (V1.1 - Enhanced for flagging)
VOCAL_KEYWORDS = [
    "vocal", "vox", "voice", "singer", "lead_vocal", "harmony",
    "adlib", "choir", "speech", "lyrics", "acapella", "accapella", "acappella"
]

# SAMPLE TYPES (V1.1 - For metadata schema v2)
SAMPLE_TYPES = ["one_shot", "loop", "full_track"]


# NORMALIZATION HELPERS FOR TAXONOMY

def normalize_group(g: str) -> str:
    """
    Normalize group name to match taxonomy format
    
    Args:
        g: Group name in any case
        
    Returns:
        Group name in TitleCase format (FX remains uppercase)
    """
    normalized = g.strip().capitalize()
    # Special case: FX should remain all uppercase
    if normalized.lower() == "fx":
        return "FX"
    return normalized


def normalize_instrument(i: str) -> str:
    """
    Normalize instrument name to match taxonomy format
    Handles underscores and multi-word instruments
    
    Args:
        i: Instrument name in any case
        
    Returns:
        Instrument name in taxonomy format (e.g., "Hat_Closed", "Mid_Bass")
    """
    # Replace spaces with underscores for consistency
    normalized = i.strip().replace(" ", "_")
    
    # Split by underscore, capitalize each part, rejoin
    parts = normalized.split("_")
    parts = [part.capitalize() for part in parts]
    return "_".join(parts)


def normalize_layer(l: str) -> str:
    """
    Normalize layer name to match taxonomy format
    
    Args:
        l: Layer name in any case
        
    Returns:
        Layer name in taxonomy format (e.g., "Main", "Layer1", "One_Shot")
    """
    # Replace spaces with underscores for consistency
    normalized = l.strip().replace(" ", "_")
    
    # Split by underscore, capitalize each part, rejoin
    parts = normalized.split("_")
    parts = [part.capitalize() for part in parts]
    return "_".join(parts)
