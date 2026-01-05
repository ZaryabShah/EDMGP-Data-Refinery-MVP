"""
Audio and MIDI processing module
Handles waveform visualization, slicing, and alignment
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, List
import pretty_midi
from dataclasses import dataclass
import config


@dataclass
class AudioInfo:
    """Audio file information"""
    sample_rate: int
    duration: float
    channels: int
    samples: int


@dataclass
class MIDIInfo:
    """MIDI file information"""
    duration: float
    tempo: float
    time_signature: Tuple[int, int]
    has_tempo_map: bool


class AudioProcessor:
    """Handles audio file loading, analysis, and processing"""
    
    def __init__(self):
        self.audio_data = None
        self.sample_rate = None
        self.duration = None
        self.channels = None
    
    def load_audio(self, audio_path: Path) -> Tuple[np.ndarray, int]:
        """
        Load audio file and resample to standard sample rate if needed
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        # Load with soundfile (preserves multi-channel)
        audio_data, sample_rate = sf.read(str(audio_path), dtype='float32')
        
        # Resample to default sample rate if different
        if sample_rate != config.DEFAULT_SAMPLE_RATE:
            print(f"  ℹ Resampling from {sample_rate} Hz to {config.DEFAULT_SAMPLE_RATE} Hz")
            
            # Handle mono vs stereo
            if audio_data.ndim == 1:
                # Mono audio
                audio_data = librosa.resample(
                    audio_data,
                    orig_sr=sample_rate,
                    target_sr=config.DEFAULT_SAMPLE_RATE
                )
            else:
                # Stereo/multi-channel - resample each channel
                resampled_channels = []
                for channel_idx in range(audio_data.shape[1]):
                    resampled_channel = librosa.resample(
                        audio_data[:, channel_idx],
                        orig_sr=sample_rate,
                        target_sr=config.DEFAULT_SAMPLE_RATE
                    )
                    resampled_channels.append(resampled_channel)
                audio_data = np.column_stack(resampled_channels)
            
            sample_rate = config.DEFAULT_SAMPLE_RATE
        
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        
        # Determine number of channels
        if audio_data.ndim == 1:
            self.channels = 1
            self.duration = len(audio_data) / sample_rate
        else:
            self.channels = audio_data.shape[1]
            self.duration = audio_data.shape[0] / sample_rate
        
        return audio_data, sample_rate
    
    def get_audio_info(self, audio_path: Path) -> AudioInfo:
        """
        Get audio file information without loading full data
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioInfo object
        """
        info = sf.info(str(audio_path))
        
        return AudioInfo(
            sample_rate=info.samplerate,
            duration=info.duration,
            channels=info.channels,
            samples=info.frames
        )
    
    def get_mono_mix(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Convert stereo/multi-channel audio to mono for visualization
        
        Args:
            audio_data: Audio data array
            
        Returns:
            Mono audio array
        """
        if audio_data.ndim == 1:
            return audio_data
        else:
            # Average all channels
            return np.mean(audio_data, axis=1)
    
    def detect_bpm(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Detect BPM using librosa
        
        Args:
            audio_data: Audio data (mono or stereo)
            sample_rate: Sample rate
            
        Returns:
            Detected BPM
        """
        # Convert to mono if needed
        if audio_data.ndim > 1:
            audio_mono = self.get_mono_mix(audio_data)
        else:
            audio_mono = audio_data
        
        # Detect tempo
        tempo, _ = librosa.beat.beat_track(y=audio_mono, sr=sample_rate)
        
        return float(tempo)
    
    def slice_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        start_time: float,
        end_time: float
    ) -> np.ndarray:
        """
        Slice audio to specific time range (sample-accurate)
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Sliced audio data
        """
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)
        
        # Handle mono vs stereo
        if audio_data.ndim == 1:
            return audio_data[start_sample:end_sample]
        else:
            return audio_data[start_sample:end_sample, :]
    
    def convert_to_mono(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Convert audio to mono
        
        Args:
            audio_data: Audio data array
            
        Returns:
            Mono audio array
        """
        if audio_data.ndim == 1:
            return audio_data
        else:
            return np.mean(audio_data, axis=1)
    
    def resample_audio(
        self,
        audio_data: np.ndarray,
        orig_sr: int,
        target_sr: int
    ) -> np.ndarray:
        """
        Resample audio to target sample rate (backward-compatible helper)
        
        Args:
            audio_data: Audio data array
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio array
        """
        # No-op if already at target rate
        if orig_sr == target_sr:
            return audio_data
        
        # Handle mono vs stereo/multi-channel
        if audio_data.ndim == 1:
            # Mono: resample directly
            return librosa.resample(
                audio_data,
                orig_sr=orig_sr,
                target_sr=target_sr
            )
        else:
            # Stereo/multi-channel: resample each channel
            channels = []
            for c in range(audio_data.shape[1]):
                ch_resampled = librosa.resample(
                    audio_data[:, c],
                    orig_sr=orig_sr,
                    target_sr=target_sr
                )
                channels.append(ch_resampled)
            return np.column_stack(channels)
    
    def save_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        output_path: Path,
        bit_depth: int = 24
    ):
        """
        Save audio to file with format standardization
        
        V2.2: Enforces 44.1kHz / 16-bit PCM output for dataset uniformity
        Handles both mono and stereo/multi-channel audio properly
        
        Args:
            audio_data: Audio data to save (1D for mono, 2D for stereo)
            sample_rate: Sample rate (will be resampled to 44.1kHz if needed)
            output_path: Output file path
            bit_depth: Bit depth (kept for compatibility, but ignored)
        """
        # V2.2: Force standardization to 44.1kHz / 16-bit PCM
        target_sr = config.DEFAULT_SAMPLE_RATE  # 44100
        
        # 1) Resample to 44.1kHz if needed (handle stereo/multi-channel)
        if sample_rate != target_sr:
            if audio_data.ndim == 1:
                # Mono: resample directly
                audio_data = librosa.resample(
                    audio_data,
                    orig_sr=sample_rate,
                    target_sr=target_sr
                )
            else:
                # Stereo / multi-channel: resample each channel separately
                channels = []
                for c in range(audio_data.shape[1]):
                    ch_resampled = librosa.resample(
                        audio_data[:, c],
                        orig_sr=sample_rate,
                        target_sr=target_sr
                    )
                    channels.append(ch_resampled)
                audio_data = np.column_stack(channels)
            sample_rate = target_sr
        
        # 2) Normalize to [-1, 1] range for safe PCM_16 conversion
        max_val = float(np.max(np.abs(audio_data))) if audio_data.size > 0 else 0.0
        if max_val > 0:
            audio_data = audio_data / (max_val + 1e-8)  # Prevent clipping
        
        # 3) Save as 16-bit PCM (forced standardization)
        sf.write(
            str(output_path),
            audio_data,
            sample_rate,
            subtype='PCM_16'  # Always 16-bit PCM for dataset uniformity
        )


class MIDIProcessor:
    """Handles MIDI file loading, analysis, and processing"""
    
    def __init__(self):
        self.midi_data = None
        self.tempo = None
    
    def load_midi(self, midi_path: Path) -> pretty_midi.PrettyMIDI:
        """
        Load MIDI file
        
        Args:
            midi_path: Path to MIDI file
            
        Returns:
            PrettyMIDI object
        """
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        self.midi_data = midi_data
        
        return midi_data
    
    def get_midi_info(self, midi_path: Path) -> MIDIInfo:
        """
        Get MIDI file information
        
        Args:
            midi_path: Path to MIDI file
            
        Returns:
            MIDIInfo object
        """
        midi_data = pretty_midi.PrettyMIDI(str(midi_path))
        
        # Get tempo (use first tempo change or estimate)
        tempo = self.get_tempo(midi_data)
        
        # Get time signature (use first or default to 4/4)
        time_sig = self.get_time_signature(midi_data)
        
        # Check if has tempo map (multiple tempo changes)
        tempo_times, tempos = midi_data.get_tempo_changes()
        has_tempo_map = len(tempo_times) > 1
        
        # Warn if complex tempo map exists
        if has_tempo_map:
            print(f"  ⚠ MIDI has {len(tempo_times)} tempo changes (using first: {tempo:.1f} BPM)")
            print(f"    Note: Complex tempo maps are currently flattened to single tempo")
        
        return MIDIInfo(
            duration=midi_data.get_end_time(),
            tempo=tempo,
            time_signature=time_sig,
            has_tempo_map=has_tempo_map
        )
    
    def get_tempo(self, midi_data: pretty_midi.PrettyMIDI) -> float:
        """
        Get tempo from MIDI file
        
        Args:
            midi_data: PrettyMIDI object
            
        Returns:
            Tempo in BPM
        """
        tempo_changes = midi_data.get_tempo_changes()
        
        if len(tempo_changes[0]) > 0:
            # Return first tempo
            return float(tempo_changes[1][0])
        else:
            # Estimate tempo (default 120 BPM if can't determine)
            return 120.0
    
    def get_time_signature(self, midi_data: pretty_midi.PrettyMIDI) -> Tuple[int, int]:
        """
        Get time signature from MIDI file
        
        Args:
            midi_data: PrettyMIDI object
            
        Returns:
            Tuple of (numerator, denominator)
        """
        time_signatures = midi_data.time_signature_changes
        
        if time_signatures:
            ts = time_signatures[0]
            return (ts.numerator, ts.denominator)
        else:
            # Default to 4/4
            return (4, 4)
    
    def calculate_bar_duration(
        self,
        tempo: float,
        time_signature: Tuple[int, int] = (4, 4)
    ) -> float:
        """
        Calculate the duration of one bar in seconds
        
        Args:
            tempo: Tempo in BPM
            time_signature: Time signature (numerator, denominator)
            
        Returns:
            Bar duration in seconds
        """
        beats_per_bar = time_signature[0]
        seconds_per_beat = 60.0 / tempo
        bar_duration = beats_per_bar * seconds_per_beat
        
        return bar_duration
    
    def bars_to_seconds(
        self,
        num_bars: int,
        tempo: float,
        time_signature: Tuple[int, int] = (4, 4)
    ) -> float:
        """
        Convert bars to seconds
        
        Args:
            num_bars: Number of bars
            tempo: Tempo in BPM
            time_signature: Time signature
            
        Returns:
            Duration in seconds
        """
        bar_duration = self.calculate_bar_duration(tempo, time_signature)
        return num_bars * bar_duration
    
    def slice_midi(
        self,
        midi_data: pretty_midi.PrettyMIDI,
        start_time: float,
        end_time: float
    ) -> pretty_midi.PrettyMIDI:
        """
        Slice MIDI to specific time range and shift to start at 0
        
        Args:
            midi_data: PrettyMIDI object
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            New PrettyMIDI object with sliced content
        """
        # Create new MIDI object
        sliced_midi = pretty_midi.PrettyMIDI(initial_tempo=self.get_tempo(midi_data))
        
        # Copy time signature
        for ts in midi_data.time_signature_changes:
            if start_time <= ts.time <= end_time:
                new_ts = pretty_midi.TimeSignature(
                    ts.numerator,
                    ts.denominator,
                    ts.time - start_time
                )
                sliced_midi.time_signature_changes.append(new_ts)
        
        # Copy instruments with filtered notes
        for instrument in midi_data.instruments:
            new_instrument = pretty_midi.Instrument(
                program=instrument.program,
                is_drum=instrument.is_drum,
                name=instrument.name
            )
            
            # Filter and shift notes (including overlapping notes)
            for note in instrument.notes:
                # Skip notes that don't overlap with the time window
                # A note overlaps if its end is after the start AND its start is before the end
                if note.end <= start_time or note.start >= end_time:
                    continue
                
                # Clip the note to the time window and shift to start at 0
                new_start = max(note.start, start_time) - start_time
                new_end = min(note.end, end_time) - start_time
                
                # Skip if clipping resulted in zero-length note
                if new_end <= new_start:
                    continue
                
                new_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=new_start,
                    end=new_end
                )
                new_instrument.notes.append(new_note)
            
            # Only add instrument if it has notes
            if new_instrument.notes:
                sliced_midi.instruments.append(new_instrument)
        
        return sliced_midi
    
    def save_midi(self, midi_data: pretty_midi.PrettyMIDI, output_path: Path):
        """
        Save MIDI to file
        
        Args:
            midi_data: PrettyMIDI object
            output_path: Output file path
        """
        midi_data.write(str(output_path))


class AlignedSlicer:
    """Handles aligned slicing of audio and MIDI"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.midi_processor = MIDIProcessor()
    
    def slice_pair(
        self,
        audio_path: Path,
        midi_path: Optional[Path],
        start_bars: float,
        end_bars: float,
        tempo: Optional[float] = None,
        time_signature: Tuple[int, int] = (4, 4)
    ) -> Tuple[np.ndarray, int, Optional[pretty_midi.PrettyMIDI]]:
        """
        Slice audio and MIDI to the same bar range
        
        Args:
            audio_path: Path to audio file
            midi_path: Path to MIDI file (optional)
            start_bars: Start position in bars
            end_bars: End position in bars
            tempo: Tempo in BPM (from MIDI or detected)
            time_signature: Time signature
            
        Returns:
            Tuple of (sliced_audio, sample_rate, sliced_midi)
        """
        # Load audio
        audio_data, sample_rate = self.audio_processor.load_audio(audio_path)
        
        # Get tempo from MIDI if available, otherwise use provided or detect
        if midi_path and midi_path.exists():
            midi_data = self.midi_processor.load_midi(midi_path)
            tempo = self.midi_processor.get_tempo(midi_data)
            time_signature = self.midi_processor.get_time_signature(midi_data)
        elif tempo is None:
            # Detect tempo from audio
            tempo = self.audio_processor.detect_bpm(audio_data, sample_rate)
            print(f"Detected BPM: {tempo:.1f}")
        
        # Calculate time range
        start_time = self.midi_processor.bars_to_seconds(start_bars, tempo, time_signature)
        end_time = self.midi_processor.bars_to_seconds(end_bars, tempo, time_signature)
        
        print(f"Slicing from {start_bars} to {end_bars} bars ({start_time:.2f}s to {end_time:.2f}s)")
        
        # Slice audio
        sliced_audio = self.audio_processor.slice_audio(
            audio_data, sample_rate, start_time, end_time
        )
        
        # Slice MIDI if present
        sliced_midi = None
        if midi_path and midi_path.exists():
            sliced_midi = self.midi_processor.slice_midi(midi_data, start_time, end_time)
        
        return sliced_audio, sample_rate, sliced_midi


if __name__ == "__main__":
    # Test audio processing
    print("Audio/MIDI Processing Module")
    print("This module will be used by the main application")
