# ROEX TONN Audio Effects Guide

This guide explains how to use the extensive audio effects processing capabilities in the ROEX TONN API for mixing and mastering.

## Overview

The ROEX TONN API now supports advanced audio effects processing for each track in your multitrack mix, including:

- **Gain Control**: Precise level adjustment per track
- **Panning**: Stereo positioning from left to right
- **6-Band Parametric EQ**: Frequency-specific tonal shaping
- **Compression**: Dynamic range control

## Audio Effects Parameters

### Gain Control

- **Parameter**: `gainDb`
- **Range**: -60 dB to +12 dB
- **Description**: Adjusts the overall level of the track

```json
{
  "gainDb": -3
}
```

### Panning Settings

- **Parameter**: `panning_settings.panning_angle`
- **Range**: -60° (left) to +60° (right)
- **Description**: Controls stereo positioning
  - `-60` to `-1`: Panned left
  - `0`: Center
  - `1` to `60`: Panned right

```json
{
  "panning_settings": {
    "panning_angle": -25
  }
}
```

**Common Panning Strategies:**
- **Bass/Kick**: Center (0°) - anchors the low end
- **Lead Vocals/Main Elements**: Center (0°)
- **Supporting Elements**: ±15° to ±30° - adds width
- **Percussion/Effects**: ±25° to ±45° - creates space
- **Stereo Width**: Opposite panning (e.g., -35° and +35°)

### EQ Settings (6-Band Parametric)

Each track has 6 fully parametric EQ bands with individual control over:

- **gain**: -12 dB to +12 dB (boost or cut)
- **q**: 0.1 to 10 (bandwidth/resonance)
  - Lower Q (0.1-0.5): Wide, gentle curves
  - Medium Q (0.5-2.0): Standard EQ adjustments
  - High Q (2.0-10): Narrow, surgical cuts/boosts
- **centre_freq**: 20 Hz to 20,000 Hz

```json
{
  "eq_settings": {
    "band_1": {
      "gain": 2,
      "q": 0.7,
      "centre_freq": 60
    },
    "band_2": {
      "gain": -3,
      "q": 0.5,
      "centre_freq": 250
    },
    "band_3": {
      "gain": 0,
      "q": 0.8,
      "centre_freq": 800
    },
    "band_4": {
      "gain": 1,
      "q": 1.0,
      "centre_freq": 2000
    },
    "band_5": {
      "gain": -2,
      "q": 0.5,
      "centre_freq": 5000
    },
    "band_6": {
      "gain": -4,
      "q": 0.3,
      "centre_freq": 12000
    }
  }
}
```

**Frequency Ranges:**
- **Sub-bass**: 20-60 Hz - Fundamental low frequency energy
- **Bass**: 60-250 Hz - Warmth and body
- **Low-mids**: 250-800 Hz - Fullness and thickness
- **Mids**: 800-2000 Hz - Presence and definition
- **Upper-mids**: 2000-5000 Hz - Clarity and articulation
- **Highs**: 5000-20000 Hz - Brightness and air

### Compression Settings

Dynamic range control with precise attack and release characteristics:

- **threshold**: -60 dB to 0 dB - Level at which compression begins
- **ratio**: 1:1 to 20:1 - Amount of compression applied
  - 1:1 - No compression
  - 2:1 to 4:1 - Gentle, musical compression
  - 4:1 to 8:1 - Medium, noticeable compression
  - 8:1 to 20:1 - Heavy compression/limiting
- **attack_ms**: 0.1 ms to 100 ms - How quickly compression engages
  - Fast (0.1-5 ms): Catches transients, more aggressive
  - Medium (5-20 ms): Balanced, natural sound
  - Slow (20-100 ms): Preserves transients, gentle
- **release_ms**: 1 ms to 1000 ms - How quickly compression releases
  - Fast (1-50 ms): Responsive, can pump
  - Medium (50-200 ms): Natural, musical
  - Slow (200-1000 ms): Smooth, transparent

```json
{
  "compression_settings": {
    "threshold": -18,
    "ratio": 4,
    "attack_ms": 10,
    "release_ms": 80
  }
}
```

## Instrument-Specific Examples

### Bass Guitar/Synth Bass

