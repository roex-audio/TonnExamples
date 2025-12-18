# Quick Start Guide

Get up and running with the Tonn API in 5 minutes.

## Step 1: Get Your API Key

1. Go to [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
2. Sign up or log in
3. Copy your API key

## Step 2: Set Up Your Environment

```bash
# Clone the repo
git clone https://github.com/roex-audio/TonnExamples.git
cd TonnExamples

# Install dependencies
pip install requests

# Set your API key (replace with your actual key)
export TONN_API_KEY=your_api_key_here
```

## Step 3: Run Your First Example

Analyze a mix to see how the API works:

```bash
cd python/examples

# Using a sample track from the demo bucket
python 01_mix_analysis.py --help

# Or analyze your own file
python 01_mix_analysis.py /path/to/your/track.wav POP
```

You'll see output like:

```
📤 Uploading track.wav...
✓ Upload URLs obtained successfully
✓ File uploaded successfully

🔍 Analyzing your mix...
✅ Analysis complete

============================================================
MIX DIAGNOSIS RESULTS
============================================================

--- Technical Details ---
  Bit Depth: 24
  Sample Rate: 44100
  Integrated Loudness (LUFS): -14.2
  Peak Loudness (dBFS): -1.0
  Stereo Field: STEREO
  Mono Compatible: True

--- Recommendations ---
  1. Loudness is appropriate for streaming platforms
  2. Good dynamic range preserved
  ...
```

## What's Next?

### Try More Examples

| Example | What it does |
|---------|--------------|
| `02_mix_comparison.py` | Compare two mixes side-by-side |
| `03_mix_enhance.py` | Auto-enhance a stereo mix |
| `04_multitrack_mix.py` | Mix multiple stems together |
| `05_audio_cleanup.py` | Clean up noisy recordings |
| `06_batch_mastering.py` | Master an entire album |

### Read the Tutorials

- [Multitrack Mixing Tutorial](docs/tutorials/multitrack_mixing.md)
- [Batch Mastering Tutorial](docs/tutorials/batch_mastering.md)
- [Mix Analysis Tutorial](docs/tutorials/mix_analysis.md)
- [Audio Effects Guide](docs/AUDIO_EFFECTS_GUIDE.md)

### Build Your Own Integration

Use the shared utilities in your own code:

```python
from shared import TonnClient

client = TonnClient()

# Upload your audio file
url = client.upload_local_file("my_track.wav")

# Call any API endpoint
response = client.post("/mixanalysis", {
    "mixDiagnosisData": {
        "audioFileLocation": url,
        "musicalStyle": "POP",
        "isMaster": False
    }
})

print(response)
```

## Need Help?

- [Full API Documentation](https://tonn-portal.roexaudio.com)
- [Python Examples README](python/README.md)
- Email: support@roexaudio.com

