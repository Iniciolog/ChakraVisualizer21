import os
import base64
from pydub import AudioSegment
import io
import numpy as np

def get_sound_html(chakra_name, volume=0.5):
    """
    Generate HTML audio tag with embedded audio data for a specific chakra
    
    Parameters:
    chakra_name (str): Name of the chakra (e.g., 'Root', 'Heart')
    volume (float): Volume level between 0.0 and 1.0
    
    Returns:
    str: HTML string containing the audio element
    """
    # Sound files should be in the sounds directory
    # If the sound file doesn't exist, generate one
    sound_path = f"sounds/{chakra_name.lower()}_tone.mp3"
    
    if not os.path.exists(sound_path):
        # Generate a sound if it doesn't exist
        sound = generate_chakra_sound(chakra_name)
        sound.export(sound_path, format="mp3")
    
    # Read the sound file and encode it
    data = open(sound_path, "rb").read()
    encoded = base64.b64encode(data).decode()
    
    # Create HTML with audio controls and autoplay option
    audio_html = f"""
    <audio id="chakra-sound-{chakra_name.lower()}" style="display:none;">
        <source src="data:audio/mp3;base64,{encoded}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    
    # Add JavaScript to control the audio
    audio_html += f"""
    <script>
        // Function to control sound playback
        function setupChakraSound{chakra_name.replace(" ", "")}() {{
            const audio = document.getElementById('chakra-sound-{chakra_name.lower()}');
            if (audio) {{
                audio.volume = {volume};
                
                // Add this audio element to the global audio collection
                if (!window.chakraSounds) {{
                    window.chakraSounds = {{}};
                }}
                window.chakraSounds['{chakra_name.lower()}'] = audio;
            }}
        }}
        
        // Initialize on load
        if (document.readyState === 'complete') {{
            setupChakraSound{chakra_name.replace(" ", "")}();
        }} else {{
            document.addEventListener('DOMContentLoaded', setupChakraSound{chakra_name.replace(" ", "")});
        }}
    </script>
    """
    
    return audio_html

def generate_chakra_sound(chakra_name):
    """
    Generate a sound file for a specific chakra based on its traditional frequency
    
    Parameters:
    chakra_name (str): Name of the chakra
    
    Returns:
    AudioSegment: Pydub AudioSegment containing the generated sound
    """
    # Traditional frequencies associated with each chakra (Hz)
    frequencies = {
        "Root": 256,        # C (note: traditional is 396Hz, but using lower for audibility)
        "Sacral": 288,      # D (note: traditional is 417Hz, but using lower for audibility)
        "Solar Plexus": 320, # E (note: traditional is 528Hz, but using lower for audibility)
        "Heart": 341,       # F (note: traditional is 639Hz, but using lower for audibility)
        "Throat": 384,      # G (note: traditional is 741Hz, but using lower for audibility)
        "Third Eye": 426,   # A (note: traditional is 852Hz, but using lower for audibility)
        "Crown": 480        # B (note: traditional is 963Hz, but using lower for audibility)
    }
    
    # If chakra name is not found, default to C (256Hz)
    frequency = frequencies.get(chakra_name, 256)
    
    # Generate a sine wave tone at the chakra frequency
    sample_rate = 44100  # CD quality
    duration_ms = 10000  # 10 seconds of sound
    
    # Generate the sine wave
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
    tone = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Add subtle overtones for richness
    tone += 0.15 * np.sin(2 * np.pi * (frequency * 2) * t)
    tone += 0.08 * np.sin(2 * np.pi * (frequency * 3) * t)
    
    # Apply a soft envelope to the sound (avoid clicks)
    envelope = np.ones_like(tone)
    attack_samples = int(0.05 * sample_rate)  # 50ms attack
    decay_samples = int(0.1 * sample_rate)    # 100ms decay
    
    # Attack (fade in)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay (fade out)
    envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
    
    # Apply envelope
    tone = tone * envelope
    
    # Convert to 16-bit signed integers
    tone = np.int16(tone * 32767)
    
    # Create an in-memory file-like object
    buffer = io.BytesIO()
    
    # Convert the NumPy array to raw audio bytes
    buffer.write(tone.tobytes())
    buffer.seek(0)
    
    # Create an AudioSegment from the raw audio
    sound = AudioSegment(
        data=buffer.read(),
        sample_width=2,  # 16-bit = 2 bytes
        frame_rate=sample_rate,
        channels=1       # Mono
    )
    
    # Add a subtle reverb effect by creating a delayed version and mixing it
    delayed = sound.fade_in(300).fade_out(300)._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * 0.994)  # Slightly slower for chorus effect
    }).fade_in(300).fade_out(300)
    
    sound = sound.overlay(delayed - 12)  # -12dB quieter for the reverb
    
    return sound

def get_sound_control_js():
    """
    Generate JavaScript to control all chakra sounds on the page
    
    Returns:
    str: HTML/JS string with sound control functions
    """
    return """
    <script>
        // Master control for chakra sounds
        function controlChakraSounds(chakraName, action) {
            if (!window.chakraSounds) return;
            
            // Get the specific chakra sound
            const sound = window.chakraSounds[chakraName.toLowerCase()];
            if (!sound) return;
            
            // Perform the requested action
            if (action === 'play') {
                // Stop any other playing sounds first
                for (let name in window.chakraSounds) {
                    if (name !== chakraName.toLowerCase()) {
                        window.chakraSounds[name].pause();
                        window.chakraSounds[name].currentTime = 0;
                    }
                }
                // Play this sound
                sound.currentTime = 0;  // Start from beginning
                sound.loop = true;      // Loop the sound
                sound.play();
            } else if (action === 'stop') {
                sound.pause();
                sound.currentTime = 0;
            } else if (action === 'setVolume') {
                sound.volume = arguments[2] || 0.5;  // Third argument as volume
            }
        }
        
        // Stop all sounds
        function stopAllChakraSounds() {
            if (!window.chakraSounds) return;
            
            for (let name in window.chakraSounds) {
                window.chakraSounds[name].pause();
                window.chakraSounds[name].currentTime = 0;
            }
        }
    </script>
    """

def inject_sound_setup():
    """
    Injects all necessary HTML and JavaScript for the chakra sound system
    
    Returns:
    str: Complete HTML string with all audio elements and control scripts
    """
    # Start with the master control script
    html = get_sound_control_js()
    
    # Add all the individual chakra sounds
    chakras = ["Root", "Sacral", "Solar Plexus", "Heart", "Throat", "Third Eye", "Crown"]
    for chakra in chakras:
        html += get_sound_html(chakra)
    
    return html