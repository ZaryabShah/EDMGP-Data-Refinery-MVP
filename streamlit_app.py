"""
EDMGP Data Refinery App - Streamlit UI V1.1
Complete rewrite with all client-requested features
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
import base64

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from ingestion import FileIngester
from audio_processing import AudioProcessor, MIDIProcessor, AlignedSlicer
from metadata import MetadataGenerator, StemValidator
from export import ExportSession

# WaveSurfer Audio Player Component
def wavesurfer_player(audio_path: Path, height: int = 128, key: str = None, enable_regions: bool = False, start_bar: float = 0, end_bar: float = 16, bpm: float = 140):
    """
    Custom WaveSurfer.js audio player with waveform visualization
    
    Args:
        audio_path: Path to audio file
        height: Waveform height in pixels
        key: Unique key for component
        enable_regions: Enable region selection for Loop Slicer
        start_bar: Start bar for region (if enabled)
        end_bar: End bar for region (if enabled)
        bpm: BPM for time calculations
    """
    # V1.3 Performance: Use cached base64 encoding
    cache_key = str(audio_path)
    if cache_key not in st.session_state.wavesurfer_b64_cache:
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        st.session_state.wavesurfer_b64_cache[cache_key] = base64.b64encode(audio_bytes).decode()
    
    audio_b64 = st.session_state.wavesurfer_b64_cache[cache_key]
    
    # Calculate region times if enabled
    region_start = (start_bar * 4 * 60 / bpm) if enable_regions else 0
    region_end = (end_bar * 4 * 60 / bpm) if enable_regions else 0
    
    # Generate unique component ID
    component_id = f"wavesurfer_{key}" if key else f"wavesurfer_{hash(str(audio_path))}"
    
    # HTML/JavaScript for WaveSurfer
    html_code = f"""
    <div id="{component_id}" style="width: 100%; margin: 10px 0;"></div>
    <div id="controls_{component_id}" style="margin-top: 10px;">
        <button onclick="ws_{component_id}.playPause()" style="padding: 8px 16px; margin: 2px; cursor: pointer; background: #1f77b4; color: white; border: none; border-radius: 4px;">
            ▶️ Play/Pause
        </button>
        <button onclick="ws_{component_id}.stop()" style="padding: 8px 16px; margin: 2px; cursor: pointer; background: #d73a49; color: white; border: none; border-radius: 4px;">
            ⏹️ Stop
        </button>
        <button onclick="window.zoomLevel_{component_id} = Math.min(window.zoomLevel_{component_id} * 2, 800); window.ws_{component_id}.zoom(window.zoomLevel_{component_id});" style="padding: 8px 16px; margin: 2px; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 4px;">
            🔍 Zoom In
        </button>
        <button onclick="window.zoomLevel_{component_id} = Math.max(window.zoomLevel_{component_id} / 2, 20); window.ws_{component_id}.zoom(window.zoomLevel_{component_id});" style="padding: 8px 16px; margin: 2px; cursor: pointer; background: #28a745; color: white; border: none; border-radius: 4px;">
            🔍 Zoom Out
        </button>
        <span id="time_{component_id}" style="margin-left: 15px; font-weight: bold;">0:00 / 0:00</span>
    </div>
    
    <script src="https://unpkg.com/wavesurfer.js@7"></script>
    <script src="https://unpkg.com/wavesurfer.js@7/dist/plugins/regions.js"></script>
    <script>
        (function() {{
            // Wait for WaveSurfer to load
            if (typeof WaveSurfer === 'undefined') {{
                setTimeout(arguments.callee, 100);
                return;
            }}
            
            // Clear existing instance if any
            if (window.ws_{component_id}) {{
                window.ws_{component_id}.destroy();
            }}
            
            // V1.3 FIX: Track zoom level separately (params.minPxPerSec is undefined in v7)
            let zoomLevel_{component_id} = 50;
            
            // Create WaveSurfer instance
            const ws_{component_id} = WaveSurfer.create({{
                container: '#{component_id}',
                waveColor: '#4a9eff',
                progressColor: '#1f77b4',
                cursorColor: '#ff6b6b',
                barWidth: 2,
                barGap: 1,
                height: {height},
                normalize: true,
                backend: 'WebAudio',
                minPxPerSec: zoomLevel_{component_id}
            }});
            
            // Store globally so buttons can access
            window.ws_{component_id} = ws_{component_id};
            window.zoomLevel_{component_id} = zoomLevel_{component_id};
            
            // Load audio from base64
            const audioData = 'data:audio/wav;base64,{audio_b64}';
            ws_{component_id}.load(audioData);
            
            // Update time display
            ws_{component_id}.on('audioprocess', function() {{
                const current = ws_{component_id}.getCurrentTime();
                const duration = ws_{component_id}.getDuration();
                document.getElementById('time_{component_id}').textContent = 
                    formatTime(current) + ' / ' + formatTime(duration);
            }});
            
            ws_{component_id}.on('ready', function() {{
                const duration = ws_{component_id}.getDuration();
                document.getElementById('time_{component_id}').textContent = 
                    '0:00 / ' + formatTime(duration);
                    
                {f'''
                // Add region for Loop Slicer mode
                if ({str(enable_regions).lower()}) {{
                    const regionsPlugin = ws_{component_id}.registerPlugin(WaveSurfer.Regions.create());
                    regionsPlugin.addRegion({{
                        start: {region_start},
                        end: {region_end},
                        color: 'rgba(0, 255, 0, 0.2)',
                        drag: true,
                        resize: true
                    }});
                }}
                ''' if enable_regions else ''}
            }});
            
            function formatTime(seconds) {{
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return mins + ':' + (secs < 10 ? '0' : '') + secs;
            }}
        }})();
    </script>
    """
    
    st.components.v1.html(html_code, height=height + 80, scrolling=False)

# Page configuration
st.set_page_config(
    page_title="EDMGP Data Refinery V1.1",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme-aware Custom CSS
def apply_theme_css(theme="dark"):
    """Apply theme-specific CSS styles"""
    if theme == "dark":
        # Dark Theme - Default
        css = """
