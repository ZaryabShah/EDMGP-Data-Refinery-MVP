"""
EDMGP Data Refinery App - Streamlit UI
Main application interface for audio/MIDI dataset processing
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

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from ingestion import FileIngester
from audio_processing import AudioProcessor, MIDIProcessor, AlignedSlicer
from metadata import MetadataGenerator, StemValidator
from export import ExportSession

# Page configuration
st.set_page_config(
    page_title="EDMGP Data Refinery",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .stem-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'ingester' not in st.session_state:
        st.session_state.ingester = None
    if 'source_dir' not in st.session_state:
        st.session_state.source_dir = None
    if 'vocal_rights' not in st.session_state:
        st.session_state.vocal_rights = "Exclusive"
    if 'stem_labels' not in st.session_state:
        st.session_state.stem_labels = {}
    if 'current_stem_index' not in st.session_state:
        st.session_state.current_stem_index = 0
    if 'export_session' not in st.session_state:
        st.session_state.export_session = None
    if 'track_metadata' not in st.session_state:
        st.session_state.track_metadata = {}
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'manual_overrides' not in st.session_state:
        st.session_state.manual_overrides = {}
    if 'slice_settings' not in st.session_state:
        st.session_state.slice_settings = {'start_bars': 0, 'end_bars': 16}


def plot_waveform_with_grid(audio_path, midi_path=None, bpm=None, start_bars=0, end_bars=16):
    """
    Plot audio waveform with optional beat grid overlay
    
    Args:
        audio_path: Path to audio file
        midi_path: Optional path to MIDI file
        bpm: BPM for beat grid (detected if not provided)
        start_bars: Start bar for visualization
        end_bars: End bar for visualization
    
    Returns:
        matplotlib figure
    """
    # Load audio
    audio_proc = AudioProcessor()
    audio_data, sr = audio_proc.load_audio(Path(audio_path))
    
    # Convert to mono for visualization
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
    
    # Calculate time range for bars
    bar_duration = (60 / bpm) * 4  # 4/4 time signature
    start_time = start_bars * bar_duration
    end_time = end_bars * bar_duration
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 4))
    
    # Plot waveform
    librosa.display.waveshow(audio_mono, sr=sr, ax=ax, alpha=0.6)
    
    # Add beat grid
    beat_times = np.arange(start_time, min(end_time, len(audio_mono)/sr), bar_duration)
    for i, beat_time in enumerate(beat_times):
        ax.axvline(x=beat_time, color='red', linestyle='--', alpha=0.5, linewidth=1)
        ax.text(beat_time, ax.get_ylim()[1] * 0.9, f'Bar {start_bars + i}', 
                rotation=90, verticalalignment='top', fontsize=8, color='red')
    
    # Highlight selection range
    ax.axvspan(start_time, min(end_time, len(audio_mono)/sr), 
               alpha=0.2, color='green', label='Selected Range')
    
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Waveform with Beat Grid (BPM: {bpm:.1f})')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def render_sidebar():
    """Render sidebar with configuration and status"""
    with st.sidebar:
        st.markdown('<p class="main-header">⚙️ Configuration</p>', unsafe_allow_html=True)
        
        # Vocal Rights Toggle
        st.markdown("### Vocal Rights Gate")
        vocal_rights = st.radio(
            "Contains Exclusive Vocals?",
            options=["Exclusive", "Royalty_Free"],
            index=0 if st.session_state.vocal_rights == "Exclusive" else 1,
            help="If Royalty_Free, vocal stems will be automatically excluded from the dataset"
        )
        st.session_state.vocal_rights = vocal_rights
        
        if vocal_rights == "Royalty_Free":
            st.markdown('<div class="warning-box">⚠️ Royalty-free mode: Vocal stems will be excluded</div>', 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Track Metadata
        st.markdown("### Track Metadata")
        
        track_title = st.text_input("Track Title", value="", placeholder="Enter track name")
        
        genre = st.selectbox(
            "Genre",
            options=config.GENRES,
            help="Select the genre from the taxonomy"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            bpm = st.number_input("BPM", min_value=40, max_value=300, value=140, step=1)
        with col2:
            key = st.text_input("Key", value="Cmin", placeholder="e.g., Cmin, Fmaj")
        
        energy_level = st.slider("Energy Level", min_value=1, max_value=5, value=3)
        
        mood_options = config.MOODS
        moods = st.multiselect(
            "Mood Tags (max 2)",
            options=mood_options,
            max_selections=2,
            help="Select up to 2 mood tags"
        )
        
        # Store metadata in session state
        st.session_state.track_metadata = {
            'title': track_title,
            'genre': genre.lower() if genre else None,
            'bpm': bpm,
            'key': key,
            'energy_level': energy_level,
            'mood': [m.lower() for m in moods]
        }
        
        st.markdown("---")
        
        # Status indicators
        st.markdown("### Status")
        
        if st.session_state.ingester:
            num_pairs = len(st.session_state.ingester.pairs)
            num_labeled = len(st.session_state.stem_labels)
            
            st.metric("Total Stems", num_pairs)
            st.metric("Labeled Stems", num_labeled)
            
            if num_labeled == num_pairs:
                st.markdown('<div class="success-box">✅ All stems labeled!</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="info-box">ℹ️ {num_pairs - num_labeled} stems remaining</div>', 
                           unsafe_allow_html=True)


def render_step1_ingestion():
    """Step 1: File Ingestion and Auto-Pairing"""
    st.markdown('<p class="sub-header">📂 Step 1: File Ingestion & Auto-Pairing</p>', 
                unsafe_allow_html=True)
    
    # Directory selection
    source_dir = st.text_input(
        "Source Directory",
        value=st.session_state.source_dir or "",
        placeholder="Enter or paste the path to your source folder",
        help="Folder containing .wav and .mid files"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        ingest_button = st.button("🔍 Scan & Pair Files", type="primary", use_container_width=True)
    
    if ingest_button and source_dir:
        st.session_state.source_dir = source_dir
        
        with st.spinner("Scanning files and auto-pairing..."):
            try:
                # Create ingester
                ingester = FileIngester(Path(source_dir))
                
                # Scan files
                ingester.scan_files()
                
                # Auto-pair
                ingester.auto_pair_files()
                
                # Filter vocals if needed
                if st.session_state.vocal_rights == "Royalty_Free":
                    # Remove vocal files from pairs
                    original_count = len(ingester.pairs)
                    ingester.pairs = [
                        pair for pair in ingester.pairs 
                        if not ingester.is_vocal_file(pair.audio)
                    ]
                    filtered_count = original_count - len(ingester.pairs)
                    
                    if filtered_count > 0:
                        st.warning(f"⚠️ Filtered out {filtered_count} vocal stem(s) (Royalty_Free mode)")
                
                # Store in session state
                st.session_state.ingester = ingester
                st.session_state.stem_labels = {}  # Reset labels
                st.session_state.current_stem_index = 0
                
                st.success(f"✅ Found {len(ingester.pairs)} file pair(s)")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during ingestion: {str(e)}")
    
    # Display pairing results
    if st.session_state.ingester:
        st.markdown("### Pairing Results")
        
        # Create dataframe for display
        pairs_data = []
        for i, pair in enumerate(st.session_state.ingester.pairs):
            pairs_data.append({
                '#': i + 1,
                'Audio File': pair.audio.filename,
                'MIDI File': pair.midi.filename if pair.midi else "❌ No MIDI",
                'Match Score': f"{pair.match_score}%" if pair.midi else "N/A",
                'Labeled': "✅" if pair.audio.filename in st.session_state.stem_labels else "⏳"
            })
        
        df = pd.DataFrame(pairs_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", len(st.session_state.ingester.pairs))
        with col2:
            midi_count = sum(1 for p in st.session_state.ingester.pairs if p.midi)
            st.metric("With MIDI", midi_count)
        with col3:
            no_midi_count = sum(1 for p in st.session_state.ingester.pairs if not p.midi)
            st.metric("Without MIDI", no_midi_count)


def render_step2_labeling():
    """Step 2: Stem Labeling with Waveform Visualization"""
    st.markdown('<p class="sub-header">🎨 Step 2: Stem Labeling & Visualization</p>', 
                unsafe_allow_html=True)
    
    if not st.session_state.ingester:
        st.info("👆 Please complete Step 1 first: Ingest files")
        return
    
    pairs = st.session_state.ingester.pairs
    
    if not pairs:
        st.warning("No files to label")
        return
    
    # Stem navigation
    total_stems = len(pairs)
    current_idx = st.session_state.current_stem_index
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", disabled=(current_idx == 0), use_container_width=True):
            st.session_state.current_stem_index = max(0, current_idx - 1)
            st.rerun()
    
    with col3:
        st.markdown(f"<h3 style='text-align: center;'>Stem {current_idx + 1} of {total_stems}</h3>", 
                   unsafe_allow_html=True)
    
    with col5:
        if st.button("Next ➡️", disabled=(current_idx >= total_stems - 1), use_container_width=True):
            st.session_state.current_stem_index = min(total_stems - 1, current_idx + 1)
            st.rerun()
    
    # Current stem
    current_pair = pairs[current_idx]
    
    # File information
    st.markdown("### Current File")
    st.markdown(f'<div class="stem-card"><strong>Audio:</strong> {current_pair.audio.filename}</div>', 
               unsafe_allow_html=True)
    
    if current_pair.midi:
        st.markdown(f'<div class="stem-card"><strong>MIDI:</strong> {current_pair.midi.filename} (Match: {current_pair.match_score}%)</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">⚠️ No MIDI file paired</div>', unsafe_allow_html=True)
    
    # Waveform visualization
    st.markdown("### Waveform with Beat Grid")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("#### Slice Settings")
        start_bars = st.number_input(
            "Start Bar", 
            min_value=0, 
            max_value=64, 
            value=st.session_state.slice_settings.get('start_bars', 0), 
            step=1,
            key=f"start_bars_{current_idx}"
        )
        end_bars = st.number_input(
            "End Bar", 
            min_value=1, 
            max_value=128, 
            value=st.session_state.slice_settings.get('end_bars', 16), 
            step=1,
            key=f"end_bars_{current_idx}"
        )
        
        # Update slice settings
        st.session_state.slice_settings = {
            'start_bars': start_bars,
            'end_bars': end_bars
        }
        
        if end_bars <= start_bars:
            st.error("End bar must be greater than start bar")
        
        # Duration info
        if st.session_state.track_metadata.get('bpm'):
            bpm = st.session_state.track_metadata['bpm']
            bar_duration = (60 / bpm) * 4
            total_duration = (end_bars - start_bars) * bar_duration
            st.info(f"⏱️ Duration: {total_duration:.2f}s\n({end_bars - start_bars} bars @ {bpm} BPM)")
    
    with col1:
        try:
            fig = plot_waveform_with_grid(
                current_pair.audio.path,
                current_pair.midi.path if current_pair.midi else None,
                bpm=st.session_state.track_metadata.get('bpm'),
                start_bars=start_bars,
                end_bars=end_bars
            )
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Error displaying waveform: {str(e)}")
    
    # Manual pairing override
    if st.checkbox("🔧 Manual Pairing Override", key=f"manual_override_{current_idx}"):
        st.markdown("### Override MIDI Pairing")
        st.info("Select a different MIDI file to pair with this audio file, or remove the pairing")
        
        # Get all available MIDI files
        if st.session_state.ingester.midi_files:
            midi_options = ["❌ No MIDI"] + [m.filename for m in st.session_state.ingester.midi_files]
            
            current_midi = current_pair.midi.filename if current_pair.midi else "❌ No MIDI"
            current_idx_midi = midi_options.index(current_midi) if current_midi in midi_options else 0
            
            selected_midi = st.selectbox(
                "MIDI File",
                options=midi_options,
                index=current_idx_midi,
                key=f"midi_override_{current_idx}"
            )
            
            if st.button("Apply Override", key=f"apply_override_{current_idx}"):
                if selected_midi == "❌ No MIDI":
                    st.session_state.manual_overrides[current_pair.audio.filename] = None
                    st.success("✅ MIDI pairing removed")
                else:
                    # Find the MIDI file
                    midi_file = next((m for m in st.session_state.ingester.midi_files if m.filename == selected_midi), None)
                    if midi_file:
                        st.session_state.manual_overrides[current_pair.audio.filename] = midi_file
                        st.success(f"✅ Paired with: {selected_midi}")
                
                st.rerun()
        else:
            st.warning("No MIDI files available for pairing")
    
    # Labeling interface
    st.markdown("### Label This Stem")
    
    # Check if already labeled
    existing_label = st.session_state.stem_labels.get(current_pair.audio.filename)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        group = st.selectbox(
            "Group",
            options=config.GROUPS,
            index=config.GROUPS.index(existing_label[0]) if existing_label else 0,
            key=f"group_{current_idx}"
        )
    
    with col2:
        # Get instruments for selected group
        instruments = config.INSTRUMENTS.get(group, [])
        instrument = st.selectbox(
            "Instrument",
            options=instruments,
            index=instruments.index(existing_label[1]) if existing_label and existing_label[1] in instruments else 0,
            key=f"instrument_{current_idx}"
        )
    
    with col3:
        layer = st.selectbox(
            "Layer",
            options=config.LAYERS,
            index=config.LAYERS.index(existing_label[2]) if existing_label else 0,
            key=f"layer_{current_idx}"
        )
    
    # Validation and helper info
    validator = StemValidator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Check mono/stereo requirement
        force_mono = validator.should_force_mono(group, instrument)
        if force_mono:
            st.info(f"ℹ️ This stem will be converted to **MONO** (Group: {group}, Instrument: {instrument})")
        else:
            st.info(f"ℹ️ This stem will remain **STEREO**")
    
    with col2:
        # Check MIDI requirement
        requires_midi = validator.requires_midi(group)
        if requires_midi and not current_pair.midi:
            st.warning(f"⚠️ {group} stems typically require MIDI pairing!")
    
    # Save button
    if st.button("💾 Save Label", type="primary", use_container_width=True):
        # Normalize labels
        normalized_group = config.normalize_group(group)
        normalized_instrument = config.normalize_instrument(instrument)
        normalized_layer = config.normalize_layer(layer)
        
        # Store label
        st.session_state.stem_labels[current_pair.audio.filename] = (
            normalized_group,
            normalized_instrument,
            normalized_layer
        )
        
        st.success(f"✅ Saved: {normalized_group}/{normalized_instrument}/{normalized_layer}")
        
        # Auto-advance to next unlabeled stem
        for i in range(current_idx + 1, total_stems):
            if pairs[i].audio.filename not in st.session_state.stem_labels:
                st.session_state.current_stem_index = i
                st.rerun()
                return
        
        # If no unlabeled stems found, stay on current
        st.info("All stems have been labeled!")


def render_step3_export():
    """Step 3: Export and Generate Dataset"""
    st.markdown('<p class="sub-header">📦 Step 3: Export Dataset</p>', 
                unsafe_allow_html=True)
    
    if not st.session_state.ingester:
        st.info("👆 Please complete Step 1 first: Ingest files")
        return
    
    total_stems = len(st.session_state.ingester.pairs)
    labeled_stems = len(st.session_state.stem_labels)
    
    # Check if all stems are labeled
    if labeled_stems < total_stems:
        st.warning(f"⚠️ Only {labeled_stems} of {total_stems} stems are labeled. Please label all stems before exporting.")
        return
    
    # Export configuration
    st.markdown("### Export Configuration")
    
    output_dir = st.text_input(
        "Output Directory",
        value="Clean_Dataset_Staging",
        help="Directory where the processed dataset will be saved"
    )
    
    # Validate track metadata
    metadata = st.session_state.track_metadata
    
    if not metadata.get('title'):
        st.error("❌ Please enter a track title in the sidebar")
        return
    
    # Display export summary
    st.markdown("### Export Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stems", total_stems)
    with col2:
        midi_count = sum(1 for p in st.session_state.ingester.pairs if p.midi)
        st.metric("With MIDI", midi_count)
    with col3:
        st.metric("Output Format", "44.1kHz / 24-bit WAV")
    
    # Show metadata preview
    with st.expander("📄 View Metadata Preview"):
        metadata_gen = MetadataGenerator()
        
        preview_metadata = {
            "uid": "GP_XXXXX (auto-generated)",
            "original_track_title": metadata['title'],
            "bpm": metadata['bpm'],
            "key": metadata['key'],
            "genre": metadata['genre'],
            "vocal_rights": st.session_state.vocal_rights.lower().replace('_', ''),
            "energy_level": metadata['energy_level'],
            "mood": metadata['mood'],
            "tech_specs": {
                "sample_rate": 44100,
                "bit_depth": 24
            }
        }
        
        st.json(preview_metadata)
    
    # Export button
    st.markdown("---")
    
    if st.button("🚀 Process & Export Dataset", type="primary", use_container_width=True):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize processors
            slicer = AlignedSlicer()
            metadata_gen = MetadataGenerator()
            export_session = ExportSession(output_dir)
            
            # Start batch
            status_text.text("Creating batch directory...")
            batch_path = export_session.start_batch()
            progress_bar.progress(5)
            
            # Generate UID
            uid = metadata_gen.get_next_uid(Path(output_dir))
            
            # Create track directory
            status_text.text("Creating track directory...")
            track_path = export_session.start_track(
                uid,
                metadata['genre'],
                metadata['bpm'],
                metadata['key']
            )
            progress_bar.progress(10)
            
            # Process stems
            audio_count = 0
            midi_count = 0
            
            for i, pair in enumerate(st.session_state.ingester.pairs):
                progress = 10 + int((i / total_stems) * 80)
                progress_bar.progress(progress)
                status_text.text(f"Processing stem {i+1}/{total_stems}: {pair.audio.filename}")
                
                # Get labels
                group, instrument, layer = st.session_state.stem_labels[pair.audio.filename]
                
                # Check for manual override
                midi_path = None
                if pair.audio.filename in st.session_state.manual_overrides:
                    override_midi = st.session_state.manual_overrides[pair.audio.filename]
                    midi_path = override_midi.path if override_midi else None
                elif pair.midi:
                    midi_path = pair.midi.path
                
                # Slice audio and MIDI
                sliced_audio, sample_rate, sliced_midi = slicer.slice_pair(
                    pair.audio.path,
                    midi_path,
                    start_bars=st.session_state.slice_settings.get('start_bars', 0),
                    end_bars=st.session_state.slice_settings.get('end_bars', 16),
                    tempo=metadata['bpm']
                )
                
                # Export stem
                export_session.export_stem(
                    sliced_audio,
                    sample_rate,
                    sliced_midi,
                    uid,
                    group,
                    instrument,
                    layer
                )
                
                audio_count += 1
                if sliced_midi:
                    midi_count += 1
            
            # Generate metadata
            status_text.text("Generating metadata...")
            progress_bar.progress(95)
            
            track_metadata = metadata_gen.create_metadata(
                uid=uid,
                original_title=metadata['title'],
                bpm=metadata['bpm'],
                key=metadata['key'],
                genre=metadata['genre'],
                audio_count=audio_count,
                midi_count=midi_count,
                vocal_rights=st.session_state.vocal_rights,
                energy_level=metadata['energy_level'],
                mood=metadata['mood']
            )
            
            export_session.finalize_track(track_metadata)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Export complete!")
            
            st.success(f"""
            ✅ **Export Successful!**
            
            - **UID:** {uid}
            - **Audio Files:** {audio_count}
            - **MIDI Files:** {midi_count}
            - **Location:** {track_path}
            """)
            
            st.session_state.processing_complete = True
            
            # Show output location
            st.markdown(f'<div class="success-box">📁 Output: <code>{track_path}</code></div>', 
                       unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def main():
    """Main application"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<p class="main-header">🎵 EDMGP Data Refinery</p>', unsafe_allow_html=True)
    st.markdown("**Audio/MIDI Dataset Processing for Machine Learning**")
    
    # Render sidebar
    render_sidebar()
    
    # Main content tabs
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
        <small>EDMGP Data Refinery v1.0 | Backend MVP Complete | Streamlit UI Phase 2</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
