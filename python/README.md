# Python Examples for the Tonn API

This folder contains Python examples for integrating with the Tonn API for automated audio mixing, mastering, and analysis.

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

This installs:
- `requests` - HTTP client
- `python-dotenv` - Load `.env` files automatically

### 2. Set Your API Key

Get your API key from [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)

**On macOS/Linux:**
```bash
export TONN_API_KEY=your_api_key_here
```

**On Windows (Command Prompt):**
```cmd
set TONN_API_KEY=your_api_key_here
```

**On Windows (PowerShell):**
```powershell
$env:TONN_API_KEY="your_api_key_here"
```

### 3. Run an Example

```bash
cd examples
python 01_mix_analysis.py your_track.wav POP
```

## Examples Overview

| # | Script | Description |
|---|--------|-------------|
| 01 | `mix_analysis.py` | Analyze your mix for loudness, dynamics, and issues |
| 02 | `mix_comparison.py` | Compare two mixes side-by-side |
| 03 | `mix_enhance.py` | Automatically enhance a stereo mix |
| 04 | `multitrack_mix.py` | Mix multiple stems with AI-assisted settings |
| 05 | `audio_cleanup.py` | Clean up noisy recordings |
| 06 | `batch_mastering.py` | Master an entire album/EP consistently |

## Folder Structure

```
python/
├── README.md           # This file
├── examples/           # Runnable example scripts
│   ├── 01_mix_analysis.py
│   ├── 02_mix_comparison.py
│   ├── 03_mix_enhance.py
│   ├── 04_multitrack_mix.py
│   ├── 05_audio_cleanup.py
│   └── 06_batch_mastering.py
├── shared/             # Shared utilities (import in your own code)
│   ├── __init__.py
│   ├── client.py       # TonnClient class
│   └── config.py       # Configuration helpers
└── payloads/           # Example JSON payloads
    ├── multitrack_mix.json
    ├── final_mix_settings.json
    └── album_mastering.json
```

## Using the Shared Utilities

The `shared/` folder contains reusable code you can use in your own projects:

```python
from shared import TonnClient

# Create a client
client = TonnClient()

# Upload a local file and get its cloud URL
url = client.upload_local_file("my_track.wav")

# Make API requests
response = client.post("/mixanalysis", {"mixDiagnosisData": {...}})

# Download results
client.download_file(download_url, "output.wav")
```

## Supported Audio Formats

- `.mp3` - MP3 audio
- `.wav` - WAV audio
- `.flac` - FLAC audio

## Musical Styles

When analyzing or processing audio, specify a musical style:

- `ROCK` / `ROCK_INDIE`
- `POP`
- `ELECTRONIC`
- `HIPHOP_GRIME`
- `ACOUSTIC`
- `SINGER_SONGWRITER`
- `JAZZ`
- `CLASSICAL`
- And more...

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"

```bash
pip install -r ../requirements.txt
```

### "ModuleNotFoundError: No module named 'shared'"

Make sure you're running from the `examples/` directory:

```bash
cd python/examples
python 01_mix_analysis.py ...
```

### "TONN_API_KEY environment variable not set"

Set your API key or create a `.env` file in the project root:

```bash
# Option 1: Environment variable
export TONN_API_KEY=your_key_here

# Option 2: Create .env file
echo "TONN_API_KEY=your_key_here" > ../../.env
```

### More Issues?

See the full [Troubleshooting Guide](../docs/TROUBLESHOOTING.md).

## Need Help?

- [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- [Full API Documentation](https://tonn-portal.roexaudio.com)
- [Audio Effects Guide](../docs/AUDIO_EFFECTS_GUIDE.md)
- Contact: support@roexaudio.com