<style>
    /* Dark Theme */
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #58a6ff;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f78166;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #1c2433;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #58a6ff;
        margin: 0.5rem 0;
        color: #c9d1d9 !important;
    }
    .warning-box {
        background-color: #2d2205;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f0ad4e;
        margin: 0.5rem 0;
        color: #f0ad4e !important;
    }
    .success-box {
        background-color: #0d2818;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #56d364;
        margin: 0.5rem 0;
        color: #aff5b4 !important;
    }
    .vocal-flag-box {
        background-color: #ff4444;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 6px solid #cc0000;
        margin: 0.5rem 0;
        color: #ffffff !important;
        font-weight: 600;
    }
    /* Dark theme text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #c9d1d9 !important;
    }
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #c9d1d9 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
    }
</style>
"""
    else:
        # Light Theme
        css = """
<style>
    /* Light Theme */
    .stApp {
        background-color: #ffffff;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0366d6;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #d73a49;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0366d6;
        margin: 0.5rem 0;
        color: #24292e !important;
    }
    .warning-box {
        background-color: #fffbdd;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f9c513;
        margin: 0.5rem 0;
        color: #735c0f !important;
    }
    .success-box {
        background-color: #dcffe4;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2da44e;
        margin: 0.5rem 0;
        color: #1a7f37 !important;
    }
    .vocal-flag-box {
        background-color: #ffe0e0;
        padding: 0.8rem;
        border-radius: 0.5rem;
        border-left: 4px solid #d73a49;
        margin: 0.5rem 0;
        color: #b31d28 !important;
    }
    /* Light theme text colors */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #24292e !important;
    }
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #24292e !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f6f8fa;
    }
    .stTabs [data-baseweb="tab"] {
        color: #57606a;
    }
    .stTabs [aria-selected="true"] {
        color: #0366d6 !important;
    }
