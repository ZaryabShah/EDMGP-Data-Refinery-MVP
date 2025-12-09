"""
Demo script showing proper stem labeling for "Fall Down" track
This demonstrates how the Streamlit UI would allow users to label each stem
"""

import sys
sys.path.insert(0, r'c:\Users\zarya\Desktop\Python\Music_upwork_Josh')

from run_app import DataRefineryApp

# Initialize app
app = DataRefineryApp()

# Ingest files
app.ingest_directory(
    source_dir=r"c:\Users\zarya\Desktop\Python\Music_upwork_Josh\Raw_input_sample\Fall Down",
    vocal_rights="Royalty_Free"
)

# Define proper stem labels (this would come from UI dropdowns)
stem_labels = {
    # Master/Mix files
    "Fall Down (Master).wav": ("mix", "master", "main"),
    "Fall Down (Instrumental Master).wav": ("mix", "instrumental", "main"),
    "Fall Down (Mixdown).wav": ("mix", "premaster", "main"),
    "Fall Down (Instrumental Mix).wav": ("mix", "instrumental", "main"),
    
    # Bass stems
    "_ bass 1.wav": ("bass", "sub", "main"),
    "_ bass 2.wav": ("bass", "mid_bass", "layer2"),
    "_ bass 3.wav": ("bass", "reese", "main"),
    "_ bass 4.wav": ("bass", "reese", "layer2"),
    "_ sub bass.wav": ("bass", "sub", "main"),
    "_ reese.wav": ("bass", "reese", "main"),
    "_ reese 2.wav": ("bass", "reese", "layer2"),
    
    # Drums
    "_ Kick&Snare.wav": ("drums", "drum_loop", "main"),
    "_ clap.wav": ("drums", "clap", "main"),
    "_ snare build.wav": ("drums", "snare", "roll"),
    "_ ochestral drums.wav": ("drums", "orchestral", "loop"),
    
    # Cymbals
    "_ cymbal loop.wav": ("drums", "crash", "loop"),
    "_ cymbal loop 2.wav": ("drums", "crash", "layer2"),
    "_ cymbal loop 3.wav": ("drums", "crash", "layer3"),
    "_ cymbal loop 4.wav": ("drums", "crash", "layer4"),
    
    # Synth
    "_ arp.wav": ("synth", "arp", "main"),
    
    # FX
    "_ ambience fx.wav": ("fx", "ambience", "main"),
    "_ ambience fx 3.wav": ("fx", "ambience", "layer2"),
    "_ texture fx.wav": ("fx", "ambience", "texture"),
    "_ impact.wav": ("fx", "impact", "main"),
    "_ reverse fx.wav": ("fx", "reverse", "main"),
    "_ reverse kick.wav": ("fx", "reverse_kick", "main"),
    "_ riser 2.wav": ("fx", "riser", "main"),
}

# Process track with proper labels
app.process_track(
    output_dir=r"c:\Users\zarya\Desktop\Python\Music_upwork_Josh\Clean_Dataset_Staging",
    track_title="Fall Down",
    genre="trap",
    bpm=145,
    key="Fmin",
    vocal_rights="Royalty_Free",
    energy_level=5,
    mood=["aggressive", "dark"],
    start_bars=0,
    end_bars=16,
    stem_labels=stem_labels
)

print("\n✅ Demo complete!")
print("Check output in: Clean_Dataset_Staging/")
