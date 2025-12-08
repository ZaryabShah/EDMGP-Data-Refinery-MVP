"""
EDMGP Data Refinery - Usage Guide and Examples
"""

# ============================================================================
# EXAMPLE 1: Basic CLI Usage
# ============================================================================

# Process a folder with auto-detection
python run_app.py "C:/path/to/source/folder"

# Process with specific parameters
python run_app.py "C:/path/to/source/folder" \
    --title "My Track" \
    --genre trap \
    --bpm 140 \
    --key Fmin \
    --vocal-rights Exclusive \
    --energy 5 \
    --mood aggressive dark

# ============================================================================
# EXAMPLE 2: Using Individual Modules
# ============================================================================

from ingestion import FileIngester
from audio_processing import AlignedSlicer
from metadata import MetadataGenerator
from export import ExportSession

# Initialize components
ingester = FileIngester("path/to/source", vocal_rights="Exclusive")
slicer = AlignedSlicer()
metadata_gen = MetadataGenerator()
export_session = ExportSession("output/directory")

# Scan and pair files
ingester.scan_files()
ingester.auto_pair_files()
print(ingester.get_pairing_report())

# Process a single pair
pair = ingester.pairs[0]

# Slice audio and MIDI (0 to 16 bars)
sliced_audio, sample_rate, sliced_midi = slicer.slice_pair(
    audio_path=pair.audio.path,
    midi_path=pair.midi.path if pair.midi else None,
    start_bars=0,
    end_bars=16,
    tempo=140  # Or None to auto-detect
)

# Export with proper naming
export_session.start_batch()
track_path = export_session.start_track(
    uid="GP_00001",
    genre="trap",
    bpm=140,
    key="Fmin"
)

export_session.export_stem(
    audio_data=sliced_audio,
    sample_rate=sample_rate,
    midi_data=sliced_midi,
    uid="GP_00001",
    group="bass",
    instrument="sub",
    layer="main"
)

# ============================================================================
# EXAMPLE 3: Batch Processing Multiple Tracks
# ============================================================================

import os
from pathlib import Path

source_root = Path("C:/Music_Projects")
output_root = Path("C:/Clean_Dataset_Staging")

# Process each track folder
for track_folder in source_root.iterdir():
    if track_folder.is_dir():
        print(f"Processing: {track_folder.name}")
        
        # Initialize ingester for this track
        ingester = FileIngester(str(track_folder), vocal_rights="Exclusive")
        ingester.scan_files()
        ingester.auto_pair_files()
        
        # ... continue with processing ...

# ============================================================================
# EXAMPLE 4: Custom Stem Labeling
# ============================================================================

# Define custom labels for each file
stem_labels = {
    "kick_sample.wav": ("drums", "kick", "main"),
    "bass_line.wav": ("bass", "sub", "main"),
    "lead_synth.wav": ("synth", "lead", "layer1"),
    "pad_texture.wav": ("synth", "pad", "texture"),
}

# Use in processing
from run_app import DataRefineryApp

app = DataRefineryApp()
app.ingest_directory("source/folder")
app.process_track(
    output_dir="output",
    track_title="My Track",
    genre="trap",
    bpm=140,
    key="Fmin",
    vocal_rights="Exclusive",
    energy_level=5,
    mood=["dark", "aggressive"],
    stem_labels=stem_labels
)

# ============================================================================
# EXAMPLE 5: Validation and Quality Control
# ============================================================================

from metadata import StemValidator

# Validate stem configuration
warnings = StemValidator.validate_stem(
    group="bass",
    instrument="sub",
    layer="main",
    has_midi=True,
    is_mono=True
)

if warnings:
    for warning in warnings:
        print(warning)

# Check if should be mono
should_be_mono = StemValidator.should_force_mono("drums", "kick")
print(f"Kick should be mono: {should_be_mono}")  # True

# Check if requires MIDI
requires_midi = StemValidator.requires_midi("bass")
print(f"Bass requires MIDI: {requires_midi}")  # True

# ============================================================================
# EXAMPLE 6: Working with MIDI Tempo Maps
# ============================================================================

from audio_processing import MIDIProcessor
import pretty_midi

midi_proc = MIDIProcessor()

# Load and analyze MIDI
midi_data = midi_proc.load_midi(Path("track.mid"))
midi_info = midi_proc.get_midi_info(Path("track.mid"))

print(f"MIDI Duration: {midi_info.duration:.2f}s")
print(f"Tempo: {midi_info.tempo:.1f} BPM")
print(f"Time Signature: {midi_info.time_signature}")
print(f"Has Tempo Map: {midi_info.has_tempo_map}")

