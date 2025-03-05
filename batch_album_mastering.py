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

    Args:
        url (str): The direct URL to the file to be downloaded.
        local_filename (str): The file path where the downloaded file will be saved.
    """
    try:
        # We use a 'stream=True' request to handle large files in chunks.
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Raises an HTTPError if the response wasn't 2xx.
            with open(local_filename, 'wb') as f:
                # Write the response content in chunks of 8192 bytes to avoid memory overload.
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded file to {local_filename}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")


def poll_preview_master(task_id, headers, max_attempts=30, poll_interval=5):
    """
    Poll the /retrievepreviewmaster endpoint until the preview master is ready.

    This function sends a POST request with the mastering task ID to the /retrievepreviewmaster
    endpoint. It will repeatedly poll the endpoint until the preview master is ready (status 200)
    or until the maximum number of attempts is reached.

    NOTE: If you provided a webhookURL in the payload to /masteringpreview, you can rely on
    the webhook notification instead of polling.

    Args:
        task_id (str): The ID from /masteringpreview that identifies the preview mastering task.
        headers (dict): A dictionary of HTTP headers, including the API key.
        max_attempts (int): The maximum number of times we'll poll before giving up.
        poll_interval (int): Seconds to wait between each polling attempt.

    Returns:
        dict or None: Dictionary of preview master results if ready, otherwise None.
    """
    # Construct the endpoint and request payload.
    retrieve_url = f"{BASE_URL}/retrievepreviewmaster"
    retrieve_payload = {
        "masteringData": {
            "masteringTaskId": task_id
        }
    }

    print(f"Polling for preview master with task ID: {task_id}")
    for attempt in range(max_attempts):
        # Attempt to call the /retrievepreviewmaster endpoint.
        try:
            response = requests.post(retrieve_url, json=retrieve_payload, headers=headers)
        except Exception as e:
            print("Error during POST request to /retrievepreviewmaster:", e)
            return None

        # If the API responds with 202, the task is still processing.
        if response.status_code == 202:
            # We can parse the JSON to check the current status message (if provided).
            try:
                data = response.json()
                current_status = data.get("status", "Processing")
            except Exception:
                current_status = "Processing"
            print(f"Attempt {attempt + 1}/{max_attempts}: Task still processing (Status: {current_status}).")

        # If the API responds with 200, the preview master should be ready.
        elif response.status_code == 200:
            try:
                data = response.json()
                preview_results = data.get("previewMasterTaskResults")
                # Check if the relevant key is present.
                if preview_results:
                    print("Preview master is complete.")
                    return preview_results
                else:
                    print("Received 200 but missing 'previewMasterTaskResults' in the response.")
                    return None
            except Exception as e:
                print("Error parsing JSON response:", e)
                return None

        else:
            # Handle unexpected status codes.
            print("Unexpected response code:", response.status_code)
            print("Response:", response.text)
            return None

        # Wait before next attempt if not yet ready.
        time.sleep(poll_interval)

    # If we reach here, the preview master didn't become ready in time.
    print("Preview master was not available after polling. Please try again later.")
    return None


def retrieve_final_master(task_id, headers):
    """
    Calls the /retrievefinalmaster endpoint to retrieve the final master.

    This function sends a POST request to the /retrievefinalmaster endpoint with the given
    task_id. It should return the final mastered track’s URL if successful.

    Args:
        task_id (str): The mastering task ID returned from /masteringpreview.
        headers (dict): HTTP headers including Content-Type and API key.

    Returns:
        dict or None: The final master task results if ready, else None.
    """
    # Construct the request URL and payload.
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

    # Status code 200 means success in retrieving the final master.
    if response.status_code == 200:
        try:
            data = response.json()
            final_results = data.get("finalMasterTaskResults")
            return final_results
        except Exception as e:
            print("Error parsing final master JSON response:", e)
            return None
    else:
        # Any code other than 200 indicates some error or missing info.
        print("Failed to retrieve final master.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return None


def main():
    """
    Main function to batch-master an entire album and download each final master.

    This script expects a JSON file (e.g. 'album_mastering_payload.json') containing
    an array of track objects to master. For each track:
        1. POST to /masteringpreview to create a preview task.
        2. Poll /retrievepreviewmaster until the preview is ready (unless you have a webhook).
        3. Print the preview download URL.
        4. POST to /retrievefinalmaster to get the final full master URL.
        5. Download the final master to disk.

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

    # Attempt to load the album tracks data from a JSON file.
    try:
        with open(input_file, "r") as f:
            album_tracks = json.load(f)
    except Exception as e:
        print(f"Error reading {input_file}:", e)
        return

    # Define HTTP headers, including our API key.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Create an output directory to store final masters (optional).
    output_dir = "final_masters"
    os.makedirs(output_dir, exist_ok=True)

    # Loop through each track in the album data.
    for idx, track_data in enumerate(album_tracks, start=1):
        print("=" * 60)
        print(f"Starting mastering for Track #{idx}")

        # Build the payload that will be sent to /masteringpreview.
        # We gather the info from the track_data JSON object.
        mastering_payload = {
            "masteringData": {
                "trackData": [
                    {
                        "trackURL": track_data["trackURL"]
                    }
                ],
                "musicalStyle": track_data["musicalStyle"],
                "desiredLoudness": track_data["desiredLoudness"],
                # sampleRate is optional; if not provided, API defaults to 44100.
                "sampleRate": track_data.get("sampleRate", "44100"),
                "webhookURL": track_data["webhookURL"]
            }
        }

        # 1. Send a POST request to /masteringpreview to create a preview task.
        preview_url = f"{BASE_URL}/masteringpreview"
        print("Creating preview mastering task...")
        try:
            response = requests.post(preview_url, json=mastering_payload, headers=headers)
        except Exception as e:
            print("Error during POST request to /masteringpreview:", e)
            continue

        # If successful, we should get 200 + a JSON response containing 'mastering_task_id'.
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
            # If we didn’t get a 200, something went wrong (e.g., invalid data or missing fields).
            print("Failed to create preview mastering task.")
            print("Status code:", response.status_code)
            print("Response:", response.text)
            continue

        # 2. Poll the /retrievepreviewmaster endpoint until the preview is ready (or times out).
        preview_results = poll_preview_master(mastering_task_id, headers)
        if not preview_results:
            # If preview never became ready, we skip trying to finalize this track.
            print("Preview not ready. Skipping final mastering for this track.")
            continue

        # 3. Print the preview master's URL if available.
        preview_download_url = preview_results.get("download_url_mastered_preview")
        if preview_download_url:
            print("Preview mastered track URL:", preview_download_url)
        else:
            print("Missing 'download_url_mastered_preview' in preview results.")

        # Show the preview start time if provided (some APIs might return a different number or -1).
        preview_start_time = preview_results.get("preview_start_time", -1)
        print("Preview start time:", preview_start_time)

        # 4. Retrieve the final mastered track by calling /retrievefinalmaster.
        final_results = retrieve_final_master(mastering_task_id, headers)
        if not final_results:
            print("Failed to retrieve final master for this track.")
            continue

        # final_results should contain the final mastering download URL under "download_url_mastered".
        final_download_url = final_results.get("download_url_mastered")
        if not final_download_url:
            print("Error: final download URL not found in final_results!")
        else:
            print("Final Mastered Track URL:", final_download_url)

            # 5. Download the final master locally to "final_masters/final_master_track_{idx}.wav"
            local_filename = os.path.join(output_dir, f"final_master_track_{idx}.wav")
            download_file(final_download_url, local_filename)

        print(f"Finished mastering for Track #{idx}.\n")

    print("All done!")


# Standard Python entry point for script execution.
if __name__ == "__main__":
    main()