</style>
"""
    
    st.markdown(css, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables (V1.1)"""
    defaults = {
        'ingester': None,
        'source_dir': None,
        'vocal_rights': "Exclusive",
        'stem_labels': {},
        'current_stem_index': 0,
        'track_metadata': {},
        'processing_complete': False,
        'manual_overrides': {},
        'slice_settings': {'start_bars': 0, 'end_bars': 16},
        # V1.1 Critical additions
        'enable_slicer': False,  # Default: Full Track Mode
        'deleted_pairs': set(),
        'custom_instruments': {},
        'manual_uid': "",
        'vocal_flagged_indices': set(),
        'theme': 'dark',  # Default to dark theme
        'lyrics_file': None,  # V1.3: Uploaded lyrics file
        'preview_ingest_idx': None,  # V1.3: Selected file for preview in Step 1
        'wavesurfer_b64_cache': {}  # V1.3: Cache for base64 encoded audio
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def plot_waveform_with_grid(audio_path, midi_path=None, bpm=None, start_bars=0, end_bars=16):
    """Plot audio waveform with beat grid overlay"""
    try:
        audio_proc = AudioProcessor()
        audio_data, sr = audio_proc.load_audio(Path(audio_path))
        
        # Convert to mono
        if audio_data.ndim > 1:
            audio_mono = audio_proc.get_mono_mix(audio_data)
        else:
            audio_mono = audio_data
        
        # Get BPM
        if bpm is None:
            if midi_path:
                midi_proc = MIDIProcessor()
                midi_info = midi_proc.get_midi_info(Path(midi_path))
                bpm = midi_info.tempo
            else:
                bpm = audio_proc.detect_bpm(audio_mono, sr)
        
        # Calculate bar times
        bar_duration = (60 / bpm) * 4
        start_time = start_bars * bar_duration
        end_time = end_bars * bar_duration
        
        # Create figure - V1.3 FIX: Larger size for better transient visibility
        fig, ax = plt.subplots(figsize=(18, 6))
        librosa.display.waveshow(audio_mono, sr=sr, ax=ax, alpha=0.6)
        
        # Add beat grid
        beat_times = np.arange(start_time, min(end_time, len(audio_mono)/sr), bar_duration)
        for i, beat_time in enumerate(beat_times):
            ax.axvline(x=beat_time, color='red', linestyle='--', alpha=0.5, linewidth=1)
            ax.text(beat_time, ax.get_ylim()[1] * 0.9, f'Bar {start_bars + i}', 
                    rotation=90, verticalalignment='top', fontsize=8, color='red')
        
        # Highlight selection
        ax.axvspan(start_time, min(end_time, len(audio_mono)/sr), 
                   alpha=0.2, color='green', label='Selected Range')
        
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Amplitude')
        ax.set_title(f'Waveform with Beat Grid (BPM: {bpm:.1f})')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error plotting waveform: {str(e)}")
        return None


def render_sidebar():
    """Render sidebar (V1.1 - Updated with manual UID and parent/child genres)"""
    with st.sidebar:
        st.markdown('<p class="main-header">⚙️ Configuration</p>', unsafe_allow_html=True)
        
        # Theme Switcher
        st.markdown("### 🎨 Theme")
        theme = st.radio(
            "Color Mode",
            options=["dark", "light"],
            index=0 if st.session_state.theme == "dark" else 1,
            format_func=lambda x: "🌙 Dark Mode" if x == "dark" else "☀️ Light Mode",
            help="Switch between dark and light color themes"
        )
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        st.markdown("---")
        
        # V1.3 Performance: Clear audio cache button
        if st.session_state.wavesurfer_b64_cache:
            cache_size = len(st.session_state.wavesurfer_b64_cache)
            if st.button(f"🗑️ Clear Audio Cache ({cache_size} files)", help="Free memory by clearing cached audio data"):
                st.session_state.wavesurfer_b64_cache = {}
                st.success("Cache cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Vocal Rights
        st.markdown("### Vocal Rights Gate")
        vocal_rights = st.radio(
            "Contains Exclusive Vocals?",
            options=["Exclusive", "Royalty_Free"],
            index=0 if st.session_state.vocal_rights == "Exclusive" else 1,
            help="Royalty_Free mode flags vocal files for review/deletion"
        )
        st.session_state.vocal_rights = vocal_rights
        
        if vocal_rights == "Royalty_Free":
            st.warning("🎤 Vocal stems will be flagged in red")
        
        # V1.3 FIX #3: Lyrics Upload (only for Exclusive vocals)
        if vocal_rights == "Exclusive":
            st.markdown("### 📝 Lyrics Upload")
            uploaded_lyrics = st.file_uploader(
                "Upload Lyrics (optional)",
                type=["txt", "docx", "pdf"],
                help="Upload lyrics for exclusive vocal tracks",
                key="lyrics_upload"
            )
            if uploaded_lyrics:
                st.session_state.lyrics_file = uploaded_lyrics
                st.success(f"✅ Lyrics uploaded: {uploaded_lyrics.name}")
        
        st.markdown("---")
        
        # Track Metadata
        st.markdown("### Track Metadata")
        
        # V1.1: Manual UID Control (CRITICAL)
        manual_uid = st.text_input(
            "Track UID",
            value=st.session_state.manual_uid,
            placeholder="GP_00500",
            help="⚠️ MASTER SOURCE OF TRUTH - Enter UID from your masterlist. This will be used as-is."
        )
        st.session_state.manual_uid = manual_uid
        
        if not manual_uid:
            st.error("❌ UID Required! Enter UID from masterlist (e.g., GP_00500)")
        
        track_title = st.text_input(
            "Track Title",
            placeholder="Fall Down - Trap Dubstep",
            help="Full track title including style/genre"
        )
        
        # V1.1: Parent/Child Genre
        st.markdown("#### Genre Classification")
        parent_genre = st.selectbox(
            "Parent Genre",
            options=list(config.PARENT_GENRES.keys()),
            format_func=lambda x: config.PARENT_GENRES[x],
            help="Broad genre category"
        )
        
        sub_genre_options = config.SUB_GENRES.get(parent_genre, [])
        sub_genre = st.selectbox(
            "Sub-Genre",
            options=sub_genre_options,
            help="Specific sub-genre"
        )
        
        # BPM and Key
        col1, col2 = st.columns(2)
        with col1:
            bpm = st.number_input("BPM", min_value=40, max_value=300, value=140, step=1)
        with col2:
            key = st.text_input("Key", value="Cmin", placeholder="Cmin, Fmaj")
        
        energy_level = st.slider("Energy Level", 1, 5, 3)
        
        moods = st.multiselect(
            "Mood Tags (max 2)",
            options=config.MOODS,
            max_selections=2
        )
        
        # V1.1: AI Content Flag
        contains_ai = st.checkbox("Contains AI-generated content", value=False)
        
        # Store metadata
        st.session_state.track_metadata = {
            'uid': manual_uid,
            'title': track_title,
            'genre_parent': parent_genre,
            'genre_sub': sub_genre,
            'bpm': bpm,
            'key': key,
            'energy_level': energy_level,
            'mood': [m.lower() for m in moods],
            'contains_ai': contains_ai
        }
        
        st.markdown("---")
        
        # Status
        st.markdown("### Status")
        if st.session_state.ingester:
            active_pairs = [p for idx, p in enumerate(st.session_state.ingester.pairs) 
                           if idx not in st.session_state.deleted_pairs]
            num_pairs = len(active_pairs)
            num_labeled = sum(1 for idx, p in enumerate(st.session_state.ingester.pairs)
                            if idx not in st.session_state.deleted_pairs 
                            and p.audio.filename in st.session_state.stem_labels)
            
            st.metric("Active Stems", num_pairs)
            st.metric("Labeled Stems", num_labeled)
            
            if num_labeled == num_pairs and num_pairs > 0:
                st.success("✅ All stems labeled!")
            elif num_pairs > 0:
                st.info(f"⏳ {num_pairs - num_labeled} stems remaining")


def render_step1_ingestion():
    """Step 1: Ingestion with delete buttons and vocal flagging (V1.1)"""
    st.markdown('<p class="sub-header">📂 Step 1: File Ingestion & Auto-Pairing</p>', 
                unsafe_allow_html=True)
    
    # Directory input
    source_dir = st.text_input(
        "Source Directory",
        value=st.session_state.source_dir or "",
        placeholder="C:\\Path\\To\\Your\\Stems",
        help="Folder containing .wav and .mid files (searches recursively in subfolders)"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔍 Scan & Pair Files", type="primary", use_container_width=True):
            if source_dir:
                st.session_state.source_dir = source_dir
                
                with st.spinner("Scanning files recursively..."):
                    try:
                        ingester = FileIngester(Path(source_dir))
                        ingester.scan_files()
                        ingester.auto_pair_files()
                        
                        # Flag vocal files (V1.1)
                        if st.session_state.vocal_rights == "Royalty_Free":
                            vocal_indices = ingester.flag_vocal_files()
                            st.session_state.vocal_flagged_indices = set(vocal_indices)
                            if vocal_indices:
                                st.warning(f"🎤 Flagged {len(vocal_indices)} vocal file(s) for review")
                        
                        st.session_state.ingester = ingester
                        st.session_state.stem_labels = {}
                        st.session_state.current_stem_index = 0
                        st.session_state.deleted_pairs = set()
                        
                        st.success(f"✅ Found {len(ingester.audio_files)} audio and {len(ingester.midi_files)} MIDI files")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.error("Please enter a source directory path")
    
    # Display results with delete buttons and audio playback (V1.1)
    if st.session_state.ingester:
        st.markdown("### Pairing Results")
        st.caption("🎤 = Vocal file (flagged in Royalty_Free mode) | 🗑️ = Delete | ▶️ = Play audio")
        
        # Build active pairs list
        active_pairs = [(idx, p) for idx, p in enumerate(st.session_state.ingester.pairs) 
                       if idx not in st.session_state.deleted_pairs]
        
        if not active_pairs:
            st.info("No active files. All have been deleted.")
        else:
            for display_num, (original_idx, pair) in enumerate(active_pairs, 1):
                # Check if vocal (V1.3 FIX #4: Enhanced vocal detection)
                is_vocal = original_idx in st.session_state.vocal_flagged_indices
                
                # V1.3 FIX #4: Use strong red highlight for vocal files
                if is_vocal:
                    st.markdown(f"""
                    <div style='background-color: #ff4444; padding: 10px; border-radius: 5px; 
                                border-left: 6px solid #cc0000; margin: 5px 0;'>
                        <span style='color: white; font-weight: 600;'>
                            🎤 VOCAL FILE - #{display_num}: {pair.audio.filename}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 2, 1.5, 0.5])
                
                with col1:
                    st.markdown(f"**{display_num}**")
                
                with col2:
                    icon = "🎤 " if is_vocal else ""
                    status = "✅" if pair.audio.filename in st.session_state.stem_labels else "⏳"
                    display_name = f"**{pair.audio.filename}**" if not is_vocal else pair.audio.filename
                    st.markdown(f"{icon}{display_name} {status}")
                
                with col3:
                    midi_text = pair.midi.filename if pair.midi else "❌ No MIDI"
                    score_text = f"({pair.match_score:.0f}%)" if pair.midi else ""
                    st.markdown(f"{midi_text} {score_text}")
                
                with col4:
                    # V1.3 Performance: Single shared preview instead of per-row player
                    if st.button("▶️ Preview", key=f"preview_btn_{original_idx}", help="Preview this audio file"):
                        st.session_state.preview_ingest_idx = original_idx
                        st.rerun()
                
                with col5:
                    # Delete button (V1.1)
                    if st.button("🗑️", key=f"delete_{original_idx}", help="Remove this file"):
                        st.session_state.deleted_pairs.add(original_idx)
                        # Also remove from labels if present
                        if pair.audio.filename in st.session_state.stem_labels:
                            del st.session_state.stem_labels[pair.audio.filename]
                        st.rerun()
        
        # V1.3 Performance: Single shared preview player for selected file
        preview_idx = st.session_state.get('preview_ingest_idx')
        if preview_idx is not None and preview_idx not in st.session_state.deleted_pairs:
            preview_pair = st.session_state.ingester.pairs[preview_idx]
            st.markdown("---")
            st.markdown("### 🎵 Audio Preview (Waveform with Zoom)")
            st.caption(f"**File:** {preview_pair.audio.filename}")
            wavesurfer_player(
                audio_path=preview_pair.audio.path,
                height=120,
                key=f"ingest_preview_{preview_idx}",
                enable_regions=False
            )
        
        # Summary
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Files", len(active_pairs))
        with col2:
            midi_count = sum(1 for _, p in active_pairs if p.midi)
            st.metric("With MIDI", midi_count)
        with col3:
            vocal_count = len(st.session_state.vocal_flagged_indices - st.session_state.deleted_pairs)
            st.metric("Vocal Files", vocal_count)
        with col4:
            st.metric("Deleted", len(st.session_state.deleted_pairs))


def render_step2_labeling():
    """Step 2: Labeling with Task Mode toggle and optimized layout (V1.1)"""
    st.markdown('<p class="sub-header">🎨 Step 2: Stem Labeling</p>', 
                unsafe_allow_html=True)
    
    if not st.session_state.ingester:
        st.info("👆 Please complete Step 1 first")
        return
    
    # Get active pairs
    active_pairs = [(idx, p) for idx, p in enumerate(st.session_state.ingester.pairs) 
                   if idx not in st.session_state.deleted_pairs]
    
    if not active_pairs:
        st.warning("No files to label (all deleted)")
        return
    
    # V1.1: Task Mode Toggle (CRITICAL)
    st.markdown("### Processing Mode")
    task_mode = st.radio(
        "Select Mode:",
        options=["Full Track (Default)", "Loop Slicer"],
        horizontal=True,
        help="Full Track = Rename only, no cropping | Loop Slicer = Slice to specific bars"
    )
    st.session_state.enable_slicer = (task_mode == "Loop Slicer")
    
    if not st.session_state.enable_slicer:
        st.info("📁 **Full Track Mode:** Files will be renamed and resampled (44.1kHz) without cropping")
    else:
        st.info("✂️ **Loop Slicer Mode:** Files will be cropped to selected bar range")
    
    st.markdown("---")
    
    # Navigation
    current_idx = st.session_state.current_stem_index
    
    # Ensure current index is valid
    if current_idx >= len(active_pairs):
        st.session_state.current_stem_index = 0
        current_idx = 0
    
    total_stems = len(active_pairs)
    _, current_pair = active_pairs[current_idx]
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=(current_idx == 0)):
            st.session_state.current_stem_index = max(0, current_idx - 1)
            st.rerun()
    with col3:
        st.markdown(f"### Stem {current_idx + 1} of {total_stems}")
    with col5:
        if st.button("Next ➡️", disabled=(current_idx >= total_stems - 1)):
            st.session_state.current_stem_index = min(total_stems - 1, current_idx + 1)
            st.rerun()
    
    st.markdown("---")
    
    # V1.1: OPTIMIZED LAYOUT - Labels at TOP
    st.markdown("### Quick Label Entry")
    
    existing_label = st.session_state.stem_labels.get(current_pair.audio.filename)
    
    # Dropdowns in single row at TOP (V1.1 - Critical UX fix)
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
    
    with col1:
        # Find group index with case-insensitive matching
        default_group_index = 0
        if existing_label:
            normalized_existing = config.normalize_group(existing_label[0])
            try:
                default_group_index = config.GROUPS.index(normalized_existing)
            except ValueError:
                # Fallback to case-insensitive search
                for i, g in enumerate(config.GROUPS):
                    if g.lower() == existing_label[0].lower():
                        default_group_index = i
                        break
        
        group = st.selectbox(
            "Group",
            options=config.GROUPS,
            index=default_group_index,
            key="label_group"
        )
    
    with col2:
        instruments = config.INSTRUMENTS.get(group, [])
        
        # V1.1: Handle custom instruments
        if existing_label and existing_label[1] not in instruments and existing_label[1] != "Other":
            # Previously saved custom instrument
            instruments_display = instruments.copy()
            if existing_label[1] not in instruments_display:
                instruments_display.insert(-1, existing_label[1])  # Add before "Other"
            instrument = st.selectbox("Instrument", options=instruments_display, 
                                    index=instruments_display.index(existing_label[1]), key="label_instrument")
        else:
            instrument = st.selectbox("Instrument", options=instruments,
                                    index=instruments.index(existing_label[1]) if existing_label and existing_label[1] in instruments else 0,
                                    key="label_instrument")
    
    with col3:
        # Find layer index with case-insensitive matching
        default_layer_index = 0
        if existing_label:
            normalized_existing = config.normalize_layer(existing_label[2])
            try:
                default_layer_index = config.LAYERS.index(normalized_existing)
            except ValueError:
                # Fallback to case-insensitive search
                for i, lyr in enumerate(config.LAYERS):
                    if lyr.lower() == existing_label[2].lower():
                        default_layer_index = i
                        break
        
        layer = st.selectbox(
            "Layer",
            options=config.LAYERS,
            index=default_layer_index,
            key="label_layer"
        )
    
    with col4:
        save_button = st.button("💾 Save", type="primary", use_container_width=True)
    
    # V1.1: "Other" instrument handling
    custom_instrument_value = None
    if instrument == "Other":
        st.markdown("#### Custom Instrument")
        custom_instrument_value = st.text_input(
            "Enter instrument name:",
            value=st.session_state.custom_instruments.get(current_pair.audio.filename, ""),
            placeholder="e.g., Laser, Siren, Alarm",
            key="custom_inst_input"
        )
        if custom_instrument_value:
            st.session_state.custom_instruments[current_pair.audio.filename] = custom_instrument_value
    
    # Save label logic
    if save_button:
        # Use custom instrument if "Other" was selected
        final_instrument = custom_instrument_value if instrument == "Other" and custom_instrument_value else instrument
        
        if instrument == "Other" and not custom_instrument_value:
            st.error("❌ Please enter a custom instrument name")
        else:
            # Normalize
            normalized_group = config.normalize_group(group)
            normalized_instrument = config.normalize_instrument(final_instrument)
            normalized_layer = config.normalize_layer(layer)
            
            st.session_state.stem_labels[current_pair.audio.filename] = (
                normalized_group,
                normalized_instrument,
                normalized_layer
            )
            
            st.success(f"✅ Saved: {normalized_group}/{normalized_instrument}/{normalized_layer}")
            
            # Auto-advance
            for i in range(current_idx + 1, total_stems):
                next_pair = active_pairs[i][1]
                if next_pair.audio.filename not in st.session_state.stem_labels:
                    st.session_state.current_stem_index = i
                    st.rerun()
                    return
            
            st.info("🎉 All stems labeled!")
    
    st.markdown("---")
    
    # File info
    st.markdown("### Current File")
    st.markdown(f"**Audio:** `{current_pair.audio.filename}`")
    if current_pair.midi:
        st.markdown(f"**MIDI:** `{current_pair.midi.filename}` ({current_pair.match_score:.0f}% match)")
    else:
        st.warning("⚠️ No MIDI paired")
    
    # V1.3 Performance: Show preview only when NOT in slicer mode (slicer has its own player)
    if not st.session_state.enable_slicer:
        st.markdown("#### 🎵 Audio Preview (with Zoom)")
        wavesurfer_player(
            audio_path=current_pair.audio.path,
            height=150,
            key=f"labeling_{current_idx}",
            enable_regions=False
        )
    
    # Validation helpers
    validator = StemValidator()
    col1, col2 = st.columns(2)
    with col1:
        force_mono = validator.should_force_mono(group, instrument)
        if force_mono:
            st.info(f"ℹ️ Will convert to **MONO** ({group}/{instrument})")
        else:
            st.info("ℹ️ Will keep **STEREO**")
    with col2:
        requires_midi = validator.requires_midi(group)
        if requires_midi and not current_pair.midi:
            st.warning(f"⚠️ {group} stems typically need MIDI!")
    
    # Conditional waveform display (V1.1 - Only show in Loop Slicer mode)
    if st.session_state.enable_slicer:
        st.markdown("---")
        st.markdown("### Waveform & Slice Settings")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("#### Slice Range")
            start_bars = st.number_input("Start Bar", 0, 64, 
                                        st.session_state.slice_settings.get('start_bars', 0), 1)
            end_bars = st.number_input("End Bar", 1, 128, 
                                      st.session_state.slice_settings.get('end_bars', 16), 1)
            
            st.session_state.slice_settings = {'start_bars': start_bars, 'end_bars': end_bars}
            
            if end_bars <= start_bars:
                st.error("End bar must be > start bar")
            else:
                bpm = st.session_state.track_metadata.get('bpm', 140)
                duration = ((end_bars - start_bars) * 4 * 60) / bpm
                st.info(f"⏱️ {duration:.2f}s\n({end_bars - start_bars} bars)")
        
        with col1:
            try:
                # V1.3: Interactive WaveSurfer with region selection for Loop Slicer
                st.markdown("#### Interactive Waveform (Drag region to adjust slice)")
                wavesurfer_player(
                    audio_path=current_pair.audio.path,
                    height=200,
                    key=f"slicer_{current_idx}",
                    enable_regions=True,
                    start_bar=start_bars,
                    end_bar=end_bars,
                    bpm=st.session_state.track_metadata.get('bpm', 140)
                )
            except Exception as e:
                st.error(f"Cannot display waveform: {str(e)}")
    
    # Manual MIDI override
    if st.checkbox("🔧 Manual MIDI Override", key="midi_override_check"):
        if st.session_state.ingester.midi_files:
            midi_options = ["❌ No MIDI"] + [m.filename for m in st.session_state.ingester.midi_files]
            current_midi = current_pair.midi.filename if current_pair.midi else "❌ No MIDI"
            
            selected_midi = st.selectbox("MIDI File:", midi_options, 
                                        index=midi_options.index(current_midi) if current_midi in midi_options else 0)
            
            if st.button("Apply Override"):
                if selected_midi == "❌ No MIDI":
                    st.session_state.manual_overrides[current_pair.audio.filename] = None
                else:
                    midi_file = next((m for m in st.session_state.ingester.midi_files if m.filename == selected_midi), None)
                    st.session_state.manual_overrides[current_pair.audio.filename] = midi_file
                st.success(f"✅ Override applied: {selected_midi}")
                st.rerun()


def render_step3_export():
    """Step 3: Export with Full Track Mode support and Metadata V2 (V1.1)"""
    st.markdown('<p class="sub-header">📦 Step 3: Export Dataset</p>', 
                unsafe_allow_html=True)
    
    if not st.session_state.ingester:
        st.info("👆 Please complete Step 1 first")
        return
    
    # Get active pairs
    active_pairs = [(idx, p) for idx, p in enumerate(st.session_state.ingester.pairs) 
                   if idx not in st.session_state.deleted_pairs]
    
    total_stems = len(active_pairs)
    labeled_stems = sum(1 for _, p in active_pairs if p.audio.filename in st.session_state.stem_labels)
    
    # Validation
    if labeled_stems < total_stems:
        st.warning(f"⚠️ Only {labeled_stems}/{total_stems} stems labeled. Please label all before exporting.")
        return
    
    metadata = st.session_state.track_metadata
    
    # V1.1: Require manual UID
    if not metadata.get('uid'):
        st.error("❌ **UID Required!** Please enter Track UID in the sidebar (e.g., GP_00500)")
        return
    
    if not metadata.get('title'):
        st.error("❌ **Title Required!** Please enter Track Title in the sidebar")
        return
    
    # Export config
    st.markdown("### Export Configuration")
    output_dir = st.text_input("Output Directory", value="Clean_Dataset_Staging")
    
    # Summary
    st.markdown("### Export Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Stems", total_stems)
    with col2:
        midi_count = sum(1 for _, p in active_pairs if p.midi)
        st.metric("With MIDI", midi_count)
    with col3:
        mode_text = "Full Track" if not st.session_state.enable_slicer else "Loop Slice"
        st.metric("Mode", mode_text)
    with col4:
        st.metric("UID", metadata['uid'])
    
    # Metadata preview
    with st.expander("📄 Metadata Preview (Schema V2)"):
        preview = {
            "uid": metadata['uid'],
            "original_folder_name": Path(st.session_state.source_dir).name if st.session_state.source_dir else "Unknown",
            "global_attributes": {
                "genre_parent": metadata['genre_parent'],
                "genre_sub": metadata['genre_sub'],
                "bpm": metadata['bpm'],
                "key": metadata['key'],
                "energy_level": metadata['energy_level'],
                "moods": metadata['mood'],
                "vocal_rights": st.session_state.vocal_rights.lower(),
                "contains_ai": metadata.get('contains_ai', False)
            },
            "stems_manifest": f"[{total_stems} stems with full metadata]",
            "processing_info": {
                "date_processed": "2025-12-14",
                "app_version": "v1.1"
            }
        }
        st.json(preview)
    
    st.markdown("---")
    
    # Export button
    if st.button("🚀 Process & Export Dataset", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize
            audio_proc = AudioProcessor()
            slicer = AlignedSlicer() if st.session_state.enable_slicer else None
            metadata_gen = MetadataGenerator()
            export_session = ExportSession(output_dir)
            
            # Start batch
            status_text.text("Creating batch directory...")
            batch_path = export_session.start_batch()
            progress_bar.progress(5)
            
            # Use manual UID (V1.1 - CRITICAL)
            uid = metadata['uid']
            
            # Create track directory
            status_text.text("Creating track directory...")
            track_path = export_session.start_track(
                uid,
                metadata['genre_sub'],
                metadata['bpm'],
                metadata['key']
            )
            progress_bar.progress(10)
            
            # Build stems manifest
            stems_manifest = []
            audio_count = 0
            midi_count = 0
            
            # Process each stem
            for i, (original_idx, pair) in enumerate(active_pairs):
                progress = 10 + int((i / total_stems) * 80)
                progress_bar.progress(progress)
                status_text.text(f"Processing {i+1}/{total_stems}: {pair.audio.filename}")
                
                # Get labels
                group, instrument, layer = st.session_state.stem_labels[pair.audio.filename]
                
                # Get MIDI
                midi_path = None
                if pair.audio.filename in st.session_state.manual_overrides:
                    override_midi = st.session_state.manual_overrides[pair.audio.filename]
                    midi_path = override_midi.path if override_midi else None
                elif pair.midi:
                    midi_path = pair.midi.path
                
                # V1.1: Full Track Mode vs Loop Slicer
                if st.session_state.enable_slicer:
                    # Use slicer
                    sliced_audio, sr, sliced_midi = slicer.slice_pair(
                        pair.audio.path,
                        midi_path,
                        start_bars=st.session_state.slice_settings['start_bars'],
                        end_bars=st.session_state.slice_settings['end_bars'],
                        tempo=metadata['bpm']
                    )
                    sample_type = "loop"
                else:
                    # Full Track Mode - no slicing
                    audio_data, sr = audio_proc.load_audio(pair.audio.path)
                    # Just resample if needed
                    if sr != config.DEFAULT_SAMPLE_RATE:
                        audio_data = audio_proc.resample_audio(audio_data, sr, config.DEFAULT_SAMPLE_RATE)
                        sr = config.DEFAULT_SAMPLE_RATE
                    sliced_audio = audio_data
                    sliced_midi = midi_path  # Use original MIDI
                    sample_type = "full_track"
                
                # Export
                export_session.export_stem(sliced_audio, sr, sliced_midi, uid, group, instrument, layer)
                
                audio_count += 1
                if sliced_midi:
                    midi_count += 1
                
                # Build stem manifest entry (V1.1)
                validator = StemValidator()
                is_mono = validator.should_force_mono(group, instrument)
                
                stem_entry = {
                    "filename": f"{uid}_{group.lower()}_{instrument.lower()}_{layer.lower()}.wav",
                    "group": group.lower(),
                    "instrument": instrument.lower(),
                    "layer": layer.lower(),
                    "type": sample_type,
                    "channels": 1 if is_mono else 2
                }
                
                if sliced_midi:
                    stem_entry["midi_pair"] = f"{uid}_midi_{group.lower()}_{instrument.lower()}.mid"
                
                stems_manifest.append(stem_entry)
            
            # Generate metadata (V1.1 - Schema V2)
            status_text.text("Generating metadata...")
            progress_bar.progress(95)
            
            track_metadata = metadata_gen.create_metadata(
                uid=uid,
                original_title=metadata['title'],
                original_folder=Path(st.session_state.source_dir).name,
                bpm=metadata['bpm'],
                key=metadata['key'],
                genre_parent=metadata['genre_parent'],
                genre_sub=metadata['genre_sub'],
                audio_count=audio_count,
                midi_count=midi_count,
                vocal_rights=st.session_state.vocal_rights,
                energy_level=metadata['energy_level'],
                mood=metadata['mood'],
                stems_manifest=stems_manifest,
                contains_ai=metadata.get('contains_ai', False),
                app_version="v1.1"
            )
            
            # Save metadata
            import json
            metadata_path = track_path / "Metadata" / f"{uid}_info.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(track_metadata, f, indent=2)
            
            # V1.3 FIX #3: Save lyrics file if uploaded
            if st.session_state.lyrics_file is not None:
                status_text.text("Saving lyrics...")
                lyrics_path = track_path / "Metadata" / f"{uid}_lyrics.txt"
                
                # Extract text based on file type
                lyrics_content = ""
                file_extension = st.session_state.lyrics_file.name.split('.')[-1].lower()
                
                if file_extension == "txt":
                    # Plain text file
                    lyrics_content = st.session_state.lyrics_file.getvalue().decode('utf-8')
                elif file_extension == "docx":
                    # Word document
                    try:
                        import docx2txt
                        lyrics_content = docx2txt.process(st.session_state.lyrics_file)
                    except ImportError:
                        st.warning("⚠️ docx2txt not installed. Install with: pip install docx2txt")
                        lyrics_content = "[DOCX file - could not extract text. Please install docx2txt]"
                elif file_extension == "pdf":
                    # PDF file
                    try:
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(st.session_state.lyrics_file)
                        lyrics_content = "\\n".join([page.extract_text() for page in pdf_reader.pages])
                    except ImportError:
                        st.warning("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
                        lyrics_content = "[PDF file - could not extract text. Please install PyPDF2]"
                
                # Save lyrics to file
                with open(lyrics_path, 'w', encoding='utf-8') as f:
                    f.write(lyrics_content)
                
                st.success(f"✅ Lyrics saved: {lyrics_path.name}")
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Export complete!")
            
            st.success(f"""
            ### ✅ Export Successful!
            
            - **UID:** {uid}
            - **Audio Files:** {audio_count}
            - **MIDI Files:** {midi_count}
            - **Mode:** {'Loop Slicer' if st.session_state.enable_slicer else 'Full Track'}
            - **Output:** `{track_path}`
            """)
            
            st.session_state.processing_complete = True
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())


def main():
    """Main application (V1.1)"""
    initialize_session_state()
    
    # Apply theme-specific CSS
    apply_theme_css(st.session_state.theme)
    
    # Header
    st.markdown('<p class="main-header">🎵 EDMGP Data Refinery V1.1</p>', unsafe_allow_html=True)
    st.markdown("**Audio/MIDI Dataset Processing | Full Track + Loop Slicer Modes**")
    
    # Render sidebar
    render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📂 Ingest & Pair", "🎨 Label Stems", "📦 Export"])
    
    with tab1:
        render_step1_ingestion()
    
    with tab2:
        render_step2_labeling()
    
    with tab3:
        render_step3_export()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>EDMGP Data Refinery V1.1 | All Features Implemented | December 2025</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
