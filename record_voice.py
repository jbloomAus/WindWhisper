import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pynput import keyboard
import time

def record_voice(filename="output.wav", sample_rate=16000):
    # Initialize recording flag
    recording = True
    audio_chunks = []
    
    # Callback function to store audio chunks
    def callback(indata, frames, time, status):
        if status:
            print('Error:', status)
        if recording:
            audio_chunks.append(indata.copy())
    
    def on_press(key):
        nonlocal recording
        if key == keyboard.Key.esc:
            recording = False
            return False  # Stops the listener
    
    print("Recording... Press 'Esc' to stop.")
    
    # Start recording stream
    stream = sd.InputStream(samplerate=sample_rate, channels=1, callback=callback)
    with stream:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
        stream.stop()
    
    if audio_chunks:
        # Combine all audio chunks
        audio_data = np.concatenate(audio_chunks)
        # Save to WAV file
        write(filename, sample_rate, audio_data)
        print(f"Recording saved to {filename}")
    else:
        print("No audio recorded")

if __name__ == "__main__":
    print("Starting recording...")
    record_voice()