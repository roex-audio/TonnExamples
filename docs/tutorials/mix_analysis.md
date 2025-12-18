# Tutorial: Mix Analysis with Mix Check Studio

This guide explains how to use the **Tonn API** to analyze your mixed or mastered tracks, ensuring they are polished and ready for release on streaming platforms.

Using Tonn API for Mix Analysis leverages the same advanced technology behind RoEx's [Mix Check Studio](https://mixcheckstudio.roexaudio.com), which has already been used by DIY musicians and producers on hundreds of thousands of tracks.

## What is Mix Check Studio?

**Mix Check Studio** analyzes your music tracks to identify potential issues in your mix or master, providing detailed feedback on:

- **Loudness**: How your track compares to streaming platform standards
- **Dynamic Range**: Compression levels and dynamics evaluation
- **Clipping**: Detection of unwanted distortion or peaks
- **Stereo Field**: Stereo imaging and mono compatibility
- **Tonal Profile**: Frequency balance and EQ recommendations
- **Phase Issues**: Potential phase problems in your mix

## Why Analyze Your Tracks?

Before releasing music, it's crucial to ensure your tracks meet industry standards. Mix Check Studio helps by highlighting:

- **Clipping issues**: Detects unwanted distortion or peaks that may degrade audio quality
- **Dynamic range issues**: Evaluates compression levels to ensure appropriate dynamics
- **Loudness**: Analyzes how your track's loudness compares to Spotify, Apple Music, and YouTube standards
- **Stereo field and mono compatibility**: Assesses stereo imaging, ensuring your music sounds great on all devices
- **Tonal balance**: Offers insights to enhance warmth, clarity, and overall sonic presence

## Running the Analysis

```bash
cd python/examples
python 01_mix_analysis.py your_track.wav POP
```

### Command Line Options

```bash
python 01_mix_analysis.py <input_file> <musical_style> [--is-master]
```

| Argument | Description |
|----------|-------------|
| `input_file` | Path to your audio file (.mp3, .wav, .flac) |
| `musical_style` | Genre (ROCK, POP, ELECTRONIC, HIPHOP_GRIME, etc.) |
| `--is-master` | Flag if analyzing a mastered track (affects evaluation) |

## Understanding the Results

### Technical Details

```
--- Technical Details ---
  Bit Depth: 24
  Sample Rate: 44100
  Integrated Loudness (LUFS): -8.88
  Peak Loudness (dBFS): 1.3
  Clipping: MINOR
  Stereo Field: STEREO_UPMIX
  Mono Compatible: True
  Phase Issues: False
```

### What the Metrics Mean

| Metric | Good Range | Notes |
|--------|------------|-------|
| Integrated Loudness | -14 to -16 LUFS | For streaming (Spotify, Apple Music) |
| Peak Loudness | Below 0 dBFS | Above 0 = clipping |
| Clipping | NONE | MINOR = small peaks, MAJOR = serious issues |
| Mono Compatible | True | False = phase cancellation on mono speakers |

### Recommendations

The API provides actionable recommendations:

```
--- Recommendations ---
  1. Minor clipping detected; use a limiter to control peaks.
  2. Dynamic range is limited; avoid heavy compression.
  3. Loudness exceeds streaming standards by 5.1 dB
  4. Recommended EQ adjustments: boost low-mid frequencies for warmth
```

## Improving Your Mix

Based on the analysis, you can:

1. **Adjust loudness and dynamic range** in your DAW
2. **Correct clipping** using a limiter
3. **Enhance tonal profile** with EQ adjustments
4. **Fix stereo issues** for better mono compatibility

## Re-analyze After Changes

After making improvements:

1. Re-run the analysis
2. Compare results to your previous version
3. Use the [Mix Comparison](mix_comparison.md) feature for detailed A/B comparison

## Programmatic Usage

```python
from shared import TonnClient

client = TonnClient()

# Upload your file
url = client.upload_local_file("my_mix.wav")

# Analyze
response = client.post("/mixanalysis", {
    "mixDiagnosisData": {
        "audioFileLocation": url,
        "musicalStyle": "POP",
        "isMaster": False
    }
})

# Access results
results = response.get("mixDiagnosisResults", {})
payload = results.get("payload", {})

print(f"Loudness: {payload.get('integrated_loudness_lufs')} LUFS")
print(f"Clipping: {payload.get('clipping')}")
```

## Support

For further assistance:
- Visit [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- Contact: support@roexaudio.com

Remember: Use this analysis as guidance. Always trust your ears for final decisions!

