
<!-- focus: false -->
![tutorial-icon](https://img.icons8.com/cotton/128/000000/abc.png)

# Tutorial - Tonn API: Automating Audio Mixing

## Introduction
Imagine you have multiple audio tracks recorded separately—instruments like drums, bass, guitar, plus vocals—and you need a professional mix that balances them seamlessly.  The **Tonn API** allows you to automate this process, ensuring clarity, depth, and consistency in your audio mix. This guide will walk you through:
- Creating a **preview mix** to test your setup
- Polling for **mix status updates** so you know when it's ready
- Using **webhooks** instead of polling for real-time updates
- Retrieving the **final mix** for your production
- Extracting **audio effect settings** for fine-tuning
- Adjusting **track levels** in decibels before finalizing the mix

## Why Use the Tonn API?
Mixing music manually can be time-consuming and technically challenging. Whether you're an independent musician, producer, or developer integrating audio features into an application, the Tonn API provides an easy way to get professional-quality mixes in just a few steps.

## Prerequisites
Before you begin, make sure you have:
- Python installed on your system
- The `requests` library (`pip install requests`)
- A valid API key for authentication

## Base API URL
All API requests should be made to:

```
https://tonn.roexaudio.com
```

## Step 1: Creating a Preview Mix
The first step is to send your tracks to the API and create a preview mix. This mix lets you hear how your tracks sound together before committing to a final mix.

### How It Works
When you send a `POST` request to `/mixpreview`, the API takes your tracks, applies professional mixing techniques, and generates a preview mix. This step doesn’t consume any credits, allowing you to tweak and experiment freely.

Including a `webhookURL` in your request payload is **mandatory**. This ensures you receive a notification when the preview mix is ready, eliminating the need for polling.

### Endpoint Details
- **Endpoint**: `POST /mixpreview`
- **Consumes**: `application/json`
- **Response Codes**:
  - `200`: Success, returns `multitrack_task_id`
  - `400`: Bad Request (Invalid input)
  - `401`: Unauthorized (API key missing/invalid)
  - `500`: Internal Server Error

### Example JSON Payload with Webhook
Save this as `preview_payload.json`:

```json
{
  "multitrackData": {
    "trackData": [
      {
        "trackURL": "https://example.com/vocals.wav",
        "instrumentGroup": "VOCAL_GROUP",
        "presenceSetting": "LEAD",
        "panPreference": "CENTRE",
        "reverbPreference": "LOW"
      },
      {
        "trackURL": "https://example.com/drums.wav",
        "instrumentGroup": "DRUMS_GROUP",
        "presenceSetting": "NORMAL",
        "panPreference": "CENTRE",
        "reverbPreference": "NONE"
      }
    ],
    "musicalStyle": "POP",
    "returnStems": false,
    "sampleRate": 44100,
    "webhookURL": "https://example.com/webhook"
  }
}
```

## Step 2: Polling for Preview Mix Completion (For Debugging)
Polling is generally not required since webhooks provide real-time updates. However, you can use polling as a backup method for debugging or verifying status manually.

### Retrieving Mix Output Settings
Once the preview mix is complete, the API returns **mix output settings** for each track, including:
- **Dynamic range compression (DRC) settings**
- **Equalization (EQ) settings**
- **Gain adjustments**
- **Panning preferences**

#### Example of Mix Output Settings
```plaintext
Track: masks-bass.wav
  drc_settings:
    attack_ms: 0.074
    ratio: 1.8
    release_ms: 0.022
    threshold: -3.89
  eq_settings:
    band_1: {"centre_freq": 46.5, "gain": -1.69, "q": 2.66}
    band_2: {"centre_freq": 96.69, "gain": -2.73, "q": 2.42}
  gain_settings:
    gain_db: -11.8
```
These settings allow you to fine-tune the mix before finalizing it.

### Step 3: Adjusting Track Levels & Retrieving the Final Mix
Once you’re happy with the preview mix, you can send adjustments for individual track levels before retrieving the final mix.

### Example JSON Payload
Save this as `final_payload.json`:

```json
{
  "applyAudioEffectsData": {
    "multitrackTaskId": "TASK_ID_HERE",
    "trackData": [
      {
        "trackURL": "https://example.com/vocals.wav",
        "gainDb": 0.0
      },
      {
        "trackURL": "https://example.com/drums.wav",
        "gainDb": -2.0
      }
    ],
    "returnStems": false,
    "sampleRate": 44100
  }
}
```

## Conclusion
By following these steps, you can effortlessly automate professional-quality mixing with the **Tonn API**. 
- Start with a **preview mix**.
- Use **webhooks** to receive real-time notifications when the mix is ready.
- Extract **mix output settings** to analyze how the API processed each track.
- Adjust **track levels** to refine the final mix.

Whether you're developing a music app or mixing tracks at scale, this API streamlines your workflow. For more customization, check out the full API documentation!

---


# Tutorial - Tonn API: Batch Mastering Your EP or Album

When releasing an EP or album independently, achieving consistent sound quality and loudness across tracks can be challenging and time-consuming. Automating the mastering process not only saves time but ensures sonic consistency throughout your project, providing listeners with a cohesive experience. Batch mastering is just one of the many powerful uses of the Tonn API, designed to streamline various audio production workflows.

## Why Batch Mastering?

Mastering an album or EP track-by-track can lead to inconsistent loudness levels and sonic character, causing your project to lose coherence. Batch mastering allows you to set consistent mastering parameters across your entire project, ensuring uniform loudness, style, and sound quality.

## Getting Started

### Prerequisites

Before you begin, you'll need:

- Python installed on your machine ([Download here](https://www.python.org/downloads/))
- The `requests` Python package (`pip install requests`)
- An API key from [Tonn API Portal](https://tonn-portal.roexaudio.com)

## Preparing Your Tracks

Create a JSON file named `album_mastering_payload.json`. Each track requires:

- `trackURL`: URL of your track file (WAV, MP3, or FLAC).
- `musicalStyle`: Genre-specific mastering preset (e.g., ROCK_INDIE, POP, ELECTRONIC).
- `desiredLoudness`: Desired loudness level (LOW, MEDIUM, or HIGH).
- `sampleRate`: Optional, defaults to "44100".
- `webhookURL`: URL to receive API callbacks (useful for automated systems).

Here's an example:

```json
[
  {
    "trackURL": "https://example.com/track1.wav",
    "musicalStyle": "ROCK_INDIE",
    "desiredLoudness": "MEDIUM",
    "sampleRate": "44100",
    "webhookURL": "https://yourwebhook.com/track1"
  },
  {
    "trackURL": "https://example.com/track2.flac",
    "musicalStyle": "POP",
    "desiredLoudness": "HIGH",
    "sampleRate": "48000",
    "webhookURL": "https://yourwebhook.example.com/track2"
  }
]
```

## Python Script for Batch Mastering

Place this Python script (`batch_master_album.py`) in the same directory as your JSON file:

### Python Script Explanation

This script automates:
- Creating mastering tasks
- Polling the API until your previews are ready
- Retrieving and downloading your final mastered tracks

### Script Usage

Replace `API_KEY` with your API key from Tonn.

```python
import os
import requests
import json
import time

BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "YOUR_API_KEY_HERE"

# (Include the functions provided earlier: download_file, poll_preview_master, retrieve_final_master)

# See the provided code snippet in this tutorial's earlier sections.

# Main function to batch master an EP or Album
# (The main function from your provided code snippet goes here.)
```

### Running the Script

Ensure your `album_mastering_payload.json` is correctly filled out, and then run:

```bash
python batch_master_album.py
```

This script will:

- Start mastering each track (preview first).
- Poll regularly until the preview is ready.
- Retrieve the preview URL for you to check the mastering quality.
- Automatically download each final mastered track into a directory named `final_masters`.

## Listening & Checking Results

Your mastered tracks will be downloaded into a directory named `final_masters`. It's crucial to listen critically to each mastered track and ensure they meet your expectations for loudness, tonal balance, and cohesiveness.

## Tips for Optimal Results

- **Consistent Loudness**: Choose the same loudness level (`MEDIUM` is typically industry-standard at around -14 LUFS) across all tracks for a cohesive listening experience.
- **Musical Style Accuracy**: Carefully select the musical style to match your project accurately; this ensures genre-specific optimizations are applied.
- **Sample Rate Considerations**: Choose `44100` Hz (standard CD/audio distribution) or `48000` Hz (typical for video production and higher-resolution streaming).

## Explore More with Tonn API

Batch mastering is just one of many use-cases available with the Tonn API. You can also leverage Tonn to automate audio mixing, generate previews, handle multitrack projects, and integrate professional-quality audio processing into your custom applications and workflows.

## Conclusion

Batch mastering your EP or album ensures a unified and professional sound, making your music stand out to listeners and industry professionals alike. By using the provided Python script and Tonn’s mastering API, you can achieve professional-quality mastering efficiently, freeing up your time to focus on creativity and promotion.

---


# Mix Check Studio - Mix Analysis Tutorial

This guide explains how to use the **Tonn API** to analyse your mixed or mastered tracks, ensuring they are polished and ready for release on streaming platforms.

The code for this tutorial is available in the following code repository: https://github.com/roex-audio/TonnExamples

Using Tonn API for Mix Analysis leverages the same advanced technology behind RoEx's [Mix Check Studio](https://mixcheckstudio.roexaudio.com), which has already been used by DIY musicians and producers on 100,000's of tracks.

## What is Mix Check Studio?

**Mix Check Studio** analyses your music tracks to identify potential issues in your mix or master, providing detailed feedback on loudness, dynamic range, clipping, stereo field, tonal profile, and more. This allows you to make informed adjustments before your music reaches listeners.

## Why Analyse Your Tracks?

Before releasing music, it's crucial to ensure your tracks meet industry standards. Mix Check Studio helps by highlighting:

- **Clipping issues**: Detects unwanted distortion or peaks that may degrade audio quality.
- **Dynamic range issues**: Evaluates compression levels to ensure appropriate dynamics.
- **Loudness**: Analyses how your track's loudness compares to standards set by Spotify, Apple Music, and YouTube.
- **Stereo field and mono compatibility**: Assesses stereo imaging, ensuring your music sounds great on all devices.
- **Tonal balance**: Offers insights to enhance warmth, clarity, and overall sonic presence.

## Step-by-Step Tutorial

### 1. Prerequisites

Ensure you have:

- An API key from [Tonn API Portal](https://tonn-portal.roexaudio.com).
- An audio file hosted online (accessible via URL).
- Python environment setup with `requests` library installed (`pip install requests`).

### 2. Prepare Your Request

Create a payload containing:

```json
{
    "mixDiagnosisData": {
        "audioFileLocation": "https://your-audio-file-location/audiofile.wav",
        "musicalStyle": "ROCK",
        "isMaster": true
    }
}
```

Replace the `audioFileLocation` URL with your track's location, choose the appropriate `musicalStyle`, and set `isMaster` accordingly.

### 3. Run the Analysis

Use the provided Python script (`roex_mix_analysis.py`) to submit your track:

```bash
python roex_mix_analysis.py
```

### 4. Interpreting Results

Upon running the script, you'll receive detailed output similar to this example:

```
=== Mix Analysis Top-Level Response ===
Error: False
Message: Successfully initiated a diagnosis task.

=== Mix Diagnosis Results ===
Completion Time: 2025-03-17 11:05:18
Error Flag: False

--- Payload Details ---
bit_depth: 24
clipping: MINOR
if_master_drc: LESS
if_master_loudness: LESS
integrated_loudness_lufs: -8.88
mono_compatible: True
musical_style: hip_hop_grime
peak_loudness_dbfs: 1.3
phase_issues: False
sample_rate: 44100
stereo_field: STEREO_UPMIX

--- Summary ---
1. Minor clipping detected; use a limiter to control peaks.
2. Dynamic range is limited; avoid heavy compression.
3. Loudness exceeds streaming standards by 5.1 dB (Spotify, Tidal, YouTube) and 7.1 dB (Apple Music).
4. Recommended EQ adjustments: boost low-mid frequencies for warmth; subtle boosts in high-mid and highs for clarity; apply multiband compression to balance tonal profile.

Remember: Use this analysis as guidance. Always trust your ears for final decisions.
```

### 5. Improving Your Mix

You can use this feedback to go back to the DAW make changes to improve how it sounds based on the recommendations given. For example:

- Adjust your track's loudness and dynamic range.
- Correct any minor clipping using a limiter.
- Enhance the tonal profile and stereo image.

### 6. Next Steps

After addressing the feedback:

- Re-run your mix through Mix Check Studio.
- Compare results to ensure improvements.
- Confidently release your music knowing it meets professional standards.

## Support

For further assistance, please visit the [Tonn API Portal](https://tonn-portal.roexaudio.com) or contact our support team at support@roexaudio.com.

---

# Tutorial - Tonn API: Compare Two Mixes Using the Tonn API

This guide explains how to use the **Tonn API** to compare two different versions of a mix or reference tracks, allowing you to assess progress, consistency, or alignment with a sonic benchmark.

The code for this tutorial is available in the following repository: https://github.com/roex-audio/TonnExamples

This tool leverages the same technology that powers [Mix Check Studio](https://mixcheckstudio.roexaudio.com), already trusted by DIY musicians and producers for hundreds of thousands of tracks.

## What is Mix Comparison?

**Mix Comparison** allows you to:

- Compare two different versions of your mix to track improvements.
- Benchmark your mix against a professionally released track.

Using the Tonn API, you'll receive feedback on loudness, dynamic range, stereo image, tonal profile, and technical delivery.

## Why Compare Mixes?

Whether you're refining your sound or preparing a release, comparison helps ensure:

- **Improved sound quality**: Know if your changes are actually better.
- **Reference-based mixing**: Match the clarity and energy of tracks you admire.
- **Consistency across versions**: Spot regressions or overprocessing early.

## Step-by-Step Tutorial

### 1. Prerequisites

You’ll need:

- An API key from [Tonn API Portal](https://tonn-portal.roexaudio.com)
- Two audio files hosted online (public URLs)
- Python environment with `requests` installed (`pip install requests`)

### 2. Configure the Script

Edit the following values in `compare_mixes.py`:

```python
mix_a_url = "https://your-audio-file-location/mix_a.wav"
mix_b_url = "https://your-audio-file-location/mix_b.wav"

musical_style = "POP"  # e.g. techno, pop, hip_hop_grime
is_master = True         # Set to False if you're comparing unmastered mixes
```

And don’t forget to insert your Tonn API key:

```python
API_KEY = "YOUR_API_KEY_HERE"
```

### 3. Run the Script

Use the terminal:

```bash
python compare_mixes.py
```

### 4. Understanding the Output

The script will:

- Analyze both audio files using the `/mixanalysis` endpoint.
- Extract key technical fields (bit depth, LUFS, mono compatibility, etc.).
- Show side-by-side, color-coded comparisons.
- Highlight significant differences with basic interpretation.

Example:

```
=== Production Metrics Comparison ===
integrated_loudness_lufs:
  Mix A: -13.3
  Mix B: -10.9
  Interpretation: Difference of 2.4 exceeds threshold of 1.0

mono_compatible:
  Mix A: False
  Mix B: True
  Interpretation: Values differ.

bit_depth:
  Mix A: 16
  Mix B: 24
  Interpretation: Difference of 8 exceeds threshold of 0
```

You’ll also get a breakdown of tonal profile differences:

```
=== Tonal Profile Comparison ===
high_frequency:
  Mix A: LOW
  Mix B: MEDIUM
  Interpretation: Values differ.
```

### 5. What Gets Compared?

#### Technical Metrics:
- Bit depth
- Clipping
- Loudness (LUFS, peak)
- DRC evaluations
- Mono compatibility
- Stereo field and phase issues
- Sample rate

#### Tonal Profile:
- Bass frequency content
- Low-mid, high-mid, and high frequency energy

### 6. Using the Results

Use the comparison output to:

- Revisit mix decisions (e.g., loudness, stereo spread, EQ)
- Match a reference track more closely
- Track whether your changes help or hinder the mix

After you’ve made changes:

- Re-run the script
- Compare the new version to your previous one or reference
- Iterate confidently with data-backed decisions

## License & Attribution

This tutorial uses the Tonn API, part of the RoEx platform. These insights are algorithmically generated, and should always be used alongside your ears and taste.

---

Confidently improve your mixes. Try it now.
