"""
Automated Test Suite for EDMGP Data Refinery MVP
Tests core functionality without requiring manual verification
"""

import sys
import os
import numpy as np
import pretty_midi
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from audio_processing import AudioProcessor, MIDIProcessor, AlignedSlicer
from metadata import MetadataGenerator, StemValidator
from ingestion import FileIngester, AudioFile, MIDIFile


class TestSuite:
    """Automated test suite for core functionality"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name: str, condition: bool, message: str = ""):
        """
        Run a single test
        
        Args:
            name: Test name
            condition: Boolean condition to check
            message: Optional failure message
        """
        if condition:
            print(f"  ✓ {name}")
            self.passed += 1
            self.tests.append((name, True, ""))
        else:
            print(f"  ✗ {name}: {message}")
            self.failed += 1
            self.tests.append((name, False, message))
    
    def report(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({100*self.passed/total if total > 0 else 0:.1f}%)")
        print(f"Failed: {self.failed}")
        print("="*60)
        
        if self.failed > 0:
            print("\n❌ SOME TESTS FAILED")
            return False
        else:
            print("\n✅ ALL TESTS PASSED")
            return True


def test_normalization():
    """Test taxonomy normalization helpers"""
    print("\n1. Testing Taxonomy Normalization")
    print("-" * 60)
    
    suite = TestSuite()
    
    # Test group normalization
    suite.test(
        "normalize_group: lowercase",
        config.normalize_group("drums") == "Drums",
        f"Expected 'Drums', got '{config.normalize_group('drums')}'"
    )
    
    suite.test(
        "normalize_group: uppercase",
        config.normalize_group("BASS") == "Bass",
        f"Expected 'Bass', got '{config.normalize_group('BASS')}'"
    )
    
    suite.test(
        "normalize_group: already correct",
        config.normalize_group("Synth") == "Synth"
    )
    
    # Test instrument normalization
    suite.test(
        "normalize_instrument: lowercase with underscore",
        config.normalize_instrument("sub_bass") == "Sub_Bass",
        f"Expected 'Sub_Bass', got '{config.normalize_instrument('sub_bass')}'"
    )
    
    suite.test(
        "normalize_instrument: spaces to underscores",
        config.normalize_instrument("hat closed") == "Hat_Closed",
        f"Expected 'Hat_Closed', got '{config.normalize_instrument('hat closed')}'"
    )
    
    suite.test(
        "normalize_instrument: single word",
        config.normalize_instrument("kick") == "Kick",
        f"Expected 'Kick', got '{config.normalize_instrument('kick')}'"
    )
    
    # Test layer normalization
    suite.test(
        "normalize_layer: lowercase",
        config.normalize_layer("main") == "Main"
    )
    
    suite.test(
        "normalize_layer: multi-word",
        config.normalize_layer("one_shot") == "One_Shot",
        f"Expected 'One_Shot', got '{config.normalize_layer('one_shot')}'"
    )
    
    return suite.report()


def test_midi_slicing():
    """Test MIDI slicing with overlapping notes"""
    print("\n2. Testing MIDI Slicing with Overlapping Notes")
    print("-" * 60)
    
    suite = TestSuite()
    
    # Create a synthetic MIDI file
    midi = pretty_midi.PrettyMIDI(initial_tempo=120)
    instrument = pretty_midi.Instrument(program=0)
    
    # Add notes with different overlap scenarios:
    # Note 1: Completely before window (0-1s, window 2-4s) - should be excluded
    instrument.notes.append(pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=1.0))
    
    # Note 2: Starts before, ends during (1-2.5s, window 2-4s) - should be clipped to 0-0.5s
    instrument.notes.append(pretty_midi.Note(velocity=100, pitch=62, start=1.0, end=2.5))
    
    # Note 3: Completely inside window (2.5-3.5s, window 2-4s) - should be 0.5-1.5s
    instrument.notes.append(pretty_midi.Note(velocity=100, pitch=64, start=2.5, end=3.5))
    
    # Note 4: Starts during, ends after (3.5-5s, window 2-4s) - should be 1.5-2.0s
    instrument.notes.append(pretty_midi.Note(velocity=100, pitch=65, start=3.5, end=5.0))
    
    # Note 5: Completely after window (5-6s, window 2-4s) - should be excluded
    instrument.notes.append(pretty_midi.Note(velocity=100, pitch=67, start=5.0, end=6.0))
    
    midi.instruments.append(instrument)
    
    # Slice MIDI from 2-4 seconds
    processor = MIDIProcessor()
    sliced = processor.slice_midi(midi, start_time=2.0, end_time=4.0)
    
    # Check results
    suite.test(
        "MIDI slicing: has instruments",
        len(sliced.instruments) > 0,
        "No instruments in sliced MIDI"
    )
    
    if len(sliced.instruments) > 0:
        notes = sliced.instruments[0].notes
        
        suite.test(
            "MIDI slicing: correct note count (3 overlapping notes)",
            len(notes) == 3,
            f"Expected 3 notes, got {len(notes)}"
        )
        
        if len(notes) == 3:
            # Check Note 2 (was 1-2.5s, should be 0-0.5s)
            suite.test(
                "MIDI slicing: overlapping note start time",
                abs(notes[0].start - 0.0) < 0.001,
                f"Expected start=0.0, got {notes[0].start}"
            )
            
            suite.test(
                "MIDI slicing: overlapping note end time",
                abs(notes[0].end - 0.5) < 0.001,
                f"Expected end=0.5, got {notes[0].end}"
            )
            
            # Check Note 3 (was 2.5-3.5s, should be 0.5-1.5s)
            suite.test(
                "MIDI slicing: contained note timing",
                abs(notes[1].start - 0.5) < 0.001 and abs(notes[1].end - 1.5) < 0.001,
                f"Expected 0.5-1.5, got {notes[1].start}-{notes[1].end}"
            )
            
            # Check Note 4 (was 3.5-5s, should be 1.5-2.0s)
            suite.test(
                "MIDI slicing: note ending after window",
                abs(notes[2].start - 1.5) < 0.001 and abs(notes[2].end - 2.0) < 0.001,
                f"Expected 1.5-2.0, got {notes[2].start}-{notes[2].end}"
            )
    
    return suite.report()


def test_stereo_mono_validation():
    """Test mono/stereo validation rules"""
    print("\n3. Testing Mono/Stereo Validation")
    print("-" * 60)
    
    suite = TestSuite()
    validator = StemValidator()
    
    # Test force mono instruments
    suite.test(
        "Force mono: Kick should be mono",
        validator.should_force_mono("Drums", "Kick"),
        "Kick should be forced to mono"
    )
    
    suite.test(
        "Force mono: Sub should be mono",
        validator.should_force_mono("Bass", "Sub"),
        "Sub should be forced to mono"
    )
    
    suite.test(
        "Force mono: Lead should be mono",
        validator.should_force_mono("Synth", "Lead"),
        "Lead should be forced to mono"
    )
    
    # Test keep stereo groups
    suite.test(
        "Keep stereo: FX group should be stereo",
        not validator.should_force_mono("FX", "Ambience"),
        "FX group should keep stereo"
    )
    
    suite.test(
        "Keep stereo: Mix group should be stereo",
        not validator.should_force_mono("Mix", "Master"),
        "Mix group should keep stereo"
    )
    
    # Test keep stereo instruments
    suite.test(
        "Keep stereo: Pad should be stereo",
        not validator.should_force_mono("Synth", "Pad"),
        "Pad should keep stereo"
    )
    
    suite.test(
        "Keep stereo: Crash should be stereo",
        not validator.should_force_mono("Drums", "Crash"),
        "Crash should keep stereo"
    )
    
    return suite.report()


def test_metadata_validation():
    """Test metadata generation and validation"""
    print("\n4. Testing Metadata Validation")
    print("-" * 60)
    
    suite = TestSuite()
    generator = MetadataGenerator()
    
    # Create valid metadata
    metadata = generator.create_metadata(
        uid="GP_00001",
        original_title="Test Track",
        bpm=140,
        key="Cmin",
        genre="techno",
        audio_count=10,
        midi_count=5,
        vocal_rights="Exclusive",
        energy_level=4,
        mood=["dark", "aggressive"]
    )
    
    # Validate
    errors = generator.validate_metadata(metadata)
    
    suite.test(
        "Metadata validation: valid metadata passes",
        len(errors) == 0,
        f"Validation failed: {errors}"
    )
    
    # Test invalid BPM
    metadata_invalid_bpm = generator.create_metadata(
        uid="GP_00002",
        original_title="Test",
        bpm=500,  # Too high
        key="Cmin",
        genre="techno",
        audio_count=5,
        midi_count=2,
        vocal_rights="Exclusive",
        energy_level=3,
        mood=["dark"]
    )
    
    errors_bpm = generator.validate_metadata(metadata_invalid_bpm)
    
    suite.test(
        "Metadata validation: invalid BPM fails",
        len(errors_bpm) > 0,
        "BPM validation should fail for BPM > 300"
    )
    
    # Test invalid genre
    metadata_invalid_genre = generator.create_metadata(
        uid="GP_00003",
        original_title="Test",
        bpm=140,
        key="Cmin",
        genre="invalid_genre",
        audio_count=5,
        midi_count=2,
        vocal_rights="Exclusive",
        energy_level=3,
        mood=["dark"]
    )
    
    errors_genre = generator.validate_metadata(metadata_invalid_genre)
    
    suite.test(
        "Metadata validation: invalid genre fails",
        len(errors_genre) > 0,
        "Genre validation should fail for invalid genre"
    )
    
    return suite.report()


def test_sample_rate_resampling():
    """Test sample rate resampling"""
    print("\n5. Testing Sample Rate Resampling")
    print("-" * 60)
    
    suite = TestSuite()
    processor = AudioProcessor()
    
    # Create synthetic audio at 48kHz
    sample_rate_48k = 48000
    duration = 1.0  # 1 second
    samples_48k = int(sample_rate_48k * duration)
    audio_48k = np.random.randn(samples_48k).astype(np.float32)
    
    # Save to temp file
    import soundfile as sf
    temp_path = Path("temp_test_audio_48k.wav")
    sf.write(str(temp_path), audio_48k, sample_rate_48k)
    
    # Load with processor (should resample to 44.1kHz)
    audio_resampled, sr_resampled = processor.load_audio(temp_path)
    
    suite.test(
        "Resampling: output is 44.1kHz",
        sr_resampled == config.DEFAULT_SAMPLE_RATE,
        f"Expected {config.DEFAULT_SAMPLE_RATE}, got {sr_resampled}"
    )
    
    suite.test(
        "Resampling: duration approximately preserved",
        abs(len(audio_resampled) / sr_resampled - duration) < 0.01,
        f"Duration changed significantly"
    )
    
    # Clean up
    temp_path.unlink()
    
    # Test audio already at 44.1kHz (should not resample)
    audio_44k = np.random.randn(44100).astype(np.float32)
    temp_path_44k = Path("temp_test_audio_44k.wav")
    sf.write(str(temp_path_44k), audio_44k, config.DEFAULT_SAMPLE_RATE)
    
    audio_no_resample, sr_no_resample = processor.load_audio(temp_path_44k)
    
    suite.test(
        "No resampling: 44.1kHz audio unchanged",
        sr_no_resample == config.DEFAULT_SAMPLE_RATE,
        f"Sample rate changed from {config.DEFAULT_SAMPLE_RATE}"
    )
    
    # Clean up
    temp_path_44k.unlink()
    
    return suite.report()


def run_all_tests():
    """Run all automated tests"""
    print("\n" + "="*60)
    print("EDMGP DATA REFINERY - AUTOMATED TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run all test modules
    results.append(test_normalization())
    results.append(test_midi_slicing())
    results.append(test_stereo_mono_validation())
    results.append(test_metadata_validation())
    results.append(test_sample_rate_resampling())
    
    # Overall summary
    print("\n" + "="*60)
    print("OVERALL TEST RESULTS")
    print("="*60)
    
    if all(results):
        print("✅ ALL TEST MODULES PASSED")
        return True
    else:
        print("❌ SOME TEST MODULES FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