# Calculate bar duration
bar_duration = midi_proc.calculate_bar_duration(
    tempo=140,
    time_signature=(4, 4)
)
print(f"Bar duration at 140 BPM: {bar_duration:.2f}s")

# Convert bars to seconds
duration_16_bars = midi_proc.bars_to_seconds(
    num_bars=16,
    tempo=140,
    time_signature=(4, 4)
)
print(f"16 bars = {duration_16_bars:.2f}s")

# ============================================================================
# EXAMPLE 7: Audio Analysis
# ============================================================================

from audio_processing import AudioProcessor
import soundfile as sf

audio_proc = AudioProcessor()

# Get audio info without loading full file
audio_info = audio_proc.get_audio_info(Path("track.wav"))
print(f"Sample Rate: {audio_info.sample_rate}")
print(f"Duration: {audio_info.duration:.2f}s")
print(f"Channels: {audio_info.channels}")

# Load and detect BPM
audio_data, sr = audio_proc.load_audio(Path("track.wav"))
bpm = audio_proc.detect_bpm(audio_data, sr)
print(f"Detected BPM: {bpm:.1f}")

# Convert to mono
mono_audio = audio_proc.convert_to_mono(audio_data)

# Save processed audio
audio_proc.save_audio(
    audio_data=mono_audio,
    sample_rate=sr,
    output_path=Path("output_mono.wav"),
    bit_depth=24
)

# ============================================================================
# EXAMPLE 8: Custom Metadata Fields
# ============================================================================

metadata = metadata_gen.create_metadata(
    uid="GP_00001",
    original_title="Custom Track",
    bpm=140,
    key="Fmin",
    genre="trap",
    audio_count=8,
    midi_count=3,
    vocal_rights="exclusive",
    energy_level=4,
    mood=["dark", "epic"],
    sample_rate=48000,  # Custom sample rate
    bit_depth=24,
    time_signature="4/4",
    contains_ai=False,
    is_loop=True,  # Mark as loop
    engineer="Custom Engineer"
)

# Validate before export
errors = metadata_gen.validate_metadata(metadata)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")

# Save to JSON
metadata.to_json(Path("output/metadata.json"))

# ============================================================================
# EXAMPLE 9: Fuzzy Matching Configuration
# ============================================================================

# Adjust fuzzy matching threshold in config.py
import config

# Default is 70, lower for more lenient matching
config.FUZZY_MATCH_THRESHOLD = 60

# Test matching
from ingestion import FileIngester

ingester = FileIngester("source/folder")
ingester.scan_files()

# Manual matching test
audio_file = ingester.audio_files[0]
match_result = ingester.find_best_midi_match(audio_file)

if match_result:
    midi_file, score = match_result
    print(f"Best match: {midi_file.filename} (score: {score})")
else:
    print("No match found")

# ============================================================================
# EXAMPLE 10: Export Summary and Reporting
# ============================================================================

from export import FileExporter
from pathlib import Path

exporter = FileExporter("Clean_Dataset_Staging")

# Get summary of exported track
track_path = Path("Clean_Dataset_Staging/Batch_2025-12-08/GP_00001_Trap_140_Fmin")
summary = exporter.get_export_summary(track_path)

print("Export Summary:")
print(f"  Audio files: {summary['audio']}")
print(f"  MIDI files: {summary['midi']}")
print(f"  Metadata files: {summary['metadata']}")
print(f"  Master files: {summary['masters']}")

# ============================================================================
# COMMON WORKFLOWS
# ============================================================================

# Workflow 1: Quick test with default settings
python run_app.py "source_folder"

# Workflow 2: Production processing with full control
python run_app.py "source_folder" \
    --output "Clean_Dataset_Staging" \
    --title "Track Name" \
    --genre trap \
    --bpm 140 \
    --key Fmin \
    --vocal-rights Exclusive \
    --energy 5 \
    --mood aggressive dark \
    --start-bars 0 \
    --end-bars 16

# Workflow 3: Royalty-free vocal filtering
python run_app.py "source_folder" \
    --vocal-rights Royalty_Free  # Automatically skips vocal stems

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# Issue: MIDI pairing not working
# Solution: Check filename similarity, adjust FUZZY_MATCH_THRESHOLD

# Issue: Audio not slicing correctly
# Solution: Verify MIDI tempo map, check BPM detection

# Issue: Wrong mono/stereo conversion
# Solution: Review stem group/instrument classification

# Issue: Validation errors
# Solution: Check taxonomy values match config.py definitions
