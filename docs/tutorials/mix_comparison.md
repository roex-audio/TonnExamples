# Tutorial: Compare Two Mixes

This guide explains how to use the **Tonn API** to compare two different versions of a mix or reference tracks, allowing you to assess progress, consistency, or alignment with a sonic benchmark.

## What is Mix Comparison?

**Mix Comparison** allows you to:

- Compare two different versions of your mix to track improvements
- Benchmark your mix against a professionally released track
- A/B test different mastering approaches

## Why Compare Mixes?

Whether you're refining your sound or preparing a release, comparison helps ensure:

- **Improved sound quality**: Know if your changes are actually better
- **Reference-based mixing**: Match the clarity and energy of tracks you admire
- **Consistency across versions**: Spot regressions or overprocessing early

## Running the Comparison

```bash
cd python/examples
python 02_mix_comparison.py my_mix.wav reference.wav POP
```

### Command Line Options

```bash
python 02_mix_comparison.py <file_a> <file_b> <musical_style> [--is-master]
```

| Argument | Description |
|----------|-------------|
| `file_a` | First audio file (your mix) |
| `file_b` | Second audio file (reference or alternate version) |
| `musical_style` | Genre (ROCK, POP, ELECTRONIC, etc.) |
| `--is-master` | Flag if comparing mastered tracks |

## Understanding the Output

The script provides color-coded, side-by-side comparisons:

```
=== Production Metrics Comparison ===

integrated_loudness_lufs:
  File A: -13.3
  File B: -10.9
  → Difference of 2.4 exceeds threshold

mono_compatible:
  File A: False
  File B: True
  → Values differ

bit_depth:
  File A: 16
  File B: 24
  → Difference of 8 exceeds threshold
```

### What Gets Compared

#### Technical Metrics
- Bit depth
- Sample rate
- Clipping status
- Loudness (LUFS, peak)
- DRC evaluations
- Mono compatibility
- Stereo field and phase issues

#### Tonal Profile
- Bass frequency content
- Low-mid energy
- High-mid energy
- High frequency content

## Interpreting Results

### Loudness Differences

| Difference | Interpretation |
|------------|----------------|
| < 1 LUFS | Very similar, likely unnoticeable |
| 1-3 LUFS | Noticeable difference |
| > 3 LUFS | Significant difference |

### Clipping

If one file shows clipping and the other doesn't, consider why:
- Overprocessing during mastering?
- Source file issues?

### Stereo/Mono Compatibility

If your mix isn't mono compatible but your reference is:
- Check for phase issues between stereo channels
- Review any stereo widening plugins

## Use Cases

### 1. Tracking Mix Progress

Compare v1 and v2 of your mix:

```bash
python 02_mix_comparison.py mix_v1.wav mix_v2.wav ROCK
```

### 2. Matching a Reference

Compare your mix to a commercial release:

```bash
python 02_mix_comparison.py my_mix.wav reference_track.wav POP
```

### 3. A/B Testing Mastering

Compare two different mastering approaches:

```bash
python 02_mix_comparison.py master_warm.wav master_bright.wav ELECTRONIC --is-master
```

## Programmatic Usage

```python
from shared import TonnClient

client = TonnClient()

# Upload both files
url_a = client.upload_local_file("mix_a.wav")
url_b = client.upload_local_file("mix_b.wav")

# Analyze both
results = {}
for label, url in [("A", url_a), ("B", url_b)]:
    response = client.post("/mixanalysis", {
        "mixDiagnosisData": {
            "audioFileLocation": url,
            "musicalStyle": "POP",
            "isMaster": True
        }
    })
    results[label] = response.get("mixDiagnosisResults", {})

# Compare specific metrics
loudness_a = results["A"].get("payload", {}).get("integrated_loudness_lufs")
loudness_b = results["B"].get("payload", {}).get("integrated_loudness_lufs")

print(f"Loudness difference: {abs(loudness_a - loudness_b):.1f} LUFS")
```

## Tips for Better Comparisons

1. **Use the same musical style** for both tracks
2. **Compare like with like** (both mixes or both masters)
3. **Consider the source quality** - different sample rates affect results
4. **Don't over-optimize** - trust your ears alongside the data

## Support

For questions or feedback:
- Visit [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- Contact: support@roexaudio.com

