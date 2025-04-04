import requests
import time
import os

# ---------------------------------------------
# Configuration & Constants
# ---------------------------------------------
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
BASE_URL = "https://YOUR_BASE_URL"  # e.g. https://api.roexaudio.com

# Headers for authentication
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"  # or "x-api-key": API_KEY, if that's your required header
}


# ---------------------------------------------
# Helper Function: Start a Preview Task
# ---------------------------------------------
def start_mix_enhance_preview(audio_url, musical_style="POP", stem_processing=False, webhook_url=""):
    """
    Calls /mixenhancepreview to create a Cloud Task that processes a PREVIEW of the enhanced track.
    Returns the 'mixrevive_task_id' from the API response.
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

    print(f"Posting preview request to {endpoint} ...")
    response = requests.post(endpoint, json=payload, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data.get("error") is False:
            task_id = data.get("mixrevive_task_id", None)
            print(f"✓ Preview task created. Task ID: {task_id}")
            return task_id
        else:
            raise Exception(f"API returned error: {data.get('message')}")
    else:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")


# ---------------------------------------------
# Helper Function: Start a Full Enhance Task
# ---------------------------------------------
def start_full_mix_enhance(audio_url, musical_style="POP", stem_processing=False, webhook_url=""):
    """
    Calls /mixenhance to create a Cloud Task that processes the FULL enhanced track.
    Returns the 'mixrevive_task_id' from the API response.
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

    print(f"Posting full enhance request to {endpoint} ...")
    response = requests.post(endpoint, json=payload, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data.get("error") is False:
            task_id = data.get("mixrevive_task_id", None)
            print(f"✓ Full enhance task created. Task ID: {task_id}")
            return task_id
        else:
            raise Exception(f"API returned error: {data.get('message')}")
    else:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")


# ---------------------------------------------
# Helper Function: Retrieve the Enhanced Track
# ---------------------------------------------
def retrieve_enhanced_track(task_id):
    """
    Calls /retrieveenhancedtrack to fetch the final or preview-processed track URLs.
    Returns a dict with URLs to the enhanced track and optionally stems.
    """
    endpoint = f"{BASE_URL}/retrieveenhancedtrack"

    payload = {
        "mixReviveData": {
            "mixReviveTaskId": task_id
        }
    }

    print(f"Retrieving final track info for task ID: {task_id} ...")
    response = requests.post(endpoint, json=payload, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        if data.get("error") is False:
            return data.get("revived_track_tasks_results", {})
        else:
            raise Exception(f"API returned error while retrieving track: {data.get('message')}")
    else:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")


# ---------------------------------------------
# Helper Function: Download Files
# ---------------------------------------------
def download_file(url, local_filename):
    """
    Downloads the file from the given URL and saves it locally.
    """
    print(f"Downloading file from {url} to {local_filename} ...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"✓ Download complete: {local_filename}")


# ---------------------------------------------
# Main Demo Flow
# ---------------------------------------------
if __name__ == "__main__":
    # 1) Start a preview task
    preview_audio_url = "https://example.com/path/to/your-audio-file.mp3"  # Replace with a real file
    preview_style = "POP"
    preview_task_id = start_mix_enhance_preview(
        audio_url=preview_audio_url,
        musical_style=preview_style,
        stem_processing=True,  # set to False if you don't want stems
        webhook_url=""  # optional: e.g., "https://yourapp.com/webhook"
    )

    # 2) Wait or poll before retrieving.
    #    If your system is truly async, you might need to wait longer or rely on the webhook.
    print("Waiting a few seconds for the preview task to finish processing...")
    time.sleep(5)  # In real usage, you might wait longer or listen for a webhook.

    # 3) Retrieve the preview track
    preview_results = retrieve_enhanced_track(preview_task_id)
    print(f"Preview retrieval results:\n{preview_results}")

    # 4) Download the preview track (and stems if present)
    #    The dict might look like:
    #    {
    #      "preview_url": "https://example.com/path.mp3",
    #      "enhanced_full_track_url": "https://example.com/full.wav",
    #      "stems": {"vocals": "...", "drums": "...", etc.}
    #    }
    preview_url = preview_results.get("preview_url")
    if preview_url:
        download_file(preview_url, "enhanced_preview.mp3")

    # Optional: If stems were requested
    stems = preview_results.get("stems", {})
    if stems:
        for stem_name, stem_url in stems.items():
            local_stem_filename = f"enhanced_preview_stem_{stem_name}.wav"
            download_file(stem_url, local_stem_filename)

    # -------------------------------------------
    # 5) Start a FULL enhance task (not just preview)
    #    Possibly using the same audio file or a different one
    # -------------------------------------------
    full_task_id = start_full_mix_enhance(
        audio_url=preview_audio_url,  # reusing the same for demonstration
        musical_style="HIP_HOP_GRIME",
        stem_processing=True,
        webhook_url=""  # optional
    )

    # 6) Wait or poll again
    print("Waiting for the full enhance task to finish processing...")
    time.sleep(5)  # Adjust as needed

    # 7) Retrieve final track info
    full_results = retrieve_enhanced_track(full_task_id)
    print(f"Full enhance retrieval results:\n{full_results}")

    # 8) Download the final track
    full_track_url = full_results.get("enhanced_full_track_url")
    if full_track_url:
        download_file(full_track_url, "enhanced_full_track.wav")

    # Optional: Download full stems
    full_stems = full_results.get("stems", {})
    if full_stems:
        for stem_name, stem_url in full_stems.items():
            local_stem_filename = f"enhanced_full_stem_{stem_name}.wav"
            download_file(stem_url, local_stem_filename)

    print("Demo flow complete!")
