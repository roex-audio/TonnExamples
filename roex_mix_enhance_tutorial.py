import os
import requests
import time

# --------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------
BASE_URL = "https://tonn.roexaudio.com"  # or https://api.roexaudio.com, etc.
API_KEY = "YOUR_API_KEY_HERE"

HEADERS = {
    "Content-Type": "application/json",
    # If your API expects "Authorization: Bearer <token>"
    # "Authorization": f"Bearer {API_KEY}",
    # Otherwise, if your API uses x-api-key:
    "x-api-key": API_KEY
}


# --------------------------------------------------------------------------------
# Utility: Download File
# --------------------------------------------------------------------------------
def download_file(url, local_filename):
    """
    Downloads a file from the provided URL and saves it locally in chunks.
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


# --------------------------------------------------------------------------------
# Utility: Polling for Enhanced Track
# --------------------------------------------------------------------------------
def poll_enhanced_track(task_id, max_attempts=30, poll_interval=5):
    """
    Repeatedly calls /retrieveenhancedtrack to check if the track is ready.

    - If we receive 200 with 'revived_track_tasks_results', we assume it's done.
    - If the endpoint returns certain other status codes (e.g., 404), we keep trying,
      up to a maximum of 'max_attempts'.
    - If you have a well-defined "still processing" response, check for that and keep polling.

    Returns:
        dict or None: The dict from 'revived_track_tasks_results' if ready, or None if not ready.
    """
    endpoint = f"{BASE_URL}/retrieveenhancedtrack"
    payload = {
        "mixReviveData": {
            "mixReviveTaskId": task_id
        }
    }

    print(f"Polling /retrieveenhancedtrack for task ID: {task_id}")
    for attempt in range(max_attempts):
        try:
            response = requests.post(endpoint, json=payload, headers=HEADERS)
        except Exception as e:
            print(f"Error during POST to /retrieveenhancedtrack: {e}")
            return None

        # Case 1: 200 => Possibly the track is ready.
        if response.status_code == 200:
            try:
                data = response.json()
                if not data.get("error", False):
                    # If there's no error, we should have 'revived_track_tasks_results'
                    result = data.get("revived_track_tasks_results", {})
                    if result:
                        print("Enhanced track is ready!")
                        return result
                    else:
                        # 200 but no results: maybe your backend hasn't fully updated, or there's another issue.
                        # We can decide if we keep polling or break.
                        # We'll keep polling for this example.
                        print("Got 200 but 'revived_track_tasks_results' was missing. Will retry.")
                else:
                    # If "error" is True, we might want to break or keep trying depending on your logic
                    print(f"API returned an error: {data.get('message')}")
                    # We'll break here, but you could choose to keep polling if you expect it might resolve.
                    break
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                # Decide whether to keep polling or not. We'll break for now.
                break

        # Case 2: 404 => Could mean "still processing" or "invalid ID" depending on your system.
        elif response.status_code == 404:
            print(f"Attempt {attempt + 1}/{max_attempts}: 404 Not Found. Possibly still processing. Retrying...")
        # Case 3: 503 => Could mean "service unavailable" or "still processing"
        elif response.status_code == 503:
            print(f"Attempt {attempt + 1}/{max_attempts}: 503 Service Unavailable. Retrying...")
        else:
            # Handle other status codes
            print(f"Unexpected status {response.status_code}: {response.text}")
            break

        time.sleep(poll_interval)

    print("Enhanced track was not available after polling. Try again later or check logs.")
    return None


# --------------------------------------------------------------------------------
# Endpoint: Start Mix Enhance (Preview)
# --------------------------------------------------------------------------------
def start_mix_enhance_preview(audio_url, musical_style="POP", stem_processing=False, webhook_url=""):
    """
    Calls /mixenhancepreview to request a PREVIEW of the enhanced track.
    Returns the mixrevive_task_id if successful.
    """
    endpoint = f"{BASE_URL}/mixenhancepreview"
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "stemProcessing": stem_processing,
            "webhookURL": webhook_url
        }
    }

    print(f"Requesting preview enhancement for {audio_url}")
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
    except Exception as e:
        print("Error calling /mixenhancepreview:", e)
        return None

    if response.status_code == 200:
        data = response.json()
        if not data.get("error", False):
            return data.get("mixrevive_task_id")
        else:
            print(f"API returned error: {data.get('message')}")
            return None
    else:
        print(f"Preview enhancement request failed with {response.status_code}: {response.text}")
        return None


# --------------------------------------------------------------------------------
# Endpoint: Start Mix Enhance (Full)
# --------------------------------------------------------------------------------
def start_mix_enhance(audio_url, musical_style="POP", stem_processing=False, webhook_url=""):
    """
    Calls /mixenhance to process the FULL mix.
    Returns the mixrevive_task_id if successful.
    """
    endpoint = f"{BASE_URL}/mixenhance"
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "stemProcessing": stem_processing,
            "webhookURL": webhook_url
        }
    }

    print(f"Requesting full mix enhancement for {audio_url}")
    try:
        response = requests.post(endpoint, json=payload, headers=HEADERS)
    except Exception as e:
        print("Error calling /mixenhance:", e)
        return None

    if response.status_code == 200:
        data = response.json()
        if not data.get("error", False):
            return data.get("mixrevive_task_id")
        else:
            print(f"API returned error: {data.get('message')}")
            return None
    else:
        print(f"Full enhancement request failed with {response.status_code}: {response.text}")
        return None


# --------------------------------------------------------------------------------
# Main Demo
# --------------------------------------------------------------------------------
def main():
    """
    Demonstration of:
      1) Requesting a preview enhancement.
      2) Polling until it's ready.
      3) Downloading the resulting file(s).
      4) Requesting a full enhancement.
      5) Polling again and downloading.

    Modify as needed for your real flow, or rely on webhooks for asynchronous completion.
    """

    # Use your own audio file URL
    demo_audio_url = "https://example.com/path/to/your-audio-file.mp3"

    # 1) Start a Preview Job
    preview_task_id = start_mix_enhance_preview(
        audio_url=demo_audio_url,
        musical_style="POP",
        stem_processing=True,  # set True to request stems
        webhook_url=""  # optional, if you have a public endpoint
    )

    if not preview_task_id:
        print("Could not create a preview job. Exiting.")
        return

    print(f"Preview Task ID: {preview_task_id}")

    # 2) Poll for the preview result
    preview_results = poll_enhanced_track(preview_task_id, max_attempts=15, poll_interval=5)
    if not preview_results:
        print("Preview results were not returned. Check logs or try again.")
    else:
        print("Preview results:\n", preview_results)

        # Example keys: "preview_url", "enhanced_full_track_url", "stems"
        preview_url = preview_results.get("preview_url")
        if preview_url:
            download_file(preview_url, "enhanced_preview.mp3")

        # If stems are returned
        stems_dict = preview_results.get("stems", {})
        for stem_name, stem_link in stems_dict.items():
            local_stem = f"enhanced_preview_stem_{stem_name}.wav"
            download_file(stem_link, local_stem)

    # 3) Start a FULL Enhance Job
    full_task_id = start_mix_enhance(
        audio_url=demo_audio_url,
        musical_style="HIP_HOP_GRIME",
        stem_processing=True,
        webhook_url=""
    )

    if not full_task_id:
        print("Could not create a full enhance job. Exiting.")
        return

    print(f"Full Enhance Task ID: {full_task_id}")

    # 4) Poll for the final result
    full_results = poll_enhanced_track(full_task_id, max_attempts=15, poll_interval=5)
    if not full_results:
        print("Full results were not returned. Check logs or try again.")
    else:
        print("Full enhancement results:\n", full_results)

        # Example keys: "enhanced_full_track_url", "stems"
        full_track_url = full_results.get("enhanced_full_track_url")
        if full_track_url:
            download_file(full_track_url, "enhanced_full_track.wav")

        full_stems_dict = full_results.get("stems", {})
        for stem_name, stem_link in full_stems_dict.items():
            local_stem = f"enhanced_full_stem_{stem_name}.wav"
            download_file(stem_link, local_stem)

    print("All Done!")


# --------------------------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
