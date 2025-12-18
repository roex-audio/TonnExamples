# Tutorial: Audio Cleanup

In this tutorial, we'll walk through how to use RoEx's **audio cleanup API** to clean up noisy, problematic instrument tracks, especially vocals.

## Why Audio Cleanup?

Audio recordings, especially those captured in uncontrolled environments, often contain unwanted noise or imperfections. These issues can make your track sound unprofessional and detract from the overall listening experience.

With just a few API calls, the RoEx API will process your audio and clean up:
- Background noise
- Microphone bleed
- Hum and hiss
- Other imperfections

## Common Use Cases

### Outdoor Recordings

Wind, traffic, and environmental noises often seep into recordings made outdoors. The API can help clean up these recordings, leaving only the desired sounds.

### Phone Recordings

If you've recorded vocals or instruments using a phone or portable device, there's a high chance that unwanted noise has been captured. The API can clean this up while maintaining the integrity of the main sound.

### Microphone Bleed

During live performances or multi-microphone setups, sound from other sources can bleed into your recording. The API can isolate and clean up specific instrument groups.

### Noisy Recordings

Even in controlled environments, recordings can have hum, hiss, or other unwanted sounds. The API can reduce these noises and improve overall quality.

## Supported Sound Sources

| Sound Source | Description |
|--------------|-------------|
| `VOCAL_GROUP` | Lead vocals |
| `BACKING_VOCALS_GROUP` | Background vocals |
| `DRUMS_GROUP` | Full drum kit |
| `KICK_GROUP` | Kick drum |
| `SNARE_GROUP` | Snare drum |
| `PERCS_GROUP` | Percussion |
| `E_GUITAR_GROUP` | Electric guitar |
| `A_GUITAR_GROUP` | Acoustic guitar |
| `STRINGS_GROUP` | String instruments |

## Supported Formats

Audio cleanup **only supports**:
- `.wav` (WAV)
- `.flac` (FLAC)

These lossless formats are required to preserve audio quality during processing.

## Running the Cleanup

```bash
cd python/examples
python 05_audio_cleanup.py noisy_vocals.wav

# Specify the sound source
python 05_audio_cleanup.py drums.wav --source DRUMS_GROUP
```

### Command Line Options

```bash
python 05_audio_cleanup.py <input_file> [-s/--source SOUND_SOURCE]
```

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Path to audio file (.wav or .flac) | Required |
| `-s, --source` | Sound source type | VOCAL_GROUP |

## Example Output

```
🎤 Audio Cleanup
   File: noisy_vocals.wav
   Source Type: VOCAL_GROUP

📤 Uploading file...
✓ Upload URLs obtained successfully
✓ File uploaded successfully

🧹 Running audio cleanup...

==================================================
Error: False
Message: Cleanup initiated successfully
Info: Processing audio

==================================================
AUDIO CLEANUP RESULTS
==================================================

Completion Time: 2025-01-15 10:30:45
Info: Cleanup complete

📥 Download URL: https://storage.googleapis.com/...

📥 Downloading cleaned audio...
✓ Downloaded: cleaned_noisy_vocals.wav

✅ Cleaned audio saved to: cleaned_noisy_vocals.wav
```

## Programmatic Usage

```python
from shared import TonnClient

client = TonnClient()

# Upload the file
url = client.upload_local_file("noisy_vocals.wav")

# Request cleanup
response = client.post("/audio-cleanup", {
    "audioCleanupData": {
        "audioFileLocation": url,
        "soundSource": "VOCAL_GROUP"
    }
})

# Get results
results = response.get("audioCleanupResults", {})
download_url = results.get("cleaned_audio_file_location")

# Download cleaned audio
client.download_file(download_url, "cleaned_vocals.wav")
```

## Benefits

- **Time-Saving**: Manually cleaning up audio files can be time-consuming. The API automates the process.
- **High-Quality Results**: Advanced machine learning and signal processing techniques clean your audio without compromising quality.
- **Versatility**: Works with vocals, drums, guitars, strings, and more.
- **Easy to Use**: Simple API call to submit and download cleaned audio.

## Tips for Best Results

1. **Choose the right sound source**: Selecting the correct instrument group helps the AI focus on the right frequency ranges.

2. **Use high-quality source files**: Better input = better output. Use WAV or FLAC files.

3. **Check before and after**: Always compare the cleaned audio to the original to ensure the desired content is preserved.

## Support

For questions or feedback:
- Visit [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- Contact: support@roexaudio.com

Happy audio cleaning!

