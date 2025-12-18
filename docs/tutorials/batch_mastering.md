# Tutorial: Batch Mastering Your EP or Album

When releasing an EP or album independently, achieving consistent sound quality and loudness across tracks can be challenging and time-consuming. Automating the mastering process not only saves time but ensures sonic consistency throughout your project, providing listeners with a cohesive experience.

## Why Batch Mastering?

Mastering an album or EP track-by-track can lead to inconsistent loudness levels and sonic character, causing your project to lose coherence. Batch mastering allows you to set consistent mastering parameters across your entire project, ensuring uniform loudness, style, and sound quality.

## Prerequisites

Before you begin, you'll need:

- Python installed on your machine ([Download here](https://www.python.org/downloads/))
- The `requests` Python package (`pip install requests`)
- An API key from [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)

## Preparing Your Tracks

Each track requires:

- **trackURL**: URL of your track file (WAV, MP3, or FLAC)
- **musicalStyle**: Genre-specific mastering preset (e.g., ROCK_INDIE, POP, ELECTRONIC)
- **desiredLoudness**: Desired loudness level (QUIET, MEDIUM, or LOUD)
- **sampleRate**: Optional, defaults to "44100"
- **webhookURL**: Optional URL to receive API callbacks

## Running the Batch Mastering Script

```bash
cd python/examples

# Master all files in a directory
python 06_batch_mastering.py ./my_album

# Specify options
python 06_batch_mastering.py ./my_album \
    --output-dir ./masters \
    --style POP \
    --loudness MEDIUM
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_dir` | Directory containing audio files | Required |
| `-o, --output-dir` | Where to save mastered files | ./mastered_output |
| `--style` | Musical style | ROCK_INDIE |
| `--loudness` | QUIET, MEDIUM, or LOUD | MEDIUM |
| `--sample-rate` | Output sample rate | 44100 |

## What the Script Does

For each supported audio file in the directory:

1. **Upload**: Sends your track to cloud storage
2. **Preview**: Creates a mastering preview
3. **Poll**: Waits until the preview is ready
4. **Final Master**: Retrieves the fully mastered track
5. **Download**: Saves the mastered file to your output directory

## Tips for Optimal Results

### Consistent Loudness

Choose the same loudness level (`MEDIUM` is typically industry-standard at around -14 LUFS) across all tracks for a cohesive listening experience.

### Musical Style Accuracy

Carefully select the musical style to match your project accurately; this ensures genre-specific optimizations are applied.

### Sample Rate Considerations

- **44100 Hz**: Standard for CD and audio distribution
- **48000 Hz**: Typical for video production and higher-resolution streaming

## Listening & Checking Results

Your mastered tracks will be downloaded into your output directory. It's crucial to listen critically to each mastered track and ensure they meet your expectations for:

- Loudness consistency
- Tonal balance
- Overall cohesiveness

## Example Output

```
============================================================
BATCH MASTERING
============================================================

Input:     ./my_album
Output:    ./masters
Style:     POP
Loudness:  MEDIUM
Tracks:    5

============================================================
Processing: track_01_intro.wav
============================================================

📤 Uploading...
✓ File uploaded successfully

🎚️  Creating mastering preview...
✓ Preview task created: abc123...

⏳ Waiting for preview...
  Attempt 1/30: Processing
  Attempt 2/30: Processing
✓ Processing complete!

📥 Retrieving final master...
✓ Downloaded: ./masters/track_01_intro_mastered.wav

... (continues for each track)

============================================================
BATCH MASTERING COMPLETE
============================================================

✅ Successful: 5

Mastered files saved to: ./masters
```

## Support

For further assistance:
- Visit [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- Contact: support@roexaudio.com

