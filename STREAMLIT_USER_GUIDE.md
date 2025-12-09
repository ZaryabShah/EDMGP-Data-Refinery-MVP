# 🎵 STREAMLIT UI USER GUIDE

**EDMGP Data Refinery - Interactive Audio/MIDI Dataset Processing**

Version: 2.0 (Streamlit UI Complete)  
Date: December 10, 2025

---

## 🚀 QUICK START

### Launch the Application

```bash
# Navigate to project folder
cd "C:\Users\zarya\Desktop\Python\Music_upwork_Josh"

# Launch Streamlit app
python3.12.exe -m streamlit run streamlit_app.py
```

**The app will open automatically in your browser at:** `http://localhost:8501`

---

## 📖 USER INTERFACE OVERVIEW

The application has **3 main tabs** corresponding to the workflow:

1. **📂 Ingest & Pair** - Load files and auto-pair audio with MIDI
2. **🎨 Label Stems** - Visualize waveforms and label each stem
3. **📦 Export** - Process and export the final dataset

### Sidebar Configuration

The sidebar contains global settings that apply to the entire track:

- **Vocal Rights Gate** - Exclusive or Royalty_Free
- **Track Metadata** - Title, Genre, BPM, Key, Energy, Mood
- **Status** - Current progress (stems labeled vs total)

---

## 🎯 STEP-BY-STEP WORKFLOW

### STEP 1: Ingest & Pair 📂

**Purpose:** Load audio/MIDI files and automatically pair them.

#### Actions:

1. **Set Vocal Rights** (Sidebar)
   - Toggle: "Contains Exclusive Vocals?"
   - **Exclusive** - All vocal stems will be included
   - **Royalty_Free** - Vocal stems will be automatically excluded

2. **Enter Source Directory**
   ```
   Example: C:\Users\Josh\Desktop\Raw_Audio\Fall_Down
   ```
   - Paste the full path to your source folder
   - Folder should contain .wav and .mid files

3. **Click "🔍 Scan & Pair Files"**
   - App scans for audio and MIDI files
   - Fuzzy matching pairs them automatically
   - Results displayed in table with match scores

#### What You'll See:

**Pairing Results Table:**
| # | Audio File | MIDI File | Match Score | Labeled |
|---|------------|-----------|-------------|---------|
| 1 | kick.wav | kick.mid | 100% | ⏳ |
| 2 | bass_sub.wav | bass_sub.mid | 100% | ⏳ |
| 3 | fx_riser.wav | ❌ No MIDI | N/A | ⏳ |

**Summary Metrics:**
- **Total Files** - Number of audio files found
- **With MIDI** - Files successfully paired
- **Without MIDI** - Files without MIDI pairing

---

### STEP 2: Label Stems 🎨

**Purpose:** Visualize each stem and assign Group/Instrument/Layer labels.

#### Interface Elements:

**1. Navigation**
- **⬅️ Previous** / **Next ➡️** buttons
- Shows: "Stem X of Y"

**2. Current File Info**
- Audio filename
- MIDI filename (if paired) with match score
- Warning if no MIDI (for melodic content)

**3. Waveform Visualizer**
- Interactive waveform display
- Beat grid overlay (derived from MIDI or BPM)
- Red dashed lines mark bar boundaries
- Green highlight shows selected range

**4. Slice Settings** (Right Panel)
- **Start Bar** - Where to begin slicing (default: 0)
- **End Bar** - Where to end slicing (default: 16)
- **Duration Info** - Shows calculated duration in seconds

**5. Labeling Dropdowns**

**Group Dropdown:**
- Drums, Bass, Synth, Vocal, FX, Instruments, Mix
- Determines which instruments are available

**Instrument Dropdown:**
- Changes based on Group selection
- Examples:
  - Drums → Kick, Snare, Clap, Hat_Closed, etc.
  - Bass → Sub, Mid_Bass, Reese, Pluck, etc.
  - Synth → Lead, Chord, Pad, Arp, etc.

**Layer Dropdown:**
- Main, Layer1, Layer2, Layer3, etc.
- Top, Texture, Dry, Wet, One_Shot, Loop, Roll

**6. Validation & Helpers**

**Left Box - Mono/Stereo:**
```
ℹ️ This stem will be converted to MONO
(Group: Drums, Instrument: Kick)
```
or
```
ℹ️ This stem will remain STEREO
```

**Right Box - MIDI Requirement:**
```
⚠️ Bass stems typically require MIDI pairing!
```

**7. Manual Pairing Override** 🔧

- Checkbox: "Manual Pairing Override"
- Allows you to:
  - Change which MIDI file is paired
  - Remove MIDI pairing entirely
  - Useful for fixing auto-pairing errors

#### Workflow:

1. **Review waveform** - Check beat grid alignment
2. **Adjust slice settings** - Set start/end bars if needed
3. **Select Group** - Choose from dropdown
4. **Select Instrument** - Auto-filtered based on Group
5. **Select Layer** - Choose variant (main, layer2, etc.)
6. **Review validation** - Check mono/stereo and MIDI warnings
7. **Click "💾 Save Label"**
8. **Auto-advance** - Jumps to next unlabeled stem

