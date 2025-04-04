import os
import time
import requests

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "YOUR_API_KEY_HERE"

HEADERS = {
    "Content-Type": "application/json",
    # If your API expects "Authorization: Bearer <token>", do:
    # "Authorization": f"Bearer {API_KEY}",
    # Otherwise, if the API uses an x-api-key:
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
# 1) Start the Mix Enhance process
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
        stem_processing=False,
        webhook_url=""
):
    """
    Calls /mixenhance with the specified parameters.
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

    print(f"Requesting mix enhance for: {audio_url}")
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
    except Exception as e:
        print(f"Error calling /mixenhance: {e}")
        return None

    if response.status_code == 200:
        data = response.json()
        if not data.get("error", False):
            task_id = data.get("mixrevive_task_id")
            print(f"Mix Enhance task created. Task ID: {task_id}")
            return task_id
        else:
            print(f"API returned error: {data.get('message')}")
            return None
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")
        return None


# -------------------------------------------------------------------
# 2) Poll for Results
# -------------------------------------------------------------------
def poll_enhanced_track(task_id, max_attempts=20, poll_interval=5):
    """
    Calls /retrieveenhancedtrack in a loop to check if the track is ready.
    Returns the 'revived_track_tasks_results' dict if successful, otherwise None.

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
                        print("Got 200 but no results yet. Will keep polling.")
                else:
                    print(f"API returned error while retrieving track: {data.get('message')}")
                    # Typically, you'd break or return None if there's a real error.
                    # We'll break here to avoid infinite loops.
                    break
            except Exception as e:
                print(f"Error parsing JSON response: {e}")
                break
        elif response.status_code in (404, 503, 202):
            # Possibly not ready or still processing
            print(f"Attempt {attempt + 1}/{max_attempts}: status={response.status_code}, still processing...")
        else:
            print(f"Unexpected status {response.status_code}: {response.text}")
            break

        # Wait then try again
        time.sleep(poll_interval)

    print("Track was not ready after max polling attempts. Check logs or try again later.")
    return None


# -------------------------------------------------------------------
# 3) Example Flow
# -------------------------------------------------------------------
def main():
    """
    Demonstrates how to:
      - Start a mix enhance job with optional parameters
      - Poll until the track is ready
      - Download the final files
    """

    # Example input audio file
    demo_audio_url = "https://example.com/path/to/my_mix.wav"

    # Start a job. Provide custom flags as needed:
    task_id = start_mix_enhance(
        audio_url=demo_audio_url,
        musical_style="HIPHOP_GRIME",
        is_master=False,
        fix_clipping=True,
        fix_drc=True,
        fix_stereo=True,
        fix_tonal=True,
        fix_loudness=True,
        apply_mastering=True,
        loudness_preference="STREAMING_LOUDNESS",
        stem_processing=True,  # request stems
    )

    if not task_id:
        print("Failed to create mix enhance task. Exiting.")
        return

    # Poll for completion
    results = poll_enhanced_track(task_id, max_attempts=50, poll_interval=5)
    if not results:
        print("No results returned. Exiting.")
        return

    # The results should include URLs for the enhanced track and optional stems
    print("Final results from /retrieveenhancedtrack:")
    print(results)

    # Example keys your backend might return:
    #   "preview_url", "enhanced_full_track_url", "stems"
    # Let's attempt to download them if present
    enhanced_url = results.get("download_url_revived")
    if enhanced_url:
        download_file(enhanced_url, "enhanced_full_track.wav")

    stems = results.get("stems", {})
    for stem_name, stem_link in stems.items():
        local_stem_filename = f"enhanced_stem_{stem_name}.wav"
        download_file(stem_link, local_stem_filename)

    print("Done!")


if __name__ == "__main__":
    main()