**Goal**: Solid, consistent low end with clarity

```json
{
  "gainDb": -3,
  "panning_settings": {
    "panning_angle": 0
  },
  "eq_settings": {
    "band_1": {
      "gain": 2,
      "q": 0.7,
      "centre_freq": 60
    },
    "band_2": {
      "gain": -3,
      "q": 0.5,
      "centre_freq": 250
    },
    "band_3": {
      "gain": 0,
      "q": 0.8,
      "centre_freq": 800
    },
    "band_4": {
      "gain": 1,
      "q": 1.0,
      "centre_freq": 2000
    },
    "band_5": {
      "gain": -2,
      "q": 0.5,
      "centre_freq": 5000
    },
    "band_6": {
      "gain": -4,
      "q": 0.3,
      "centre_freq": 12000
    }
  },
  "compression_settings": {
    "threshold": -18,
    "ratio": 4,
    "attack_ms": 10,
    "release_ms": 80
  }
}
```

### Kick Drum

**Goal**: Punchy low end with beater click definition

```json
{
  "gainDb": 0,
  "panning_settings": {
    "panning_angle": 0
  },
  "eq_settings": {
    "band_1": {
      "gain": 4,
      "q": 1.0,
      "centre_freq": 50
    },
    "band_2": {
      "gain": -4,
      "q": 0.8,
      "centre_freq": 200
    },
    "band_3": {
      "gain": -2,
      "q": 0.5,
      "centre_freq": 500
    },
    "band_4": {
      "gain": 3,
      "q": 1.5,
      "centre_freq": 3000
    },
    "band_5": {
      "gain": 0,
      "q": 0.7,
      "centre_freq": 6000
    },
    "band_6": {
      "gain": -6,
      "q": 0.3,
      "centre_freq": 12000
    }
  },
  "compression_settings": {
    "threshold": -12,
    "ratio": 6,
    "attack_ms": 3,
    "release_ms": 50
  }
}
```

### Percussion/Hi-Hats

**Goal**: Bright, crisp high-frequency elements with stereo width

```json
{
  "gainDb": -4,
  "panning_settings": {
    "panning_angle": -25
  },
  "eq_settings": {
    "band_1": {
      "gain": -8,
      "q": 0.5,
      "centre_freq": 60
    },
    "band_2": {
      "gain": -3,
      "q": 0.7,
      "centre_freq": 250
    },
    "band_3": {
      "gain": 1,
      "q": 1.0,
      "centre_freq": 1500
    },
    "band_4": {
      "gain": 3,
      "q": 1.2,
      "centre_freq": 4000
    },
    "band_5": {
      "gain": 4,
      "q": 0.8,
      "centre_freq": 8000
    },
    "band_6": {
      "gain": 3,
      "q": 0.5,
      "centre_freq": 14000
    }
  },
  "compression_settings": {
    "threshold": -15,
    "ratio": 4,
    "attack_ms": 5,
    "release_ms": 60
  }
}
```

### Synth Chords/Pads

**Goal**: Warm, present mid-range with sparkle and width

```json
{
  "gainDb": -2,
  "panning_settings": {
    "panning_angle": 15
  },
  "eq_settings": {
    "band_1": {
      "gain": -6,
      "q": 0.7,
      "centre_freq": 80
    },
    "band_2": {
      "gain": -2,
      "q": 0.5,
      "centre_freq": 200
    },
    "band_3": {
      "gain": 2,
      "q": 1.2,
      "centre_freq": 1000
    },
    "band_4": {
      "gain": 3,
      "q": 1.5,
      "centre_freq": 3000
    },
    "band_5": {
      "gain": 2,
      "q": 0.8,
      "centre_freq": 8000
    },
    "band_6": {
      "gain": 1,
      "q": 0.5,
      "centre_freq": 15000
    }
  },
  "compression_settings": {
    "threshold": -20,
    "ratio": 3,
    "attack_ms": 15,
    "release_ms": 100
  }
}
```

### Lead Synth

**Goal**: Forward presence with harmonic enhancement

