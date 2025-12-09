# 🎨 Streamlit UI Guide

**Complete Interactive Workflow for EDMGP Data Refinery**

This guide covers everything you need to know about using the Streamlit web interface for processing audio/MIDI datasets.

---

## 📖 Table of Contents

- [Quick Start](#quick-start)
- [Interface Overview](#interface-overview)
- [Step-by-Step Workflow](#step-by-step-workflow)
  - [Step 1: Ingest & Pair](#step-1-ingest--pair)
  - [Step 2: Label Stems](#step-2-label-stems)
  - [Step 3: Export](#step-3-export)
- [UI Features](#ui-features)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Tips & Best Practices](#tips--best-practices)

---

## 🚀 Quick Start

### Launch the Application

```bash
# Navigate to project directory
cd "C:\Users\zarya\Desktop\Python\Music_upwork_Josh"

# Start Streamlit
python -m streamlit run streamlit_app.py
```

The app automatically opens in your browser at: **http://localhost:8501**

### First-Time Setup

No configuration needed! The app is ready to use immediately.

**Optional:** If browser doesn't auto-open, manually navigate to `http://localhost:8501`

---

## 🖥️ Interface Overview

The Streamlit UI has **two main areas**:

### 1. Sidebar (Left Panel)

Global settings that apply to the entire track:

- **Vocal Rights Gate**
  - Toggle: "Contains Exclusive Vocals?"
  - **Exclusive** = Include all vocal stems
  - **Royalty_Free** = Auto-filter vocal stems

- **Track Metadata**
  - Title (required)
  - Genre (dropdown)
  - BPM (number input)
  - Key (dropdown)
  - Energy Level (1-5 slider)
  - Mood (multi-select, max 2 tags)

- **Status Indicators**
  - Total stems found
  - Stems labeled
  - Progress percentage

### 2. Main Area (Right Panel)

Three tabs for the processing workflow:

1. **📂 Ingest & Pair** - Load files and auto-pair
2. **🎨 Label Stems** - Visualize and label each stem
3. **📦 Export** - Process and export dataset

---

## 🎯 Step-by-Step Workflow

### Step 1: Ingest & Pair 📂

**Purpose:** Load your audio/MIDI files and automatically pair them.

#### 1.1 Set Vocal Rights (Sidebar)

Toggle the **"Contains Exclusive Vocals?"** radio button:

- **Exclusive** - All stems included (default for commercial releases)
- **Royalty_Free** - Vocal stems automatically filtered (for sample packs/public datasets)

💡 **Why this matters:** ML training on exclusive vocals may violate licensing. This gate ensures compliance.

#### 1.2 Enter Source Directory

In the main area, find the **"Source Directory"** text input:

```
Example paths:
Windows: C:\Users\Josh\Desktop\Raw_Audio\Fall_Down
macOS:   /Users/Josh/Desktop/Raw_Audio/Fall_Down
```

Paste or type the full path to your folder containing:
- Audio files (.wav, .wave)
- MIDI files (.mid, .midi)

#### 1.3 Scan & Pair Files

Click the **"🔍 Scan & Pair Files"** button.

The app will:
1. Scan directory for audio/MIDI files
2. Use fuzzy matching to pair them (70% similarity threshold)
3. Display results in a table

#### 1.4 Review Pairing Results

**Pairing Table Columns:**

| Column | Description |
|--------|-------------|
| **#** | Stem number |
| **Audio File** | Audio filename |
| **MIDI File** | Paired MIDI filename or "❌ No MIDI" |
| **Match Score** | Pairing confidence (0-100%) |
| **Labeled** | Status: ⏳ Pending, ✅ Complete |

**Summary Metrics:**

- **Total Files** - Audio files found
- **With MIDI** - Successfully paired
- **Without MIDI** - No MIDI match (OK for drums/FX)

**Example Output:**

```
✅ Found 28 audio files and 7 MIDI files

| #  | Audio File        | MIDI File         | Match Score | Labeled |
|----|-------------------|-------------------|-------------|---------|
| 1  | kick_main.wav     | kick.mid          | 100%        | ⏳      |
| 2  | bass_sub_v2.wav   | bass_sub.mid      | 95%         | ⏳      |
| 3  | fx_riser.wav      | ❌ No MIDI         | N/A         | ⏳      |
```

**Next:** Click the **"Label Stems"** tab to continue.

---

### Step 2: Label Stems 🎨

**Purpose:** Visualize each stem's waveform and assign taxonomy labels.

This is the core of the workflow. You'll review each stem individually and assign:
- **Group** (e.g., Drums, Bass, Synth)
- **Instrument** (e.g., Kick, Sub, Lead)
- **Layer** (e.g., Main, Layer1, Layer2)

#### 2.1 Navigation

**Stem Counter:** Shows current position (e.g., "Stem 1 of 28")

**Navigation Buttons:**
- **⬅️ Previous** - Go to previous stem
- **Next ➡️** - Go to next stem

💡 **Auto-Advancement:** After saving a label, the app automatically jumps to the next unlabeled stem.

#### 2.2 Current File Information

**Display Box:** Shows current stem details:

```
📁 Current Stem: kick_main.wav
🎵 MIDI File: kick.mid (100% match)
```

Or, if no MIDI:

```
📁 Current Stem: fx_riser.wav
⚠️ No MIDI file paired
```

#### 2.3 Waveform Visualizer

**Interactive Audio Visualization:**

- **Waveform** - Blue amplitude display
- **Beat Grid** - Red dashed vertical lines at bar boundaries
- **Selected Range** - Green highlight overlay
- **X-Axis** - Time in seconds
- **Y-Axis** - Amplitude

**How Beat Grid Works:**

1. If MIDI paired → Uses MIDI tempo (most accurate)
2. If no MIDI → Auto-detects BPM from audio
3. Calculates bar positions: `bar_time = (bar_number × 4 beats × 60) / BPM`
4. Overlays red lines at each bar start

**Example:**
```
BPM: 145
Bar duration: (4 × 60) / 145 = 1.655 seconds
Bar 0: 0.000s, Bar 1: 1.655s, Bar 2: 3.310s...
```

#### 2.4 Slice Settings

**Right Panel - Slice Configuration:**

- **Start Bar** - Beginning bar number (default: 0)
- **End Bar** - Ending bar number (default: 16)
- **Duration** - Auto-calculated in seconds

**Example:**
```
Start Bar: 0
End Bar: 16
Duration: 26.5 seconds (based on 145 BPM)
```

💡 **Note:** Slice settings apply to all stems in the current export session.

#### 2.5 Taxonomy Labeling

**Three Dropdown Menus (Left to Right):**

##### Group Dropdown

Select the primary category:

- **Drums** - Percussive elements
- **Bass** - Low-frequency melodic content
- **Synth** - Synthesized melodic content
- **Vocal** - Voice content
- **FX** - Sound effects and transitions
- **Instruments** - Acoustic/real instruments
- **Mix** - Full mix or submixes

##### Instrument Dropdown

**Auto-filtered based on Group selection.**

Examples:

**If Group = Drums:**
- Kick, Snare, Clap, Hat_Closed, Hat_Open, Cymbal, Tom, Perc

**If Group = Bass:**
- Sub, Mid_Bass, Reese, Pluck, Wobble, FM, Growl

**If Group = Synth:**
- Lead, Chord, Pad, Arp, Pluck, Stab, Bell, Texture

**If Group = Vocal:**
- Main, Harmony, Ad_Lib, Chop, Vocal_FX

**If Group = FX:**
- Riser, Downsweep, Impact, Noise, Ambience, Transition

##### Layer Dropdown

Select the variant:

- **Main** - Primary version
- **Layer1, Layer2, Layer3** - Additional layers
- **Top, Bottom** - Frequency variations
- **Dry, Wet** - Effect variations
- **One_Shot, Loop, Roll** - Playback types

**Example Selection:**
```
Group: Bass
Instrument: Sub
Layer: Main

Result: bass_sub_main
```

#### 2.6 Validation Helpers

**Two Info Boxes Below Dropdowns:**

##### Left Box - Mono/Stereo Processing

Shows how the stem will be processed:

```
ℹ️ This stem will be converted to MONO
(Group: Drums, Instrument: Kick)

Forced mono stems:
• Kick, Snare, Sub, Lead, Clap, Hat_Closed, Tom
```

Or:

```
ℹ️ This stem will remain STEREO

Stereo-preserved stems:
• FX, Pad, Ambience, Cymbal, Noise, Hat_Open
```

💡 **Why?** Mono ensures phase coherence for bass/kick. Stereo preserves width for pads/FX.

##### Right Box - MIDI Requirement

Shows if MIDI is expected:

```
ℹ️ Bass stems typically have MIDI pairing
```

Or:

```
⚠️ No MIDI paired, but Bass typically requires MIDI!
```

**MIDI Required Groups:**
- Bass (melodic content needs pitch info)
- Synth (melody/harmony)
- Vocal (pitch tracking)

**MIDI Optional Groups:**
- Drums (rhythmic, no pitch)
- FX (sound design)

#### 2.7 Manual Pairing Override

**When to Use:**

- Auto-pairing made a mistake
- Want to pair different MIDI file
- Remove MIDI from incorrectly paired stem

**How to Use:**

1. Check the **"🔧 Manual Pairing Override"** checkbox
2. New controls appear:
   - Dropdown with all available MIDI files
   - Option: "❌ No MIDI" to remove pairing
3. Select the correct MIDI file
4. Click **"Apply Override"**
5. Confirmation message appears
6. Override persists for this stem until export

**Example:**
```
Original: bass_sub.wav → bass_lead.mid (90% match - WRONG)
Override: bass_sub.wav → bass_sub.mid (manually selected)
```

#### 2.8 Save Label

After selecting Group/Instrument/Layer:

1. Click **"💾 Save Label"** button
2. Success message appears: `✅ Label saved for kick_main.wav`
3. App auto-advances to next unlabeled stem
4. Sidebar updates progress counter

**Progress Tracking:**

Sidebar shows:
```
Stems Labeled: 5 / 28 (18%)
```

Table in Step 1 updates:
```
| 1  | kick_main.wav  | kick.mid | 100% | ✅ |  ← Now complete
```

💡 **You can navigate back and change labels anytime before export.**

---

### Step 3: Export 📦

**Purpose:** Process all labeled stems and generate the final dataset.

#### 3.1 Pre-Export Validation

Before showing export controls, the app checks:

**Required Checks:**

1. ✅ **All stems labeled?**
   ```
   ⚠️ Only 15 of 28 stems are labeled.
   Please label all stems before exporting.
   ```

2. ✅ **Track title entered?**
   ```
   ❌ Please enter a track title in the sidebar
   ```

3. ✅ **Valid BPM/Genre?**
   - BPM must be 40-300
   - Genre must be selected

**Fix these before proceeding to export.**

#### 3.2 Output Directory

**Text Input:** Specify where to save processed files

```
Default: Clean_Dataset_Staging
Custom:  My_Dataset_Output
```

💡 Files are organized as:
```
{output_dir}/
  └── Batch_{date}/
      └── GP_{uid}_{genre}_{bpm}_{key}/
```

#### 3.3 Export Summary

**Three Metric Boxes:**

```
📊 Total Stems: 28
🎵 With MIDI: 7
📁 Output Format: 44.1kHz / 24-bit WAV
```

#### 3.4 Metadata Preview

**Expandable Section:** Click **"Preview Metadata JSON"** to see:

```json
{
  "uid": "GP_XXXXX",
  "original_track_title": "Fall Down",
  "bpm": 145,
  "genre": "trap",
  "key": "F minor",
  "vocal_rights": "royalty_free",
  "energy_level": 5,
  "mood": ["aggressive", "dark"],
  "audio_file_count": 28,
  "midi_file_count": 7,
  "created_at": "2025-12-10T15:30:00"
}
```

Review for accuracy before exporting.

#### 3.5 Process & Export

Click **"🚀 Process & Export Dataset"** button.

**Processing Steps (with progress bar):**

```
🔄 Creating batch directory...              [5%]
🔄 Creating track directory...              [10%]
🔄 Processing stem 1/28: kick_main.wav      [15%]
🔄 Processing stem 2/28: bass_sub.wav       [20%]
... (each stem adds ~3%)
🔄 Generating metadata...                   [95%]
✅ Export complete!                          [100%]
```

**Per-Stem Processing:**

For each stem, the app:
1. Loads audio file
2. Resamples to 44.1kHz if needed
3. Slices to specified bar range
4. Converts to mono (if required by taxonomy)
5. Loads paired MIDI (if exists)
6. Slices MIDI to same bar range
7. Exports audio to `Audio/` folder
8. Exports MIDI to `MIDI/` folder

**Total Time:** ~18 seconds for 28 stems (depends on file sizes and CPU)

#### 3.6 Success Message

**Upon Completion:**

```
✅ Export Successful!

Dataset Details:
• UID: GP_00001
• Audio Files: 28
• MIDI Files: 7
• Output Location:
  C:\...\Clean_Dataset_Staging\Batch_2025-12-10\GP_00001_trap_145_Fmin

📂 Output Structure:
• Audio/ - 28 WAV files (44.1kHz, 24-bit)
• MIDI/ - 7 MIDI files (bar-aligned)
• Metadata/ - GP_00001_info.json
• Masters/ - (reserved)
```

**Next Steps:**

1. Navigate to output folder
2. Listen to a few stems in DAW
3. Verify audio/MIDI alignment
4. Check metadata JSON
5. Process next track (refresh page)

---

## 🎨 UI Features

### Auto-Features

#### Auto-Pairing
- **Fuzzy matching** with 70% threshold
- Compares filenames (e.g., "kick_main.wav" ↔ "kick.mid" = 100%)
- Ignores case and common suffixes (_v2, _final, etc.)
- Displays match score in table

#### Auto-Advancement
- After saving a label, jumps to next **unlabeled** stem
- Skips already-labeled stems
- Saves clicks and time

#### Auto-Validation
- Real-time mono/stereo requirement checks
- MIDI pairing warnings for melodic content
- Taxonomy compliance (only valid combinations shown)

#### Auto-Normalization
- Labels normalized to taxonomy format
- Case-insensitive (you can type lowercase)
- Spaces/underscores standardized

#### Auto-Resampling
- All audio converted to 44.1kHz
- Preserves bit depth (24-bit output)
- Uses high-quality SRC (sample rate conversion)

### Interactive Features

#### Waveform Visualizer
- See your audio in real-time
- Zoom/pan capability (via Matplotlib)
- Beat grid overlay for visual alignment

#### Beat Grid
- Derived from MIDI tempo (most accurate)
- Falls back to audio BPM detection if no MIDI
- Visual bar markers for precise slicing

#### Slice Preview
- Green highlight shows selected range
- Duration calculation in real-time
- Helps visualize export result

#### Manual Override
- One-click MIDI pairing changes
- Dropdown list of all available MIDI files
- Option to remove MIDI entirely

#### Progress Tracking
- Sidebar shows labeled vs total
- Visual progress percentage
- Table updates with checkmarks

### Validation Features

#### Required Fields
- Title must be entered
- Genre must be selected
- All stems must be labeled

#### Mood Limit
- Max 2 mood tags enforced
- Prevents over-tagging

#### Bar Range
- End bar must be > Start bar
- Prevents zero-length exports

#### BPM Range
- 40-300 BPM validated
- Catches typos

#### Taxonomy Compliance
- Instruments filtered by Group
- Invalid combinations prevented
- Always produces valid output

---

## 🔧 Advanced Usage

### Custom Slice Settings

**Same Slice for All Stems:**

Set Start/End bars in Step 2 (Label Stems). These settings apply to all stems in the current export.

**Example:**
```
Start Bar: 8  (skip intro)
End Bar: 24   (16-bar section)
Duration: 26.5 seconds
```

**Different Slices Per Stem:**

Not currently supported in UI. Use CLI tool for per-stem control:

```python
# See USAGE_EXAMPLES.py
slicer.slice_pair(
    audio_path,
    midi_path,
    start_bars=8,
    end_bars=24,
    tempo=145
)
```

### Batch Processing Multiple Tracks

**Option 1: Process One at a Time (UI)**

1. Complete workflow for Track 1
2. Note output location
3. Press **F5** or click Streamlit "Rerun" to reset
4. Start Track 2

**Option 2: Automated Batch (CLI)**

For 10+ tracks, use CLI scripting:

```python
tracks = [
    "Track_001_Fall_Down",
    "Track_002_Midnight",
    "Track_003_Pulse",
]

for track in tracks:
    subprocess.run([
        "python", "run_app.py",
        f"Raw_Audio/{track}",
        "--title", track,
        "--genre", "trap",
        "--bpm", "145"
    ])
```

### Workflow Tips

**Keyboard Shortcuts:**

- **Tab** - Navigate between dropdowns
- **Enter** - Click focused button
- **Ctrl+F5** - Hard refresh (reset session)

**Time-Saving Tips:**

1. Enable auto-advancement (default)
2. Use Tab key to navigate dropdowns
3. Start with stems you know (kick, snare, bass)
4. Leave ambiguous stems for last

---

## ⚠️ Troubleshooting

### UI Won't Launch

**Error:** `streamlit: command not found`

**Solution (Windows):**
```bash
python -m streamlit run streamlit_app.py
```

**Solution (macOS/Linux):**
```bash
python3 -m streamlit run streamlit_app.py
```

### "No Files Found"

**Checklist:**
- ✅ Path is correct and exists
- ✅ Folder contains .wav or .mid files
- ✅ You have read permissions
- ✅ No typos in path

**Test:**
```bash
# Windows
dir "C:\path\to\folder"

# macOS/Linux
ls "/path/to/folder"
```

### Waveform Won't Display

**Possible Causes:**

1. **File Corrupted**
   - Test: Open in DAW first
   - Solution: Re-export from DAW

2. **Unsupported Format**
   - Test: Check if 24-bit, 48kHz, etc.
   - Solution: Convert to standard 16/24-bit WAV

3. **File Too Large**
   - Test: Check file size (>1GB may cause issues)
   - Solution: Process shorter clips or use CLI

4. **Missing Dependencies**
   ```bash
   pip install matplotlib librosa
   ```

### MIDI Pairing Incorrect

**Symptoms:**
- Wrong MIDI file paired
- No MIDI when there should be

**Solutions:**

1. **Use Manual Override** (Step 2)
   - Check "Manual Pairing Override"
   - Select correct MIDI file
   - Apply

2. **Check Filename Similarity**
   - Auto-pairing uses fuzzy matching
   - "kick_v2.wav" matches "kick.mid" (90%)
   - "bassline.wav" won't match "sub.mid" (30%)

3. **Verify MIDI Files Exist**
   - Some stems genuinely have no MIDI
   - Drums/FX typically don't need MIDI

### Export Fails

**Error Messages:**

1. **"Not all stems labeled"**
   - Check sidebar: "Stems Labeled: X / Y"
   - Go to Step 2, label remaining stems
   - Table shows ⏳ for unlabeled

2. **"Please enter track title"**
   - Sidebar → Track Title field
   - Required field (no default)

3. **"Invalid BPM"**
   - Sidebar → BPM must be 40-300
   - Check for typos

4. **"Disk space error"**
   - Check available disk space
   - Each track ~500MB - 2GB
   - Clear space and retry

### Slice Settings Not Saving

**Note:** Slice settings are session-wide (not per-stem).

**Behavior:**
- Set Start/End bars in Step 2
- Settings apply to **all** stems in export
- Settings reset on page refresh

**Workaround for Per-Stem Slices:**
- Use CLI tool (`run_app.py`)
- Script per-stem slice ranges

### Session Lost on Refresh

**Cause:** Streamlit sessions are temporary.

**Prevention:**
- Complete full workflow in one session
- Don't refresh page mid-workflow
- Save labels as you go (auto-saved in session)

**Recovery:**
- No built-in session persistence
- Must re-label if page refreshed
- Future enhancement: Save/load session

---

## 💡 Tips & Best Practices

### Before Starting

1. **Organize Files**
   - One folder per track
   - Clear naming (helps auto-pairing)
   - Remove duplicates/unused files

2. **Check File Formats**
   - Audio: .wav (16 or 24-bit recommended)
   - MIDI: .mid (Type 1 or Type 0)
   - No MP3/OGG (not supported)

3. **Verify Vocal Rights**
   - Know if vocals are exclusive
   - Set toggle correctly before ingesting
   - Can't change after labeling starts

### During Labeling

1. **Use Waveform Visual**
   - Check beat grid alignment
   - Verify tempo is correct
   - Look for clipping/silence

2. **Follow Validation Warnings**
   - MIDI requirement warnings
   - Mono/stereo indicators
   - Taxonomy compliance

3. **Descriptive Layer Names**
   - Use "Main" for primary version
   - Use "Layer1/2/3" for stacked elements
   - Avoid generic names

4. **Save Frequently**
   - Auto-advancement saves clicks
   - Labels saved immediately in session
   - Can navigate back to change

### Before Export

1. **Verify Completion**
   - Sidebar: All stems labeled (100%)
   - Table: All rows have ✅
   - Metadata preview looks correct

2. **Review Slice Settings**
   - Start/End bars appropriate?
   - Duration reasonable (not too short/long)?
   - Matches track structure?

3. **Check Metadata**
   - Title spelled correctly
   - Genre accurate
   - BPM matches MIDI
   - Energy/mood appropriate

### After Export

1. **Quality Check**
   - Listen to 3-5 random stems in DAW
   - Check audio/MIDI alignment
   - Verify mono/stereo processing
   - Look for clipping/artifacts

2. **Validate Structure**
   - Files in correct folders
   - Naming schema correct
   - Metadata JSON complete
   - UID unique

3. **Back Up Data**
   - Copy `Clean_Dataset_Staging/` to safe location
   - Cloud backup recommended
   - Keep source files separately

---

## 🎬 Demo Walkthrough

### Sample Session (~5 Minutes)

**Track:** "Fall Down" (28 stems, 7 MIDI files)

#### Minute 0-1: Setup

1. Launch app: `python -m streamlit run streamlit_app.py`
2. Sidebar:
   - Vocal Rights: Royalty_Free
   - Title: "Fall Down"
   - Genre: Trap
   - BPM: 145
   - Key: F minor
   - Energy: 5
   - Mood: Aggressive, Dark

#### Minute 1-2: Ingest

3. Tab 1 (Ingest & Pair):
   - Source: `C:\...\Raw_input_sample\Fall Down`
   - Click "Scan & Pair Files"
   - Result: 28 audio, 7 MIDI, 7 paired (100%)

#### Minute 2-4: Label

4. Tab 2 (Label Stems):
   - Stem 1: kick_main.wav
     - Waveform: Clear kick pattern at 145 BPM
     - Group: Drums
     - Instrument: Kick
     - Layer: Main
     - Save (auto-advance)
   
   - Stem 2: bass_sub.wav
     - Waveform: Low-frequency with beat grid
     - MIDI: bass_sub.mid (100%)
     - Group: Bass
     - Instrument: Sub
     - Layer: Main
     - Save
   
   - (Repeat for all 28 stems...)
   - Progress: 28/28 (100%)

#### Minute 4-5: Export

5. Tab 3 (Export):
   - Output: Clean_Dataset_Staging (default)
   - Preview metadata: ✅
   - Click "Process & Export Dataset"
   - Progress: 100%
   - Success: GP_00001_trap_145_Fmin

**Total Time:** ~5 minutes for 28 stems

---

## 📊 UI vs CLI Comparison

| Feature | Streamlit UI | CLI (`run_app.py`) |
|---------|--------------|---------------------|
| **Visual Interface** | ✅ Interactive web UI | ❌ Terminal only |
| **Waveform Display** | ✅ With beat grid | ❌ No visualization |
| **Beat Grid Overlay** | ✅ MIDI/BPM based | ❌ No visual |
| **Learning Curve** | ⭐⭐ Easy | ⭐⭐⭐⭐ Advanced |
| **Labeling Method** | ✅ Dropdowns | ⚠️ Code dict |
| **Manual Pairing** | ✅ Checkbox UI | ⚠️ Edit code |
| **Progress Tracking** | ✅ Visual bars | ⚠️ Console logs |
| **Validation** | ✅ Real-time | ⚠️ Post-process |
| **Speed** | ⭐⭐⭐ Interactive | ⭐⭐⭐⭐⭐ Fast |
| **Batch Processing** | ⚠️ One at a time | ✅ Script loops |
| **Best For** | First-time, QC, learning | Bulk, automation |

**Recommendation:**
- **Use UI:** For first 10-20 tracks, quality control, learning workflow
- **Use CLI:** For 50+ tracks, automation, scripting, remote servers

---

## 🎓 Common Questions

### Q: Can I change labels after saving?

**A:** Yes! Navigate back to the stem (use Previous button) and save new labels. They'll overwrite.

### Q: Can I pause and resume later?

**A:** No. Session state is lost on page refresh. Complete the track in one session (~5 mins).

### Q: What if auto-pairing fails?

**A:** Use "Manual Pairing Override" in Step 2. Select the correct MIDI file from the dropdown.

### Q: Can I process multiple tracks at once?

**A:** No. Process one track at a time. Refresh page (F5) between tracks.

### Q: Where is my output?

**A:** Default: `Clean_Dataset_Staging/Batch_{date}/GP_{uid}_{genre}_{bpm}_{key}/`

### Q: How long does export take?

**A:** ~18 seconds for 25-30 stems (depends on file sizes and CPU speed).

### Q: Can I use on remote server?

**A:** Yes! Forward port 8501 via SSH:
```bash
ssh -L 8501:localhost:8501 user@server
python -m streamlit run streamlit_app.py
```

### Q: Is my data uploaded to the cloud?

**A:** No! 100% local processing. Streamlit runs on localhost only.

---

## 🚀 Next Steps

### Master the UI

1. Process sample data (`Raw_input_sample/Fall Down`)
2. Compare output with `Target_output_sample/`
3. Try all features (manual override, slice settings, etc.)

### Process Your Dataset

1. Start with 5-10 tracks
2. Validate output quality in DAW
3. Adjust workflow based on learnings
4. Scale up to full catalog

### Automate at Scale

1. Learn CLI tool (`run_app.py`)
2. Write batch scripts (see `USAGE_EXAMPLES.py`)
3. Set up monitoring/logging
4. Process thousands of tracks

---

**Version:** 2.0  
**Last Updated:** December 10, 2025  
**Status:** ✅ Production Ready

**Questions?** Check [README.md](README.md) for installation and troubleshooting, or review [USAGE_EXAMPLES.py](USAGE_EXAMPLES.py) for CLI usage.

---

**Happy Processing! 🎵**
