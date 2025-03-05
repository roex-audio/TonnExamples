import os
import requests
import json
import time

# BASE_URL points to the API host. Replace it with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "GO TO https://tonn-portal.roexaudio.com get an API key"


def download_file(url, local_filename):
    """
    Downloads a file from the provided URL and saves it locally.
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


def poll_preview_master(task_id, headers, max_attempts=30, poll_interval=5):
    """
    Poll the /retrievepreviewmaster endpoint until the preview master is ready.

    This function sends a POST request with the mastering task ID to the /retrievepreviewmaster
    endpoint. It will repeatedly poll the endpoint until either the preview master is ready
    (status code 200) or the maximum number of attempts is reached.

    NOTE: If you provide a webhookURL in the payload when creating the mastering preview,
    the API will send a callback to that URL once the preview is ready. In that case, you wouldn't
    need to poll this endpoint manually. Polling is used here for demonstration purposes.

    Args:
        task_id (str): The mastering task ID returned from the /masteringpreview endpoint.
        headers (dict): HTTP headers including Content-Type and API key.
        max_attempts (int): Maximum number of polling attempts.
        poll_interval (int): Seconds to wait between attempts.

    Returns:
        dict or None: The preview master task results if ready, else None.
    """
    retrieve_url = f"{BASE_URL}/retrievepreviewmaster"
    retrieve_payload = {
        "masteringData": {
            "masteringTaskId": task_id
        }
    }

    print(f"Polling for preview master with task ID: {task_id}")
    for attempt in range(max_attempts):
        try:
            response = requests.post(retrieve_url, json=retrieve_payload, headers=headers)
        except Exception as e:
            print("Error during POST request to /retrievepreviewmaster:", e)
            return None

        if response.status_code == 202:
            # Still processing, parse the status if provided
            try:
                data = response.json()
                current_status = data.get("status", "Processing")
            except Exception:
                current_status = "Processing"
            print(f"Attempt {attempt + 1}/{max_attempts}: Task still processing (Status: {current_status}).")
        elif response.status_code == 200:
            try:
                data = response.json()
                preview_results = data.get("previewMasterTaskResults")
                # If the preview master is ready, we assume the necessary keys exist
                if preview_results:
                    print("Preview master is complete.")
                    return preview_results
                else:
                    print("Received 200 but missing 'previewMasterTaskResults' in response.")
                    return None
            except Exception as e:
                print("Error parsing JSON response:", e)
                return None
        else:
            print("Unexpected response code:", response.status_code)
            print("Response:", response.text)
            return None

        time.sleep(poll_interval)

    print("Preview master was not available after polling. Please try again later.")
    return None


def retrieve_final_master(task_id, headers):
    """
    Call the /retrievefinalmaster endpoint to retrieve the final master.

    This function sends a POST request to the /retrievefinalmaster endpoint
    with the provided task ID. It expects a 200 status code and returns the
    final master task results if successful.

    Args:
        task_id (str): The mastering task ID returned from the /masteringpreview endpoint.
        headers (dict): HTTP headers including Content-Type and API key.

    Returns:
        dict or None: The final master task results if ready, else None.
    """
    retrieve_url = f"{BASE_URL}/retrievefinalmaster"
    final_payload = {
        "masteringData": {
            "masteringTaskId": task_id
        }
    }

    print(f"Requesting final master for task ID: {task_id}")
    try:
        response = requests.post(retrieve_url, json=final_payload, headers=headers)
    except Exception as e:
        print("Error during POST request to /retrievefinalmaster:", e)
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            final_results = data.get("finalMasterTaskResults")
            return final_results
        except Exception as e:
            print("Error parsing final master JSON response:", e)
            return None
    else:
        print("Failed to retrieve final master.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return None


def main():
    """
    Main function to batch-master an entire album and download each final master.

    This script expects a JSON file (e.g. 'album_mastering_payload.json') containing
    an array of tracks to master. For each track, it:
        1. POSTs to /masteringpreview to create a preview task.
        2. Polls /retrievepreviewmaster until the preview is ready (unless you use webhooks).
        3. Prints the preview download URL.
        4. POSTs to /retrievefinalmaster to get the final full master URL.
        5. Downloads the final master to disk.

    Example of album_mastering_payload.json:
    [
      {
        "trackURL": "https://example.com/path/to/track1.wav",
        "musicalStyle": "ROCK_INDIE",
        "desiredLoudness": "MEDIUM",
        "sampleRate": "44100",
        "webhookURL": "https://yourwebhook.example.com/track1"
      },
      {
        "trackURL": "https://example.com/path/to/track2.flac",
        "musicalStyle": "POP",
        "desiredLoudness": "HIGH",
        "sampleRate": "48000",
        "webhookURL": "https://yourwebhook.example.com/track2"
      }
    ]
    """
    input_file = "./album_mastering_payload.json"
    # Load the album tracks from JSON
    try:
        with open(input_file, "r") as f:
            album_tracks = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}:", e)
        return

    # Define HTTP headers with the API key.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Create an output directory for final masters (optional).
    output_dir = "final_masters"
    os.makedirs(output_dir, exist_ok=True)

    for idx, track_data in enumerate(album_tracks, start=1):
        print("=" * 60)
        print(f"Starting mastering for Track #{idx}")

        # Construct the payload for /masteringpreview
        mastering_payload = {
            "masteringData": {
                "trackData": [
                    {
                        "trackURL": track_data["trackURL"]
                    }
                ],
                "musicalStyle": track_data["musicalStyle"],
                "desiredLoudness": track_data["desiredLoudness"],
                # sampleRate is optional; default is 44100 if not provided.
                "sampleRate": track_data.get("sampleRate", "44100"),
                "webhookURL": track_data["webhookURL"]
            }
        }

        # 1. Create the preview mastering task
        preview_url = f"{BASE_URL}/masteringpreview"
        print("Creating preview mastering task...")
        try:
            response = requests.post(preview_url, json=mastering_payload, headers=headers)
        except Exception as e:
            print("Error during POST request to /masteringpreview:", e)
            continue

        if response.status_code == 200:
            try:
                data = response.json()
                mastering_task_id = data.get("mastering_task_id")
                if not mastering_task_id:
                    print("Error: mastering_task_id not found in response:", data)
                    continue
                print(f"Preview mastering task created successfully. Task ID: {mastering_task_id}")
            except Exception as e:
                print("Error parsing preview mastering JSON response:", e)
                continue
        else:
            print("Failed to create preview mastering task.")
            print("Status code:", response.status_code)
            print("Response:", response.text)
            continue

        # 2. Poll /retrievepreviewmaster for the preview to be ready
        preview_results = poll_preview_master(mastering_task_id, headers)
        if not preview_results:
            print("Preview not ready. Skipping final mastering for this track.")
            continue

        # 3. Print the preview mastered track URL
        preview_download_url = preview_results.get("download_url_mastered_preview")
        if preview_download_url:
            print("Preview mastered track URL:", preview_download_url)
        else:
            print("Missing 'download_url_mastered_preview' in preview results.")

        # Some APIs also provide additional metadata like 'preview_start_time'.
        preview_start_time = preview_results.get("preview_start_time", -1)
        print("Preview start time:", preview_start_time)

        # 4. Retrieve the final mastered track
        final_results = retrieve_final_master(mastering_task_id, headers)
        if not final_results:
            print("Failed to retrieve final master for this track.")
            continue

        # final_results should be the download URL for the final master
        final_download_url = final_results
        if not final_download_url:
            print("No final download URL returned.")
            continue

        # Extract the URL string:
        final_download_url = final_results.get("download_url_mastered")

        # 5. Download the final master locally.
        # We name the file "final_master_track_{idx}.wav" (or .mp3, etc.):
        if not final_download_url:
            print("Error: final download URL not found in final_results!")
        else:
            print("Final Mastered Track URL:", final_download_url)
            # Pass the URL (string) to your download method:
            local_filename = os.path.join(output_dir, f"final_master_track_{idx}.wav")
            download_file(final_download_url, local_filename)

        print(f"Finished mastering for Track #{idx}.\n")

    print("All done!")


if __name__ == "__main__":
    main()
