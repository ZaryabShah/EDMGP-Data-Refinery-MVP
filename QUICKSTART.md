# 🚀 EDMGP Data Refinery - Quick Start Guide

## For Josh (Project Owner)

### Installation on M4 MacBook Pro

```bash
# 1. Navigate to project directory
cd /path/to/Music_upwork_Josh

# 2. Create virtual environment (recommended)
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies (ARM64 optimized)
pip install -r requirements.txt

# 5. Verify installation
python metadata.py
# Should output: "✓ Metadata is valid" + JSON
```

---

## Testing with Developer Kit Sample

### Option 1: Quick Test (Default Settings)
```bash
# Extract the sample first (if not already done)
# Then run with minimal arguments:

python run_app.py "EDMGP_developer_kit/EDMGP_developer_kit/Raw_input_sample" \
    --title "Fall Down" \
    --genre trap \
    --key Fmin
```

### Option 2: Full Test (All Parameters)
```bash
python run_app.py "EDMGP_developer_kit/EDMGP_developer_kit/Raw_input_sample" \
    --output "Clean_Dataset_Staging" \
    --title "Fall Down" \
    --genre trap \
    --bpm 140 \
    --key Fmin \
    --vocal-rights Royalty_Free \
    --energy 5 \
    --mood aggressive dark \
    --start-bars 0 \
    --end-bars 16
```

---

## Expected Output

```
Clean_Dataset_Staging/
  └── Batch_2025-12-08/
      └── GP_00001_Trap_140_Fmin/
          ├── Audio/
          │   ├── GP_00001_drums_kick_main.wav
          │   ├── GP_00001_bass_sub_main.wav
          │   └── ... (other processed stems)
          ├── MIDI/
          │   ├── GP_00001_midi_bass_sub.mid
          │   └── ... (other MIDI files)
          ├── Metadata/
          │   └── GP_00001_info.json
          └── Masters/
```

---

## What the App Does (Step by Step)

### 1. Ingestion & Auto-Pairing
```
✓ Found 12 audio file(s)
✓ Found 4 MIDI file(s)
✓ Created 12 file pair(s)
  - 4 with MIDI
  - 8 without MIDI
```

### 2. Vocal Filtering (if Royalty_Free mode)
```
⚠ Skipping vocal file (Royalty_Free mode): vocal_lead.wav
```

### 3. MIDI Tempo Extraction
```
✓ Using BPM from MIDI: 140.0
```

### 4. Bar-Aligned Slicing
```
Slicing from 0 to 16 bars (0.00s to 27.43s)
```

### 5. Processing Each Stem
```
Processing stem 1/12: kick_sample.wav
  ✓ Exported audio: GP_00001_drums_kick_main.wav
  ✓ Exported MIDI: GP_00001_midi_drums_kick.mid
```

### 6. Metadata Generation
```
  ✓ Exported metadata: GP_00001_info.json

✓ Track export complete:
  - 12 audio file(s)
  - 4 MIDI file(s)
  - 1 metadata file(s)
```

---

## CLI Arguments Reference

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `source_dir` | YES | Folder with audio/MIDI | `/path/to/stems` |
| `-o, --output` | no | Output directory | `Clean_Dataset_Staging` |
| `-t, --title` | no | Track name | `"Fall Down"` |
| `-g, --genre` | no | Genre (see list below) | `trap` |
| `-b, --bpm` | no | BPM (auto if omitted) | `140` |
| `-k, --key` | no | Musical key | `Fmin` |
| `-v, --vocal-rights` | no | `Exclusive` or `Royalty_Free` | `Exclusive` |
| `-e, --energy` | no | Energy level (1-5) | `5` |
| `-m, --mood` | no | Up to 2 mood tags | `aggressive dark` |
| `--start-bars` | no | Start position (bars) | `0` |
| `--end-bars` | no | End position (bars) | `16` |

### Supported Genres
Tech_House, Techno, Deep_House, Bass_House, Progressive_House, Big_Room, Trap, Dubstep, Future_Bass, Trance, Pop, Midtempo

### Supported Moods
Euphoric, Dark, Sad, Happy, Aggressive, Sexy, Chill, Quirky, Epic, Tense

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'librosa'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No audio files found"
**Solution:** Check that your source directory contains `.wav` files

