# Transcription Tool Usage Guide

This tool allows you to record audio and automatically transcribe it to text using OpenAI's Whisper model.

## Setup
1. Make sure you have all required dependencies installed:
   ```bash
   uv sync
   ```

## How to Use

1. Run the script:
   ```bash
   uv run transcription_tool.py [--model MODEL] [--list-models]
   ```

2. The tool will start and wait for your commands. You have two main hotkey combinations:

   - **Ctrl+Space** (All platforms)
     - Press to start recording
     - While recording, press 'Esc' to stop recording
     - The transcription will automatically begin after stopping
     - Once complete, the text will be copied to your clipboard

   - **Cmd+Shift+Q** (Mac) or **Ctrl+Shift+Q** (Windows/Linux)
     - Press to quit the application


### Options:
- `--model MODEL`: Choose the Whisper model to use (default: "tiny")
  - Available options: tiny, base, small, medium, large
  - Larger models are more accurate but require more computational resources

- `--list-models`: Display all available Whisper models and exit


### Examples

```bash
# Run with default (tiny) model
uv run transcription_tool.py
# Use the base model for better accuracy
uv run transcription_tool.py --model base
# List all available models
uv run transcription_tool.py --list-models
```

## Features
- Automatic language detection
- Direct clipboard integration
- Real-time audio recording
- Uses OpenAI's Whisper model for accurate transcription

## Notes
- The first time you run the tool, it will download the Whisper "base" model
- The transcription quality depends on your audio input quality
- Make sure your microphone is properly configured before starting