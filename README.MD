
<!-- focus: false -->
![tutorial-icon](https://img.icons8.com/cotton/128/000000/abc.png)

# 🎚️ Advanced Audio Effects Now Available!

The Tonn API now supports **extensive per-track audio processing** for professional mixing:

- **Panning**: Position tracks in stereo field (-60° to +60°)
- **6-Band Parametric EQ**: Precise frequency shaping (20Hz - 20kHz)
- **Compression**: Dynamic range control with threshold, ratio, attack & release
- **Gain Control**: Level adjustment per track (-60 to +12 dB)

📘 **See [AUDIO_EFFECTS_GUIDE.md](AUDIO_EFFECTS_GUIDE.md) for complete documentation and examples**

**Example Files:**
- `final_mix_settings.json` - Standard balanced mix
- `final_mix_settings_alternative.json` - Alternative processing approach
- `roex_mix_settings.py` - Updated script with audio effects visualization

---

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

---


# Tutorial Tonn API - Mix Enhance

Welcome to the Mix Enhance tutorial! This guide walks you through quickly enhancing and mastering your audio tracks using RoEx's Mix Enhance technology API. You'll learn how to easily transform existing stereo mixes into polished, studio-quality tracks without needing individual stems.

## What Makes Mix Enhance Special?

- **No Stems Required**: Mix Enhance operates directly on stereo files, saving you from the hassle of exporting separate stems from your DAW.
- **Studio-Grade Enhancement**: Inspired by classic analog gear like the Pultec EQ and LA-2A Compressor, Mix Enhance instantly adds clarity, warmth, punch, and brightness to your tracks.
- **Optimized for Streaming**: Automatically adjust your mixes to meet the loudness and quality standards required by popular streaming services like Spotify and Apple Music.
- **Flexible Stem Separation**: Optionally, Mix Enhance can perform stem separation and return individually processed stems, ideal for reviving old tracks or lost projects.

## What You'll Learn in This Tutorial

- **Preview your mix enhancement** quickly to hear a short sample before committing to a full enhancement.
- **Fully enhance your mix** by automatically correcting common mixing issues and mastering your track.
- **Retrieve and download** your enhanced tracks and individual stems effortlessly.

## Getting Started

### Prerequisites

- Python installed on your system (version 3.7 or higher recommended).
- Your Mix Enhance API Key (obtain from [Tonn Portal](https://tonn-portal.roexaudio.com)).

### Installation

Make sure you have the `requests` library installed:

```bash
pip install requests
```

### Using the Tutorial Script

1. **Configure your API Key and Base URL:**

Update these lines in your Python script with your API details:

```python
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "YOUR_API_KEY_HERE"
```

2. **Specify Your Audio File and Preferences:**

Replace the placeholder audio URL in the script with the URL of the track you want to process. Select the appropriate musical style and set flags to indicate whether you want the API to fix loudness, stereo width, tonal profile, and perform mastering (especially recommended for unmastered mixes).

```python
demo_audio_url = "https://example.com/path/to/your_track.wav"  # Replace with your audio file URL
musical_style = "POP"  # Choose from available styles
fix_loudness = True
fix_stereo_width = True
fix_tonal_profile = True
apply_mastering = True
```

3. **Run the Tutorial Script:**

Execute the provided Python script:

```bash
python mix_enhance_tutorial.py
```

The script performs two steps:

- **Preview Enhancement:** Quickly generates a short sample of your enhanced track.
- **Full Enhancement:** Applies complete mixing and mastering with detailed fixes, returning the fully enhanced track and optional stems.

### Understanding the Script Workflow

The tutorial script follows these clear steps:

1. **Preview Request:** Sends your audio file URL to the `/mixenhancepreview` endpoint with specified enhancement parameters.
2. **Polling for Results:** Periodically checks if your preview enhancement is ready.
3. **Download Preview:** Automatically downloads the preview audio and optional stems.
4. **Full Enhancement Request:** Sends another request to the `/mixenhance` endpoint for comprehensive enhancement.
5. **Polling for Final Results:** Checks periodically until the full enhanced track is available.
6. **Download Final Tracks and Stems:** Downloads your fully enhanced mix along with individually processed stems if requested.

## Example Use Cases

- **Bedroom Producers:** Enhance your mixes to a professional standard quickly, letting you focus more on creativity.
- **Artists and Labels:** Revive and optimize older tracks for modern streaming platforms without remixing or accessing original sessions.
- **Mastering Engineers:** Accelerate workflows with automated fixes, allowing more time for creative fine-tuning.

## Tips for Advanced Users

- **Webhooks:** Supply a webhook URL in your requests to receive asynchronous notifications, eliminating the need for manual polling.
- **Batch Processing:** Adapt the script to handle multiple tracks simultaneously.
- **Customizing Loudness:** Choose between `STREAMING_LOUDNESS` and `CD_LOUDNESS` settings to meet your distribution needs.

## Next Steps

Feel free to adapt and expand this script for your specific workflows. Integrate it into your music production pipelines and experience how AI-driven technology simplifies audio production.

## Questions or Feedback?

For support, visit our [Tonn Portal](https://tonn-portal.roexaudio.com) or contact our team directly—we’re here to help!

__


# Tutorial - Tonn API: Audio Clean-up

In this tutorial, we'll walk through how to use RoEx's **audio cleanup API** to clean up noisy, problematic instrument tracks, specifically vocals. Whether you're a producer, podcaster, or content creator, this tool helps you clean up your recordings quickly and efficiently.

## Why Audio Cleanup?

Audio recordings, especially those captured in uncontrolled environments (like outdoor spaces or mobile phones), often contain unwanted noise or imperfections. These issues can make your track sound unprofessional and detract from the overall listening experience. This is where the **audio cleanup API** can help.

With just a few clicks, the RoEx API will process your audio and clean up background noise, microphone bleed, and other imperfections.

### Common Use Cases:
- **Outdoor Recordings:** Wind, traffic, and environmental noises often seep into recordings made outdoors. Our API can help clean up these recordings, leaving only the desired sounds.
- **Phone Recordings:** If you've recorded vocals or instruments using a phone or portable device, there’s a high chance that unwanted noise has been captured. The API can help clean up this noise while maintaining the integrity of the main sound.
- **Microphone Bleed:** During live performances or multi-microphone setups, sound from other sources can bleed into your recording. The API can isolate and clean up specific instrument groups, ensuring a cleaner sound.
- **Noisy Recordings:** Sometimes, even in controlled environments, recordings can have hum, hiss, or other unwanted sounds. The API can help reduce these noises and improve the overall sound quality.

## Benefits of Using the RoEx Audio Cleanup API

- **Time-Saving:** Manually cleaning up audio files can be time-consuming. RoEx's API automates the process, saving you hours of work.
- **High-Quality Results:** The API uses advanced machine learning models and signal processing techniques to clean up your audio without compromising quality.
- **Versatility:** Whether you're working with vocals, drums, guitars, or strings, the API supports a variety of instrument groups, making it a versatile tool for different audio projects.
- **Easy to Use:** With just a simple API call, you can submit an audio file for cleanup and download the results in minutes.

## How to Use the Audio Cleanup API

### Step 1: Prepare Your Audio File

Before you start, ensure that your audio file is in either **WAV** or **FLAC** format. These are the only supported formats for cleanup, as they preserve high audio quality, which is necessary for processing.

You can use the API to clean up:
- **Vocals**
- **Drums**
- **Electric and Acoustic Guitars**
- **Strings**
- **Percussion**
- **Backing Vocals**

### Step 2: Make the API Call

You’ll need to send a POST request to the `/audio-cleanup` endpoint. This request will include:
- **audioFileLocation:** The URL of the audio file you want to clean.
- **soundSource:** The specific instrument you want to clean (e.g., "VOCAL_GROUP", "SNARE_GROUP").

Here’s a sample payload for cleaning up vocals:

```json
{
  "audioCleanupData": {
    "audioFileLocation": "https://your-audio-file-location/vocal_track.wav",  // Replace with your file URL
    "soundSource": "VOCAL_GROUP"  // Choose the appropriate group like SNARE_GROUP, E_GUITAR_GROUP, etc.
  }
}
```

### Step 3: Download the Cleaned Audio

Once the API processes the file, it will provide a download link to the cleaned-up audio. You can then download the file to your local machine.

### Step 4: Review the Results

After downloading the cleaned audio, listen to the before-and-after results to evaluate the improvement. You'll notice a cleaner, more professional sound with reduced noise, hums, and unwanted sounds.

## Python Example Script

Here’s a Python script to help you get started with using the RoEx Audio Cleanup API:

```python
import requests
import json

BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "Your_API_Key_Here"

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded file to {local_filename}")

def clean_up_audio(payload, headers):
    cleanup_url = f"{BASE_URL}/audio-cleanup"
    response = requests.post(cleanup_url, json=payload, headers=headers)
    return response.json() if response.status_code == 200 else None

def main():
    cleanup_payload = {
        "audioCleanupData": {
            "audioFileLocation": "https://your-audio-file-location/vocal_track.wav",
            "soundSource": "VOCAL_GROUP"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    response_data = clean_up_audio(cleanup_payload, headers)
    if response_data:
        cleanup_results = response_data.get("audioCleanupResults")
        if cleanup_results:
            download_url = cleanup_results.get("download_url")
            if download_url:
                print(f"Download URL: {download_url}")
                download_file(download_url, "cleaned_audio.wav")
```

This script demonstrates how to send a POST request to the API, process the audio file, and download the cleaned results.

## Conclusion

By leveraging the RoEx Audio Cleanup API, you can automate the process of cleaning up your audio files and achieve professional-level results in just a few simple steps. Whether you're working with outdoor recordings, phone recordings, or live performance tracks, this tool will help you save time and produce cleaner, more polished audio.

We hope this tutorial helps you get started with the API. If you have any questions or feedback, feel free to reach out or share your results!

---

### Related Resources:

- [RoEx API Documentation](https://tonn.roexaudio.com/docs)
- [API Key Registration](https://tonn-portal.roexaudio.com)

Happy audio cleaning! 🎶