### Issue: "MIDI pairing not working"
**Solution:** 
- Check filename similarity between audio and MIDI
- Lower the fuzzy match threshold in `config.py`:
  ```python
  FUZZY_MATCH_THRESHOLD = 60  # default is 70
  ```

### Issue: "BPM detection seems wrong"
**Solution:** Manually specify BPM with `--bpm` flag

### Issue: "Vocal stems not being filtered"
**Solution:** Ensure you're using `--vocal-rights Royalty_Free`

---

## Next Steps After Testing

### 1. Verify Output Quality
- Check `Clean_Dataset_Staging/Batch_XXXX/` folder
- Open audio files to verify slicing accuracy
- Review `metadata.json` for correctness

### 2. Process Your Own Data
```bash
python run_app.py "/path/to/your/stems" \
    --title "Your Track Name" \
    --genre trap \
    --bpm 140 \
    --key Fmin
```

### 3. Batch Processing
For multiple tracks, create a simple bash/PowerShell script:
```bash
#!/bin/bash
for dir in /path/to/tracks/*/ ; do
    python run_app.py "$dir" \
        --title "$(basename "$dir")" \
        --genre trap
done
```

### 4. Streamlit UI Development (Phase 2)
Once core logic is validated, add Streamlit frontend:
- Waveform visualizer with Matplotlib
- Interactive dropdowns for taxonomy
- Real-time pairing review table
- Batch processing queue

---

## File Structure Overview

```
Music_upwork_Josh/
├── config.py                 # Taxonomy & rules
├── ingestion.py              # File pairing
├── audio_processing.py       # Audio/MIDI processing
├── metadata.py               # Metadata generation
├── export.py                 # Export system
├── run_app.py                # CLI interface ⭐
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
├── USAGE_EXAMPLES.py         # Code examples
├── PROJECT_SUMMARY.md        # Project overview
└── QUICKSTART.md            # This file
```

---

## Key Features to Test

### ✅ Auto-Pairing
Look for the pairing report showing match scores:
```
1. bass_line.wav
   ↳ MIDI: bass.mid (Match: 85%)
```

### ✅ Vocal Filtering
With `Royalty_Free` mode, vocal files should be skipped:
```
⚠ Skipping vocal file (Royalty_Free mode): vocal_lead.wav
```

### ✅ MIDI Tempo Map
BPM should be extracted from MIDI:
```
✓ Using BPM from MIDI: 140.0
```

### ✅ Bar-Aligned Slicing
Time ranges should align to bar boundaries:
```
Slicing from 0 to 16 bars (0.00s to 27.43s)
```

### ✅ Mono/Stereo Conversion
Check output files:
- Kicks, subs should be mono (1 channel)
- Pads, FX should be stereo (2 channels)

### ✅ File Naming
All files should follow schema:
- `GP_00001_bass_sub_main.wav`
- `GP_00001_midi_bass_sub.mid`
- `GP_00001_info.json`

---

## Support & Questions

### Documentation Files
1. **README.md** - Comprehensive guide
2. **USAGE_EXAMPLES.py** - Code examples
3. **PROJECT_SUMMARY.md** - Technical overview
4. **This file (QUICKSTART.md)** - Getting started

### For Issues
1. Check troubleshooting section above
2. Review error messages for validation warnings
3. Test with smaller sample first
4. Verify file formats (.wav, .mid)

---

## Demo Video Checklist

When recording the 2-minute demo:

1. ✅ Show folder with raw audio/MIDI files
2. ✅ Run CLI command with parameters
3. ✅ Show ingestion and pairing report
4. ✅ Show processing progress
5. ✅ Navigate to output folder
6. ✅ Show generated directory structure
7. ✅ Open a few processed audio files
8. ✅ Open metadata.json to show schema
9. ✅ Compare input vs. output quality

---

## Success Criteria

Your MVP is successful if:
- ✅ Audio and MIDI files are correctly paired
- ✅ Slicing is bar-accurate (no audio clipping mid-note)
- ✅ File names follow exact schema
- ✅ Directory structure matches specification
- ✅ Metadata JSON validates against schema
- ✅ Mono/stereo rules are applied correctly
- ✅ Vocal filtering works in Royalty_Free mode

---

**You're ready to process your first track! 🎵**

```bash
python run_app.py "EDMGP_developer_kit/EDMGP_developer_kit/Raw_input_sample" \
    --title "Fall Down" --genre trap --key Fmin
```
