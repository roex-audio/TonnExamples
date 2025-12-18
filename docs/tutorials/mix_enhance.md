# Tutorial: Mix Enhance - Automatic Mix Improvement

Welcome to the Mix Enhance tutorial! This guide walks you through quickly enhancing and mastering your audio tracks using RoEx's Mix Enhance technology API.

## What Makes Mix Enhance Special?

- **No Stems Required**: Mix Enhance operates directly on stereo files, saving you from the hassle of exporting separate stems from your DAW
- **Studio-Grade Enhancement**: Inspired by classic analog gear like the Pultec EQ and LA-2A Compressor, Mix Enhance instantly adds clarity, warmth, punch, and brightness
- **Optimized for Streaming**: Automatically adjust your mixes to meet the loudness and quality standards required by Spotify, Apple Music, etc.
- **Flexible Stem Separation**: Optionally perform stem separation and return individually processed stems

## What You'll Learn

- **Preview your mix enhancement** quickly to hear a short sample before committing
- **Fully enhance your mix** by automatically correcting common mixing issues
- **Retrieve and download** your enhanced tracks and individual stems

## Prerequisites

- Python installed on your system (version 3.7 or higher recommended)
- Your API Key from [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)

## Running the Example

```bash
cd python/examples
python 03_mix_enhance.py

# Or with your own audio URL
python 03_mix_enhance.py https://your-storage.com/your_track.wav
```

## The Enhancement Workflow

### Step 1: Preview Enhancement

The script first creates a **preview** of your enhanced track:

```
🎚️  Starting Mix Enhance preview...
✓ Preview task created. Task ID: abc123...

⏳ Waiting for preview to complete...
  Attempt 1/70: Processing
  Attempt 2/70: Processing
✓ Processing complete!
```

This preview is quick and free to experiment with.

### Step 2: Full Enhancement

After the preview, it creates the **full enhancement**:

```
🎚️  Starting full Mix Enhance...
✓ Full enhance task created. Task ID: def456...

⏳ Waiting for full enhancement to complete...
✓ Processing complete!

✅ Mix Enhance Complete!
```

## Enhancement Options

The API supports various fix options:

| Option | Description |
|--------|-------------|
| `fixClippingIssues` | Repair clipped/distorted audio |
| `fixDRCIssues` | Fix dynamic range compression problems |
| `fixStereoWidthIssues` | Correct stereo imaging |
| `fixTonalProfileIssues` | Balance frequency response |
| `fixLoudnessIssues` | Optimize loudness for streaming |
| `applyMastering` | Apply final mastering |

### Loudness Preferences

- `STREAMING_LOUDNESS`: Optimized for Spotify, Apple Music (-14 LUFS)
- `CD_LOUDNESS`: Traditional CD loudness levels

## Programmatic Usage

```python
from shared import TonnClient

client = TonnClient()

# Start enhancement
response = client.post("/mixenhance", {
    "mixReviveData": {
        "audioFileLocation": "https://your-storage.com/track.wav",
        "musicalStyle": "POP",
        "isMaster": False,
        "fixClippingIssues": True,
        "fixDRCIssues": True,
        "fixStereoWidthIssues": True,
        "fixTonalProfileIssues": True,
        "fixLoudnessIssues": True,
        "applyMastering": True,
        "loudnessPreference": "STREAMING_LOUDNESS",
        "stemProcessing": False
    }
})

task_id = response.get("mixrevive_task_id")

# Poll for results
payload = {
    "mixReviveData": {
        "mixReviveTaskId": task_id
    }
}

results = client.poll_for_result(
    endpoint="/retrieveenhancedtrack",
    payload=payload,
    result_key="revivedTrackTaskResults",
    max_attempts=70,
    poll_interval=5
)

# Download the enhanced track
download_url = results.get("download_url_revived")
client.download_file(download_url, "enhanced_track.wav")
```

## Use Cases

### Bedroom Producers

Enhance your mixes to a professional standard quickly, letting you focus more on creativity.

### Artists and Labels

Revive and optimize older tracks for modern streaming platforms without remixing or accessing original sessions.

### Mastering Engineers

Accelerate workflows with automated fixes, allowing more time for creative fine-tuning.

## Tips for Advanced Users

- **Webhooks**: Supply a webhook URL in your requests to receive asynchronous notifications
- **Batch Processing**: Adapt the script to handle multiple tracks simultaneously
- **Stem Processing**: Enable `stemProcessing: true` to receive individually processed stems

## Questions or Feedback?

- Visit [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- Contact: support@roexaudio.com

