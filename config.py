"""
Configuration file for EDMGP Data Refinery App
Contains all taxonomies, validation rules, and constants
"""

# TAXONOMY DEFINITIONS (From MASTER TAXONOMY LIST)

GENRES = [
    "Tech_House", "Techno", "Deep_House", "Bass_House", "Progressive_House",
    "Big_Room", "Trap", "Dubstep", "Future_Bass", "Trance", "Pop", "Midtempo"
]

ENERGY_LEVELS = [
    "1_Low", "2_MedLow", "3_Medium", "4_High", "5_Max"
]

MOODS = [
    "Euphoric", "Dark", "Sad", "Happy", "Aggressive", 
    "Sexy", "Chill", "Quirky", "Epic", "Tense"
]

VOCAL_RIGHTS = ["Exclusive", "Royalty_Free"]

# STEM LABELING TAXONOMY
GROUPS = ["Drums", "Bass", "Synth", "Vocal", "FX", "Instruments", "Mix"]

# Instrument options per group
INSTRUMENTS = {
    "Drums": [
        "Kick", "Snare", "Clap", "Hat_Closed", "Hat_Open", "Crash", 
        "Ride", "Tom", "Percussion", "Top_Loop", "Drum_Loop", "Fill"
    ],
    "Bass": [
        "Sub", "Mid_Bass", "Reese", "Pluck", "Wobble", "808", "Acid"
    ],
    "Synth": [
        "Lead", "Chord", "Pad", "Arp", "Pluck", "Stab"
    ],
    "Instruments": [
        "Piano", "Guitar", "Strings", "Brass", "Mallets"
    ],
    "Vocal": [
        "Lead", "Double", "Harmony", "Adlib", "Choir", "Vocal_Chops", "Speech"
    ],
    "FX": [
        "Riser", "Downlifter", "Impact", "Noise", "Ambience", "Foley"
    ],
    "Mix": [
        "Master", "Premaster", "Instrumental"
    ]
}

LAYERS = [
    "Main", "Layer1", "Layer2", "Layer3", "Layer4",
    "Top", "Texture", "Dry", "Wet", "One_Shot", "Loop", "Roll"
]

# PROCESSING RULES

# Force mono for these instrument types
FORCE_MONO_INSTRUMENTS = [
    "Kick", "Snare", "Sub", "Lead"  # Lead Vocal or Lead Bass
]

# Keep stereo for these groups
KEEP_STEREO_GROUPS = ["FX", "Mix"]

# Keep stereo for these instruments
KEEP_STEREO_INSTRUMENTS = [
    "Pad", "Ambience", "Crash", "Ride", "Chord", "Arp"
]

# Groups that REQUIRE MIDI pairing (melodic content)
REQUIRE_MIDI_GROUPS = ["Bass", "Synth", "Instruments"]

# Groups where MIDI is optional
OPTIONAL_MIDI_GROUPS = ["Drums", "FX", "Vocal", "Mix"]

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

# VOCAL FILTERING
VOCAL_KEYWORDS = [
    "vocal", "vox", "voice", "singer", "lead_vocal", "harmony",
    "adlib", "choir", "speech", "lyrics"
]


# NORMALIZATION HELPERS FOR TAXONOMY

def normalize_group(g: str) -> str:
    """
    Normalize group name to match taxonomy format
    
    Args:
        g: Group name in any case
        
    Returns:
        Group name in TitleCase format
    """
    return g.strip().capitalize()


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
