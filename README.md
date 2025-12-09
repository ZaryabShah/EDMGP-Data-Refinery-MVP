# 🎵 EDMGP Data Refinery

**Professional Audio/MIDI Dataset Processing for Machine Learning**

A complete data pipeline for processing EDM/trap audio stems and MIDI files into ML-ready datasets with automatic pairing, taxonomy-based labeling, bar-aligned slicing, and comprehensive metadata generation.

---

## 📋 Table of Contents

- [What It Does](#what-it-does)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Streamlit UI (Recommended)](#streamlit-ui-recommended)
  - [Command Line Interface](#command-line-interface)
- [Output Structure](#output-structure)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)

---

## 🎯 What It Does

This application solves the problem of processing thousands of unorganized audio/MIDI files into a clean, ML-ready dataset by:

1. **Auto-Pairing** - Automatically matches audio files with corresponding MIDI files using fuzzy matching
2. **Visual Workflow** - Interactive Streamlit UI with waveform visualization and beat grid overlay
3. **Taxonomy Labeling** - Organizes stems using a strict taxonomy (Group/Instrument/Layer)
4. **Bar-Aligned Slicing** - Crops audio and MIDI to exact bar boundaries using MIDI tempo as ground truth
5. **Smart Processing** - Automatically converts specific stems to mono, resamples to 44.1kHz
6. **Metadata Generation** - Creates comprehensive JSON metadata for ML training
7. **Vocal Rights Control** - Filters vocal stems based on licensing (Exclusive/Royalty_Free)

**Perfect for:** Music producers, ML engineers, and data scientists preparing audio datasets for generative AI training.

---

## ✨ Key Features

### 🎨 Interactive Streamlit UI
- **Waveform Visualizer** - See your audio with beat grid overlay
- **Beat Grid Overlay** - MIDI tempo-based bar markers for precise slicing
- **Auto-Pairing Display** - Visual table showing match scores
- **Interactive Labeling** - Dropdown menus for Group/Instrument/Layer
- **Manual Override** - Fix incorrect MIDI pairings with one click
- **Real-time Validation** - Instant feedback on mono/stereo requirements
- **Progress Tracking** - Visual indicators throughout the workflow

### 🔧 Backend Processing
- **Fuzzy File Matching** - 70% threshold for audio/MIDI pairing
- **MIDI Tempo Extraction** - Uses MIDI as ground truth for BPM
- **Bar-Aligned Slicing** - Precise note-level MIDI cropping
- **Auto-Resampling** - All audio normalized to 44.1kHz, 24-bit
- **Mono/Stereo Rules** - Force mono for kick, snare, sub, lead; keep stereo for FX, pads
- **Taxonomy Validation** - Ensures compliance with predefined schema

### 📊 Data Output
- **Programmatic Naming** - `UID_Group_Instrument_Layer.wav` (no manual typing)
- **Batch Organization** - Date-based batch folders with unique track IDs
- **Comprehensive Metadata** - JSON with BPM, key, genre, energy, mood, vocal rights
- **Separate Folders** - Audio/, MIDI/, Metadata/, Masters/ structure
- **ML-Ready Format** - 44.1kHz WAV, aligned MIDI, structured metadata

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Navigate to project folder
cd "C:\Users\zarya\Desktop\Python\Music_upwork_Josh"

# Install required packages
pip install -r requirements.txt
```

### 2. Launch Streamlit UI

```bash
# Start the interactive interface
python -m streamlit run streamlit_app.py
```

The app will open automatically at **http://localhost:8501**

### 3. Process Your First Track

1. **Configure** (Sidebar)
   - Set vocal rights (Exclusive/Royalty_Free)
   - Enter track metadata (title, genre, BPM, key)

2. **Ingest** (Tab 1)
   - Paste your source folder path
   - Click "Scan & Pair Files"
   - Review auto-pairing results

3. **Label** (Tab 2)
   - View waveform with beat grid
   - Select Group → Instrument → Layer
   - Click "Save Label" (auto-advances to next)

4. **Export** (Tab 3)
   - Review metadata preview
   - Click "Process & Export Dataset"
   - Find output in `Clean_Dataset_Staging/`

**Total Time:** ~5 minutes for 25 stems

---

## 💾 Installation

### Prerequisites

- **Python 3.9+** (tested on Python 3.12.10)
- **Operating System:** Windows 11, macOS (M4 compatible), Linux
- **RAM:** 4GB minimum (8GB recommended for large files)
- **Disk Space:** 2GB per 1000 processed files

### Standard Installation

```bash
# Clone or download the project
cd path/to/EDMGP-Data-Refinery

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9 or higher

# Test import
python -c "import streamlit, librosa, pretty_midi; print('✅ All dependencies installed')"
```

### macOS M4 (Apple Silicon) Notes

All dependencies are ARM64-compatible. If you encounter issues:

```bash
# Use Homebrew Python (recommended for M-series Macs)
brew install python@3.12

# Install dependencies
/opt/homebrew/bin/python3.12 -m pip install -r requirements.txt
```

---

## 📖 Usage

### Streamlit UI (Recommended)

The Streamlit interface provides a visual, step-by-step workflow perfect for first-time use and quality control.

```bash
# Launch the UI
python -m streamlit run streamlit_app.py
```

**Complete workflow guide:** See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for detailed UI documentation.

**Key Advantages:**
- ✅ Visual waveform display with beat grid
- ✅ Interactive dropdown menus (no coding)
- ✅ Real-time validation and warnings
- ✅ Manual MIDI pairing override
- ✅ Progress tracking and feedback

### Command Line Interface

For automation and batch processing, use the CLI tool:

```bash
python run_app.py "path/to/source/folder" \
  --title "My Track" \
  --genre trap \
  --bpm 145 \
  --key "F minor" \
  --vocal-rights royalty_free \
  --output Clean_Dataset_Staging
```

**Example with demo script:**

```python
# See USAGE_EXAMPLES.py for complete examples
from pathlib import Path
from ingestion import FileIngester
from export import ExportSession
from metadata import MetadataGenerator

# Load and pair files
ingester = FileIngester(Path("Raw_input_sample/Fall Down"))
ingester.scan_files()
ingester.auto_pair_files()

# Process stems (see USAGE_EXAMPLES.py for complete code)
# ...
```

**CLI Advantages:**
- ✅ Faster for bulk processing
- ✅ Scriptable and automatable
- ✅ No browser required
- ✅ Better for remote servers

---

## 📁 Output Structure

After processing, your dataset will be organized as:

```
Clean_Dataset_Staging/
└── Batch_2025-12-10/
    └── GP_00001_trap_145_Fmin/
        ├── Audio/
        │   ├── GP_00001_bass_sub_main.wav
        │   ├── GP_00001_drums_kick_main.wav
        │   ├── GP_00001_synth_lead_layer1.wav
        │   └── ... (all stems, 44.1kHz, 24-bit WAV)
        │
        ├── MIDI/
        │   ├── GP_00001_midi_bass_sub.mid
        │   ├── GP_00001_midi_synth_lead.mid
        │   └── ... (aligned MIDI files)
        │
        ├── Metadata/
        │   └── GP_00001_info.json
        │       {
        │         "uid": "GP_00001",
        │         "original_track_title": "Fall Down",
        │         "bpm": 145,
        │         "genre": "trap",
        │         "key": "F minor",
        │         "vocal_rights": "royalty_free",
        │         "energy_level": 5,
        │         "mood": ["aggressive", "dark"],
        │         "audio_file_count": 23,
        │         "midi_file_count": 4,
        │         "created_at": "2025-12-10T15:30:00"
        │       }
        │
        └── Masters/
            └── (reserved for future use)
```

### File Naming Schema

**Audio:** `{UID}_{Group}_{Instrument}_{Layer}.wav`
- Example: `GP_00001_bass_sub_main.wav`

**MIDI:** `{UID}_midi_{Instrument}.mid`
- Example: `GP_00001_midi_bass_sub.mid`

**Metadata:** `{UID}_info.json`
- Example: `GP_00001_info.json`

### Taxonomy Reference

**Groups:** Drums, Bass, Synth, Vocal, FX, Instruments, Mix

**Sample Instruments:**
- **Drums:** Kick, Snare, Clap, Hat_Closed, Hat_Open, Cymbal, Perc, Tom
- **Bass:** Sub, Mid_Bass, Reese, Pluck, Wobble
- **Synth:** Lead, Chord, Pad, Arp, Pluck, Stab, Texture
- **Vocal:** Main, Harmony, Ad_Lib, Chop, Vocal_FX
- **FX:** Riser, Downsweep, Impact, Noise, Ambience, Transition

**Layers:** Main, Layer1, Layer2, Layer3, Top, Bottom, Dry, Wet, One_Shot, Loop, Roll

---

## 🔧 Requirements

### Python Packages

All dependencies are listed in `requirements.txt`:

```
# Core
streamlit>=1.28.0
numpy>=1.24.0,<2.0.0
pandas>=2.0.0

# Audio Processing
librosa>=0.10.1
soundfile>=0.12.1
matplotlib>=3.7.0

# MIDI Processing
pretty-midi>=0.2.10
mido>=1.3.0

# Utilities
rapidfuzz>=3.0.0
python-dateutil>=2.8.2
```

### System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Python: 3.9+
- Disk: 2 GB free space

**Recommended:**
- CPU: Quad-core 3.0 GHz (or Apple M-series)
- RAM: 8 GB
- Python: 3.12+
- Disk: 10 GB free space

---

## ⚠️ Troubleshooting

### "No module named 'streamlit'"

```bash
# Install missing dependencies
pip install -r requirements.txt
```

### "No module named 'matplotlib'"

```bash
# Install visualization libraries
pip install matplotlib librosa
```

### "streamlit: command not found" (Windows)

```bash
# Use Python module syntax instead
python -m streamlit run streamlit_app.py
```

### "No files found" in UI

- ✅ Check that directory path is correct
- ✅ Ensure folder contains .wav and/or .mid files
- ✅ Verify you have read permissions

### Waveform won't display

- ✅ Check if audio file is corrupted (try opening in DAW)
- ✅ Ensure file is standard WAV format
- ✅ For large files (>1GB), try smaller clips first

### Export fails or incomplete

- ✅ Ensure all stems are labeled (check sidebar status)
- ✅ Verify track title is entered (required field)
- ✅ Check BPM is in valid range (40-300)
- ✅ Ensure sufficient disk space

### MIDI pairing incorrect

- ✅ Use "Manual Pairing Override" in Tab 2 (Label Stems)
- ✅ Check filename similarity (auto-pairing uses 70% threshold)
- ✅ Some stems may genuinely have no MIDI

### Performance issues with large datasets

**For UI:**
- Process tracks one at a time
- Close other applications to free RAM

**For bulk processing:**
- Use CLI tool instead (`run_app.py`)
- Process in batches of 50-100 tracks

---

## 📚 Documentation

- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)** - Complete UI walkthrough with screenshots
- **[USAGE_EXAMPLES.py](USAGE_EXAMPLES.py)** - Code examples and CLI usage
- **[requirements.txt](requirements.txt)** - All Python dependencies

---

## 🎯 Use Cases

### For Music Producers
- Organize stems from production sessions
- Prepare sample packs for commercial release
- Create ML training datasets from your catalog

### For ML Engineers
- Prepare audio datasets for generative AI training
- Ensure data quality with visual validation
- Generate comprehensive metadata for model training

### For Data Scientists
- Process large-scale audio collections
- Create balanced datasets with taxonomy control
- Validate data integrity before training

---

## 📊 Project Stats

- **Backend Code:** ~2,500 lines
- **UI Code:** ~600 lines
- **Automated Tests:** 27 tests (100% passing)
- **Documentation:** Comprehensive guides
- **Processing Speed:** ~18 seconds for 27 stems (CLI)
- **Batch Capacity:** Tested up to 30,000+ tracks

---

## 🔄 Workflow Comparison

| Feature | Streamlit UI | CLI Tool |
|---------|--------------|----------|
| **Visual Interface** | ✅ Interactive | ❌ Terminal only |
| **Waveform Display** | ✅ With beat grid | ❌ No visual |
| **Learning Curve** | ⭐⭐ Easy | ⭐⭐⭐⭐ Advanced |
| **Speed** | ⭐⭐⭐ Interactive | ⭐⭐⭐⭐⭐ Fast |
| **Best For** | First-time use, QC | Bulk processing, automation |

**Recommendation:** Start with Streamlit UI to learn the workflow, then use CLI for large-scale batch processing.

---

## 💡 Tips & Best Practices

### Before Processing

1. ✅ Organize source files in one folder per track
2. ✅ Name files descriptively (helps auto-pairing)
3. ✅ Use standard formats (.wav for audio, .mid for MIDI)
4. ✅ Verify vocal rights before starting

### During Labeling

1. ✅ Review beat grid alignment in waveform viewer
2. ✅ Check MIDI requirement warnings
3. ✅ Use specific layer names (main, layer2, not generic)
4. ✅ Validate mono/stereo requirements

### After Export

1. ✅ Spot-check a few output files in your DAW
2. ✅ Verify audio/MIDI alignment
3. ✅ Review metadata JSON for accuracy
4. ✅ Back up your processed dataset

---

## 🚀 Next Steps

1. **Process Sample Data**
   - Use included `Raw_input_sample/Fall Down/` as test data
   - Compare output with `Target_output_sample/`

2. **Process Your Dataset**
   - Start with UI for 10-20 tracks
   - Validate output quality in DAW
   - Scale up to full catalog

3. **Automate Workflow**
   - Write scripts using `USAGE_EXAMPLES.py` as template
   - Use CLI for batch processing
   - Set up monitoring/logging

4. **ML Training**
   - Feed dataset to your ML pipeline
   - Use metadata.json for filtering/balancing
   - Leverage taxonomy for conditional generation

---

## 📄 License & Credits

**Developed by:** Syed Wajeh (via Upwork)  
**Client:** Josh (EDMGP)  
**Version:** 2.0 (Full Stack - UI + Backend)  
**Date:** December 2025  
**Status:** ✅ Production Ready

---

## 📞 Support

For issues, questions, or feature requests:

1. Check [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for UI help
2. Review [Troubleshooting](#troubleshooting) section above
3. Examine [USAGE_EXAMPLES.py](USAGE_EXAMPLES.py) for code patterns
4. Contact developer via Upwork

---

**Ready to process your dataset?** Start with `python -m streamlit run streamlit_app.py` 🎵
