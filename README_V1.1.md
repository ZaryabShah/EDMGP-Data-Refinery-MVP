# EDMGP Data Refinery V1.1 - What's New

## 🚀 Major Improvements

### 1. Full Track Mode (Default)
- **No more auto-slicing** - Files are now renamed and resampled (44.1kHz) without cropping
- Toggle between **Full Track Mode** and **Loop Slicer Mode** with a simple radio button
- Perfect for processing complete tracks, long loops, or full compositions

### 2. Manual UID Control
- **User's UID is now the master source of truth**
- Enter your UID from the masterlist (e.g., `GP_00500`) and the app uses it exactly as entered
- No more auto-generated UIDs overwriting your input
- All output filenames and metadata use your manual UID

### 3. Better File Management
- **Delete buttons (🗑️)** - Remove unwanted files manually during ingestion
- **Vocal file flagging** - In Royalty_Free mode, vocal files are highlighted in red for review (not auto-deleted)
- **Audio playback (▶️)** - Listen to files before processing in Steps 1 and 2
- Full control over what gets processed

### 4. Enhanced Genre System
- **Parent/Child genre structure** - Two dropdowns instead of one
- Select parent genre (House, Techno, Bass Music, etc.)
- Then choose specific sub-genre (Tech House, Trap Festival, etc.)
- More organized and accurate genre classification

### 5. Custom Instruments
- **"Other" option** added to all instrument lists
- Text input appears when "Other" is selected
- Enter custom instrument names like "Laser", "Siren", "Alarm"
- Perfect for unique sound design elements

### 6. Improved MIDI Detection
- **Fully recursive** - Finds MIDI files in all subfolders (including `/MIDI` directories)
- **Case-insensitive** - Detects `.mid`, `.MID`, `.midi`, `.MIDI`
- No more missing MIDI files

### 7. Better UI/UX
- **Optimized layout** - Labeling dropdowns moved to top of page for faster workflow
- **All text visible** - Fixed CSS issues where text was invisible in info boxes
- **Task Mode toggle** at top of Step 2 for clear mode selection
- Cleaner, more intuitive interface

### 8. Metadata Schema V2
- **New JSON structure** with `global_attributes` and `stems_manifest`
- **Per-stem metadata** including filename, type, channels, and MIDI pair
- **Sample types** - "full_track" or "loop" based on processing mode
- **AI content flag** - Track if content is AI-generated
- More structured and professional metadata output

---

## 📋 Quick Comparison

| Feature | V1.0 | V1.1 |
|---------|------|------|
| Default Mode | Auto-slice everything | Full Track (no slicing) |
| UID Control | Auto-generated | Manual entry |
| File Management | No delete option | Delete buttons + vocal flagging |
| Audio Preview | None | Playback buttons |
| Genre System | Single dropdown | Parent/Child structure |
| Custom Instruments | Fixed lists only | "Other" with text input |
| MIDI Detection | Limited | Recursive + case-insensitive |
| UI Layout | Basic | Optimized dropdowns at top |
| Metadata | Simple schema | V2 with stems manifest |

---

## 🎯 Key Benefits

✅ **More Control** - You decide what gets sliced, what gets deleted, and what UID to use  
✅ **Faster Workflow** - Better layout, audio preview, and delete buttons save time  
✅ **Better Organization** - Parent/child genres and custom instruments improve classification  
✅ **Professional Output** - Metadata V2 with detailed per-stem information  
✅ **Flexibility** - Switch between Full Track and Loop Slicer modes as needed  

---

## 🚀 Getting Started

```powershell
# Launch the app
python -m streamlit run streamlit_app.py
```

**Access at:** http://localhost:8501

---

**Version:** 1.1  
**Release Date:** December 14, 2025  
**Status:** ✅ Production Ready