**Tips:**
- Labels are case-insensitive (you can type lowercase, they'll be normalized)
- Green checkmark ✅ appears next to labeled stems
- All stems must be labeled before export

---

### STEP 3: Export 📦

**Purpose:** Process all stems and generate the final dataset.

#### Configuration:

**Output Directory:**
```
Default: Clean_Dataset_Staging
Custom: My_Dataset_Output
```

**Track Metadata** (from Sidebar):
- ✅ Title - Required
- ✅ Genre - From taxonomy
- ✅ BPM - Used for slicing
- ✅ Key - Musical key
- Energy Level - 1-5 scale
- Mood - Up to 2 tags

#### Pre-Export Checks:

1. **All stems labeled?**
   ```
   ⚠️ Only 15 of 23 stems are labeled. Please label all stems before exporting.
   ```

2. **Track title entered?**
   ```
   ❌ Please enter a track title in the sidebar
   ```

#### Export Summary:

**Metrics Display:**
- **Total Stems** - Number to process
- **With MIDI** - MIDI files to export
- **Output Format** - 44.1kHz / 24-bit WAV

**Metadata Preview:**
```json
{
  "uid": "GP_XXXXX (auto-generated)",
  "original_track_title": "Fall Down",
  "bpm": 145,
  "genre": "trap",
  "vocal_rights": "royalty_free",
  "energy_level": 5,
  "mood": ["aggressive", "dark"]
}
```

#### Processing:

Click **"🚀 Process & Export Dataset"**

**Progress Bar Shows:**
```
Creating batch directory...           [5%]
Creating track directory...           [10%]
Processing stem 1/27: kick.wav        [15%]
Processing stem 2/27: bass_sub.wav    [20%]
...
Generating metadata...                [95%]
Export complete!                      [100%]
```

#### Success:

```
✅ Export Successful!

- UID: GP_00001
- Audio Files: 23
- MIDI Files: 4
- Location: C:\...\Clean_Dataset_Staging\Batch_2025-12-10\GP_00001_trap_145_Fmin
```

---

## 📁 OUTPUT STRUCTURE

```
Clean_Dataset_Staging/
  └── Batch_2025-12-10/
      └── GP_00001_trap_145_Fmin/
          ├── Audio/
          │   ├── GP_00001_bass_sub_main.wav
          │   ├── GP_00001_drums_kick_main.wav
          │   ├── GP_00001_synth_lead_layer1.wav
          │   └── ... (all audio stems)
          ├── MIDI/
          │   ├── GP_00001_midi_bass_sub.mid
          │   ├── GP_00001_midi_synth_lead.mid
          │   └── ... (MIDI for melodic stems)
          ├── Metadata/
          │   └── GP_00001_info.json
          └── Masters/
              └── (reserved for future use)
```

---

## 🎨 UI FEATURES

### Auto-Features

✅ **Auto-Pairing** - Fuzzy matching with 70% threshold  
✅ **Auto-Advancement** - Jumps to next unlabeled stem after saving  
✅ **Auto-Validation** - Real-time mono/stereo and MIDI requirement checks  
✅ **Auto-Normalization** - Labels normalized to taxonomy format  
✅ **Auto-Resampling** - All audio converted to 44.1kHz  

### Interactive Features

🎛️ **Waveform Visualizer** - See your audio with beat grid overlay  
🎛️ **Beat Grid** - Derived from MIDI tempo or audio BPM detection  
🎛️ **Slice Preview** - Visual indication of selected range  
🎛️ **Manual Override** - Change MIDI pairings when needed  
🎛️ **Progress Tracking** - See labeled vs total stems  

### Validation Features

✅ **Required Fields** - Title, Genre validated before export  
✅ **Mood Limit** - Max 2 mood tags enforced  
✅ **Bar Range** - End bar must be > Start bar  
✅ **BPM Range** - 40-300 BPM validated  
✅ **Taxonomy Compliance** - All labels checked against config  

---

## 🔧 ADVANCED USAGE

### Custom Slice Settings

**Same slice for all stems:**
1. Set Start/End bars in Step 2
2. Settings persist across all stems

**Different slices per stem:**
1. Not currently supported in UI
2. Use CLI tool (`run_app.py`) for per-stem control

### Manual Pairing Override

**When to use:**
- Auto-pairing made a mistake
- You want to pair different MIDI files
- Remove MIDI from non-melodic content

**How to use:**
1. Go to the stem in Step 2
2. Check "🔧 Manual Pairing Override"
3. Select different MIDI file or "❌ No MIDI"
4. Click "Apply Override"
5. Override persists until export

### Batch Processing Multiple Tracks

**Option 1: Process one at a time**
1. Complete workflow for Track 1
2. Refresh page (F5) to reset
3. Start new track

**Option 2: Use CLI for automation**
```bash
# Process multiple tracks with demo_with_labels.py pattern
for track in tracks:
    python run_app.py "$track" --title "..." --genre ...
```

---

## ⚠️ TROUBLESHOOTING

### "No files found"
- **Check path** - Ensure directory exists and has .wav/.mid files
- **Check permissions** - Ensure you can read the directory
- **Supported formats** - Only .wav, .wave, .mid, .midi

### "Waveform won't display"
- **File corrupt?** - Try opening in DAW first
- **Unsupported format?** - Convert to standard WAV
- **File too large?** - Librosa may have memory issues (>1GB files)

### "MIDI pairing incorrect"
- **Use manual override** - Check the override box and select correct MIDI
- **Filename similarity** - Auto-pairing uses fuzzy matching (70% threshold)
- **Missing MIDI?** - Some files may genuinely have no MIDI

### "Export fails"
- **All stems labeled?** - Check sidebar status
- **Title entered?** - Required field in sidebar
- **Valid BPM/Genre?** - Must be in valid ranges
- **Disk space?** - Ensure enough space for output

### "Slice settings not saving"
- **Per-stem settings** - Currently not supported (same slice for all)
- **Session state** - Settings stored in session, reset on page refresh

---

## 🎯 BEST PRACTICES

### Before Starting

1. ✅ Organize source files in one folder
2. ✅ Name files descriptively (helps auto-pairing)
3. ✅ Check file formats (.wav for audio, .mid for MIDI)
4. ✅ Verify vocal rights before processing

### During Labeling

1. ✅ Review beat grid alignment
2. ✅ Check MIDI requirement warnings
3. ✅ Use descriptive layers (main, layer2, not generic names)
4. ✅ Validate mono/stereo requirements
5. ✅ Save labels frequently (auto-advances)

### Before Export

1. ✅ Verify all stems labeled (check sidebar)
2. ✅ Review metadata preview
3. ✅ Confirm slice settings
4. ✅ Check output directory path

### After Export

1. ✅ Listen to a few output files in DAW
2. ✅ Check alignment (audio + MIDI match)
3. ✅ Verify file naming schema
4. ✅ Review metadata JSON

---

## 🆚 UI vs CLI COMPARISON

| Feature | Streamlit UI | CLI Tool |
|---------|--------------|----------|
| **Waveform Visualization** | ✅ Interactive | ❌ No visual |
| **Beat Grid Overlay** | ✅ Yes | ❌ No |
| **Stem Labeling** | ✅ Dropdowns | ⚠️ Manual dict |
| **Manual Pairing** | ✅ Override UI | ⚠️ Edit code |
| **Progress Tracking** | ✅ Visual | ⚠️ Console only |
| **Validation Warnings** | ✅ Real-time | ⚠️ After processing |
| **Batch Processing** | ⚠️ One at a time | ✅ Script loops |
| **Speed** | ⚠️ Interactive | ✅ Faster |

**Recommendation:**
- **Use UI** - For first-time processing, learning, quality control
- **Use CLI** - For bulk processing, automation, scripting

---

## 🎬 DEMO WALKTHROUGH

### Sample Session (5 Minutes)

**1. Launch App (30 seconds)**
```bash
python3.12.exe -m streamlit run streamlit_app.py
```
Opens at http://localhost:8501

**2. Configure (1 minute)**
- Sidebar: Set "Royalty_Free" if needed
- Sidebar: Enter track title, genre, BPM, key
- Sidebar: Set energy level, mood tags

**3. Ingest (30 seconds)**
- Tab 1: Paste source directory path
- Click "Scan & Pair Files"
- Review pairing table

**4. Label Stems (2-3 minutes)**
- Tab 2: Review waveform
- Select Group → Instrument → Layer
- Click "Save Label"
- Repeat for all stems (auto-advances)

**5. Export (1 minute)**
- Tab 3: Review summary
- Click "Process & Export Dataset"
- Wait for progress bar
- Success message shows output location

**Total Time:** ~5 minutes for 20-30 stems

---

## 📞 SUPPORT

### Common Questions

**Q: Can I change labels after saving?**  
A: Yes, navigate back to the stem and save new labels. They'll overwrite.

**Q: Can I pause and resume later?**  
A: No, session state is lost on page refresh. Complete the track in one session.

**Q: What if auto-pairing fails?**  
A: Use the manual pairing override to fix incorrect pairings.

**Q: Can I process multiple tracks at once?**  
A: No, process one track at a time. Refresh page between tracks.

**Q: Where is my output?**  
A: Default location: `Clean_Dataset_Staging/Batch_DATE/GP_XXXXX_genre_bpm_key/`

---

## 🚀 NEXT STEPS

After mastering the UI:

1. **Process your full dataset** - Use UI for quality control
2. **Automate with CLI** - Use `run_app.py` for bulk processing
3. **Validate output** - Spot-check files in DAW
4. **Train your model** - Feed dataset to ML pipeline

---

**Created:** December 10, 2025  
**Version:** 2.0 (Streamlit UI Complete)  
**Status:** ✅ Production Ready
