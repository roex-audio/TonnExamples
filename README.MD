
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
