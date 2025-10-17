import os
import time
import requests

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
import os
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = os.environ.get("TONN_API_KEY", "YOUR_API_KEY_HERE")

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    print("Error: TONN_API_KEY environment variable not set.")
    print("GO TO https://tonn-portal.roexaudio.com to get an API key")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    # If your API expects "Authorization: Bearer <token>", do:
    # "Authorization": f"Bearer {API_KEY}",
    # Otherwise, if the API uses x-api-key:
    "x-api-key": API_KEY
}


# -------------------------------------------------------------------
# Utility: Download File
# -------------------------------------------------------------------
def download_file(url, local_filename):
    """
    Downloads a file from 'url' and saves it locally to 'local_filename'.
    """
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded file to {local_filename}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")


# -------------------------------------------------------------------
# 1) Start a Mix Enhance **Preview** job (via /mixenhancepreview)
# -------------------------------------------------------------------
def start_mix_enhance_preview(
        audio_url,
        musical_style="POP",
        is_master=False,
        fix_clipping=True,
        fix_drc=True,
        fix_stereo=True,
        fix_tonal=True,
        fix_loudness=True,
        apply_mastering=True,
        loudness_preference="STREAMING_LOUDNESS",
        stem_processing=False
):
    """
    Calls /mixenhancepreview with the specified parameters for a PREVIEW version.
    Returns the task ID if successful.
    """
    endpoint = f"{BASE_URL}/mixenhancepreview"
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": is_master,
            "fixClippingIssues": fix_clipping,
            "fixDRCIssues": fix_drc,
            "fixStereoWidthIssues": fix_stereo,
            "fixTonalProfileIssues": fix_tonal,
            "fixLoudnessIssues": fix_loudness,
            "applyMastering": apply_mastering,
            "loudnessPreference": loudness_preference,
            "stemProcessing": stem_processing
        }
    }

    print(f"Requesting PREVIEW enhancement for: {audio_url}")
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
    except Exception as e:
        print(f"Error calling /mixenhancepreview: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        if not data.get("error", False):
            task_id = data.get("mixrevive_task_id")
            print(f"Preview task created. Task ID: {task_id}")
            return task_id
        else:
            print(f"API returned error: {data.get('message')}")
            return None
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")
        return None


# -------------------------------------------------------------------
# 2) Start a Mix Enhance **Full** job (via /mixenhance)
# -------------------------------------------------------------------
def start_mix_enhance(
        audio_url,
        musical_style="POP",
        is_master=False,
        fix_clipping=True,
        fix_drc=True,
        fix_stereo=True,
        fix_tonal=True,
        fix_loudness=True,
        apply_mastering=True,
        loudness_preference="STREAMING_LOUDNESS",
        stem_processing=False
):
    """
    Calls /mixenhance with the specified parameters for a FULL track enhancement.
    Returns the task ID if successful.
    """
    endpoint = f"{BASE_URL}/mixenhance"
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": is_master,
            "fixClippingIssues": fix_clipping,
            "fixDRCIssues": fix_drc,
            "fixStereoWidthIssues": fix_stereo,
            "fixTonalProfileIssues": fix_tonal,
            "fixLoudnessIssues": fix_loudness,
            "applyMastering": apply_mastering,
            "loudnessPreference": loudness_preference,
            "stemProcessing": stem_processing
        }
    }

    print(f"Requesting FULL mix enhancement for: {audio_url}")
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
    except Exception as e:
        print(f"Error calling /mixenhance: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        if not data.get("error", False):
            task_id = data.get("mixrevive_task_id")
            print(f"Full Enhance task created. Task ID: {task_id}")
            return task_id
        else:
            print(f"API returned error: {data.get('message')}")
            return None
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")
        return None


# -------------------------------------------------------------------
# 3) Poll for Results (via /retrieveenhancedtrack)
# -------------------------------------------------------------------
def poll_enhanced_track(task_id, max_attempts=70, poll_interval=5):
    """
    Calls /retrieveenhancedtrack in a loop to check if the track is ready.
    Returns the 'revivedTrackTaskResults' dict if successful, otherwise None.

    Adjust the logic (especially on which status codes to treat as "still processing")
    based on your server's actual responses.
    """
    endpoint = f"{BASE_URL}/retrieveenhancedtrack"
    payload = {
        "mixReviveData": {
            "mixReviveTaskId": task_id
        }
    }

    print(f"Polling for enhanced track with task ID: {task_id}")
    for attempt in range(max_attempts):
        try:
            response = requests.post(endpoint, json=payload, headers=HEADERS)
        except Exception as e:
            print(f"Error calling /retrieveenhancedtrack: {e}")
            return None

        if response.status_code == 200:
            # Possibly it's ready!
            try:
                data = response.json()
                if not data.get("error", False):
                    results = data.get("revivedTrackTaskResults", {})
                    if results:
                        print("Enhanced track is ready!")
                        return results
                    else:
                        print("Got 200 but 'revivedTrackTaskResults' was empty. Will keep polling.")
                else:
                    print(f"API returned error while retrieving track: {data.get('message')}")
                    break
            except Exception as e:
                print(f"Error parsing JSON response: {e}")
                break

        # Possibly not ready or still processing
        elif response.status_code in (404, 503, 202):
            print(f"Attempt {attempt + 1}/{max_attempts}: status={response.status_code}, still processing...")
        else:
            print(f"Unexpected status {response.status_code}: {response.text}")
            break

        time.sleep(poll_interval)

    print("Track was not ready after max polling attempts. Check logs or try again later.")
    return None


# -------------------------------------------------------------------
# 4) Example Flow: Preview, Then Full
# -------------------------------------------------------------------
def main():
    """
    Demonstrates how to:
      1. Start a PREVIEW job via /mixenhancepreview
      2. Poll until it's ready
      3. Download the preview track (and stems if available)
      4. Start a FULL job via /mixenhance
      5. Poll until the final track is ready
      6. Download final track (and stems if available)
    """

    # Example input audio file - use one from test bucket
    demo_audio_url = "https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3"

    # =====================================================
    # (A) Start the PREVIEW job
    # =====================================================
    preview_task_id = start_mix_enhance_preview(
        audio_url=demo_audio_url,
        musical_style="HIPHOP_GRIME",
        is_master=False,
        fix_clipping=True,
        fix_drc=True,
        fix_stereo=True,
        fix_tonal=True,
        fix_loudness=True,
        apply_mastering=True,               # For a quick preview with mastering
        loudness_preference="STREAMING_LOUDNESS",
        stem_processing=False               # Also test stem splitting in preview
    )

    if not preview_task_id:
        print("Failed to create PREVIEW task. Exiting.")
        return

    # Poll for completion
    preview_results = poll_enhanced_track(preview_task_id, max_attempts=70, poll_interval=5)
    if not preview_results:
        print("No preview results returned. Exiting.")
        return

    print("\n--- PREVIEW RESULTS ---")
    print(preview_results)

    # Download the preview track if present
    preview_track_url = (
        preview_results.get("download_url_preview_revived")
    )
    if preview_track_url:
        download_file(preview_track_url, "enhanced_preview.wav")

    # Download preview stems (if returned)
    preview_stems = preview_results.get("stems", {})
    for stem_name, stem_link in preview_stems.items():
        local_stem_filename = f"enhanced_preview_stem_{stem_name}.wav"
        download_file(stem_link, local_stem_filename)

    # =====================================================
    # (B) Start the FULL job
    # =====================================================
    full_task_id = start_mix_enhance(
        audio_url=demo_audio_url,
        musical_style="HIPHOP_GRIME",
        is_master=False,
        fix_clipping=True,
        fix_drc=True,
        fix_stereo=True,
        fix_tonal=True,
        fix_loudness=True,
        apply_mastering=True,               # For final mastering pass
        loudness_preference="STREAMING_LOUDNESS",
        stem_processing=False               # Request stems again
    )

    if not full_task_id:
        print("Failed to create FULL enhance task. Exiting.")
        return

    # Poll for the final track
    full_results = poll_enhanced_track(full_task_id, max_attempts=50, poll_interval=5)
    if not full_results:
        print("No final results returned. Exiting.")
        return

    print("\n--- FULL ENHANCEMENT RESULTS ---")
    print(full_results)

    # Download the full track if present
    final_track_url = (
        full_results.get("download_url_revived")
    )
    if final_track_url:
        download_file(final_track_url, "enhanced_full_track.wav")

    # Download stems if returned
    final_stems = full_results.get("stems", {})
    for stem_name, stem_link in final_stems.items():
        local_stem_filename = f"enhanced_full_stem_{stem_name}.wav"
        download_file(stem_link, local_stem_filename)

    print("\nAll Done!")


if __name__ == "__main__":
    main()