```json
{
  "gainDb": -5,
  "panning_settings": {
    "panning_angle": -15
  },
  "eq_settings": {
    "band_1": {
      "gain": -5,
      "q": 0.7,
      "centre_freq": 80
    },
    "band_2": {
      "gain": 1,
      "q": 0.8,
      "centre_freq": 400
    },
    "band_3": {
      "gain": 2,
      "q": 1.0,
      "centre_freq": 1200
    },
    "band_4": {
      "gain": 3,
      "q": 1.2,
      "centre_freq": 2500
    },
    "band_5": {
      "gain": 4,
      "q": 0.8,
      "centre_freq": 6000
    },
    "band_6": {
      "gain": 2,
      "q": 0.6,
      "centre_freq": 12000
    }
  },
  "compression_settings": {
    "threshold": -22,
    "ratio": 3,
    "attack_ms": 20,
    "release_ms": 150
  }
}
```

## Top-Level Mix Settings

Beyond individual track settings, you can control the overall mix output:

```json
{
  "applyAudioEffectsData": {
    "multitrackTaskId": "your-task-id",
    "trackData": [ /* ... track settings ... */ ],
    "returnStems": true,
    "createMaster": true,
    "desiredLoudness": "MEDIUM",
    "sampleRate": "44100",
    "webhookURL": "https://your-webhook-url.com"
  }
}
```

### Parameters:

- **multitrackTaskId**: Task ID from the preview mix (required)
- **returnStems**: `true` to receive individual processed stems
- **createMaster**: `true` to create a mastered version
- **desiredLoudness**: `"QUIET"`, `"MEDIUM"`, `"LOUD"`, or `"VERY_LOUD"`
- **sampleRate**: `"44100"`, `"48000"`, `"88200"`, or `"96000"`
- **webhookURL**: Optional callback URL for async processing

## Example Files

### Standard Mix: `final_mix_settings.json`

A balanced, professional mix with:
- Natural panning spread
- Moderate compression
- Frequency separation between instruments
- Medium loudness target

### Alternative Mix: `final_mix_settings_alternative.json`

A more aggressive approach with:
- Wider stereo image
- Heavier compression
- More pronounced EQ shaping
- Loud mastering target

## Usage with Python Script

The `roex_mix_settings.py` script includes helper functions to display all audio effects:

```python
# Import and use the audio effects printer
from roex_mix_settings import print_audio_effects_settings

# Load your settings
with open("final_mix_settings.json") as f:
    settings = json.load(f)

# Display all effects
track_data = settings["applyAudioEffectsData"]["trackData"]
print_audio_effects_settings(track_data)
```

This will display a formatted view of all panning, EQ, and compression settings for each track.

## Best Practices

1. **Start with Preview Mix**: Always create a preview mix first to get AI-suggested settings
2. **Iterate Gradually**: Make incremental adjustments rather than extreme changes
3. **Monitor in Context**: Listen to each track in the context of the full mix
4. **Balance Frequencies**: Ensure instruments occupy different frequency ranges
5. **Use Compression Wisely**: Over-compression can make mixes sound lifeless
6. **Create Space with Panning**: Don't overcrowd the center image
7. **Reference Commercial Tracks**: Compare your mix to professional releases

## Troubleshooting

### Mix Sounds Muddy
- Cut low frequencies on non-bass instruments (band_1, band_2)
- Reduce overlapping mid-range frequencies
- Add clarity with upper-mid boosts (band_4, band_5)

### Mix Sounds Harsh
- Reduce high-frequency boosts (band_5, band_6)
- Use wider Q values for gentler EQ curves
- Reduce compression ratios

### Mix Lacks Punch
- Boost fundamental frequencies on kick and bass
- Use faster attack times on drums
- Increase compression ratios on rhythmic elements

### Mix Sounds Flat (Mono)
- Increase panning spread on supporting elements
- Keep bass and kick centered
- Pan similar elements to opposite sides

## API Endpoints

- **Preview Mix**: `POST /mixpreview` - Create initial AI-suggested mix
- **Apply Effects**: `POST /retrievefinalmix` - Apply custom audio effects
- **Poll Status**: `POST /retrievepreviewmix` - Check mix progress

For complete API documentation, visit: https://tonn-portal.roexaudio.com

## Support

For questions or support, contact the ROEX team or visit the developer portal.
