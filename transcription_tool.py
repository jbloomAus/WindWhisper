import sounddevice as sd
import numpy as np
import whisper
import pyperclip
from pynput import keyboard
from pynput.keyboard import Controller
import queue
import argparse
import sys
from playsound import playsound

class TranscriptionTool:
    def __init__(self, model_name="tiny"):
        # Initialize Whisper model (download on first run)
        self.model = whisper.load_model(model_name)
        self.recording = False
        self.audio_queue = queue.Queue()
        self.listener = None
        self.keyboard_controller = Controller()  # Add keyboard controller
        # Define sound file paths - you'll need to provide your own sound files
        self.start_sound = "sounds/start_recording.m4a"  # or .mp3
        self.stop_sound = "sounds/end_recording.m4a"   # or .mp3
        
    def record_audio(self):
        # Audio parameters
        sample_rate = 16000
        
        print("Recording... Press 'Esc' to stop.")
        self.recording = True
        
        def on_press(key):
            if key == keyboard.Key.esc:
                self.recording = False
                return False  # Stops the listener
        
        # Start recording
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=self.audio_callback):
            with keyboard.Listener(on_press=on_press) as listener:
                self.listener = listener
                listener.join()
                
        # Get all audio from queue
        audio_chunks = []
        while not self.audio_queue.empty():
            audio_chunks.append(self.audio_queue.get())
            
        if not audio_chunks:
            return None
            
        # Concatenate chunks and ensure float32 format
        audio = np.concatenate(audio_chunks)
        audio = audio.flatten().astype(np.float32)
        return audio
    
    def audio_callback(self, indata, frames, time, status):
        if status:
            print('Error:', status)
        if self.recording:
            self.audio_queue.put(indata.copy())
    
    def transcribe_audio(self, audio):
        # No need to save to file, we can process the audio directly
        # Pad or trim audio to fit 30 seconds
        audio = whisper.pad_or_trim(audio)
        
        # Create mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        
        # Detect language
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        print(f"Detected language: {detected_lang}")
        
        # Decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        return result.text.strip()
    
    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        print(f"Transcribed and copied to clipboard: {text}")
    
    def start(self):
        self.currently_pressed = set()
        self.setup_keyboard_listener()
        print("Transcription tool running. Press Ctrl+Space to start/stop recording.")
        print("Press Ctrl+Q to quit.")
        self.listener.start()
        self.listener.join()

    def setup_keyboard_listener(self):
        def on_press(key):
            try:
                # Change to Control + Space to toggle recording
                if key == keyboard.Key.space and keyboard.Key.ctrl in self.currently_pressed:
                    self.toggle_recording()
            except AttributeError:
                pass

        def on_release(key):
            try:
                if key in self.currently_pressed:
                    self.currently_pressed.remove(key)
            except KeyError:
                pass

        # Initialize set for tracking pressed keys
        self.currently_pressed = set()

        def on_press_track(key):
            self.currently_pressed.add(key)
            on_press(key)

        # Set up the keyboard listener
        self.listener = keyboard.Listener(
            on_press=on_press_track,
            on_release=on_release)

    def toggle_recording(self):
        if self.recording:
            playsound(self.stop_sound, block=False)  # Play stop sound first
            self.recording = False  # Then stop recording
        else:
            playsound(self.start_sound, block=False)  # Non-blocking sound play
            # Start new recording
            audio = self.record_audio()
            if audio is not None:
                text = self.transcribe_audio(audio)
                self.copy_to_clipboard(text)
                playsound(self.stop_sound, block=False)  # Play stop sound first
                self.recording = False  # Then stop recording

def list_available_models():
    models = ["tiny", "base", "small", "medium", "large"]
    print("\nAvailable Whisper models:")
    for model in models:
        print(f"- {model}")
    print("\nNote: Larger models are more accurate but require more computational resources and memory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Voice Transcription Tool using Whisper')
    parser.add_argument('--model', type=str, default='tiny',
                      help='Whisper model to use (tiny, base, small, medium, large)')
    parser.add_argument('--list-models', action='store_true',
                      help='List all available Whisper models')
    
    args = parser.parse_args()
    
    if args.list_models:
        list_available_models()
        sys.exit(0)
        
    try:
        tool = TranscriptionTool(model_name=args.model)
        tool.start()
    except ValueError as e:
        print(f"Error: Invalid model name '{args.model}'")
        list_available_models()
        sys.exit(1)