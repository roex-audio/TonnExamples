import os
import requests
import json
import time
import argparse
import mimetypes

# BASE_URL points to the API host. Replace it with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
# Read API Key from environment variable for better security
API_KEY = os.environ.get("TONN_API_KEY")

if not API_KEY:
    print("Error: TONN_API_KEY environment variable not set.")
    print("GO TO https://tonn-portal.roexaudio.com to get an API key")
    exit(1)

SUPPORTED_EXTENSIONS = ['.mp3', '.wav', '.flac']

def get_content_type(filename):
    """
    Determine the appropriate content type based on the file extension.
    Args: filename (str)
    Returns: str or None
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.mp3':
        return 'audio/mpeg'
    elif ext == '.wav':
        return 'audio/wav'
    elif ext == '.flac':
        return 'audio/flac'
    else:
        return None # Only return explicitly supported types

def get_upload_urls(filename, content_type, api_key):
    """
    Calls the /upload endpoint to get signed and readable URLs.
    Args: filename (str), content_type (str), api_key (str)
    Returns: tuple (signed_url, readable_url) or (None, None)
    """
    upload_url = f"{BASE_URL}/upload"
    params = {"key": api_key}
    payload = {"filename": filename, "contentType": content_type}
    headers = {"Content-Type": "application/json"}

    print(f"Requesting upload URLs for {filename} ({content_type})...")
    try:
        response = requests.post(upload_url, params=params, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("error"):
            print(f"API Error getting upload URL: {data.get('message', 'Unknown error')}")
            return None, None
        signed_url = data.get("signed_url")
        readable_url = data.get("readable_url")
        if not signed_url or not readable_url:
            print(f"Error: Missing signed_url or readable_url in response: {data}")
            return None, None
        print("Successfully obtained upload URLs.")
        return signed_url, readable_url
    except requests.exceptions.RequestException as e:
        print(f"Error requesting upload URLs: {e}")
        if response is not None: print(f"Response: {response.status_code} {response.text}")
        return None, None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from /upload: {response.text}")
        return None, None

def upload_file_to_signed_url(signed_url, local_filepath, content_type):
    """
    Uploads the local file to the provided signed URL using PUT.
    Args: signed_url (str), local_filepath (str), content_type (str)
    Returns: bool
    """
    print(f"Uploading {local_filepath} to signed URL...")
    headers = {'Content-Type': content_type}
    try:
        with open(local_filepath, 'rb') as f:
            response = requests.put(signed_url, data=f, headers=headers)
            response.raise_for_status()
        print("File uploaded successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: Local file not found at {local_filepath}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        if response is not None: print(f"Response: {response.status_code} {response.text}")
        return False

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
    except requests.exceptions.RequestException as e: # Catch specific request errors
        print(f"Error downloading file from {url}: {e}")
    except IOError as e: # Catch file writing errors
        print(f"Error writing file {local_filename}: {e}")
    except Exception as e: # Generic catch-all
        print(f"An unexpected error occurred during download: {e}")

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
    Main function to batch-master audio files from an input directory.

    For each supported audio file in the directory:
        1. Get upload URLs using the /upload endpoint.
        2. Upload the file via the signed URL.
        3. POST to /masteringpreview using the readable URL and global settings.
        4. Poll /retrievepreviewmaster until the preview is ready.
        5. POST to /retrievefinalmaster to get the final master URL.
        6. Download the final master to the output directory.
    """
    parser = argparse.ArgumentParser(description="Batch master audio files in a directory using Tonn Roex API.")
    parser.add_argument("input_dir", help="Path to the directory containing input audio files (.mp3, .wav, .flac)")
    parser.add_argument("-o", "--output-dir", default="./output_masters", help="Directory to save final masters (default: ./output_masters)")
    parser.add_argument("--style", default="ROCK_INDIE", help="Musical style for mastering (default: ROCK_INDIE)")
    parser.add_argument("--loudness", default="MEDIUM", help="Desired loudness (default: MEDIUM)")
    parser.add_argument("--sample-rate", default="44100", help="Sample rate (default: 44100)")
    # parser.add_argument("--webhook", help="Optional webhook URL for notifications") # Example if needed

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found: {input_dir}")
        return

    # Create the output directory if it doesn't exist.
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output masters will be saved to: {output_dir}")

    # Define common HTTP headers.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Iterate over files in the input directory
    for filename in os.listdir(input_dir):
        local_filepath = os.path.join(input_dir, filename)
        _, ext = os.path.splitext(filename)

        # Skip non-files and unsupported file types
        if not os.path.isfile(local_filepath) or ext.lower() not in SUPPORTED_EXTENSIONS:
            if os.path.isfile(local_filepath):
                 print(f"Skipping unsupported file: {filename}")
            continue

        print(f"\n--- Processing: {filename} ---")

        # 1. Determine content type
        content_type = get_content_type(filename)
        if not content_type:
            print(f"Error: Could not determine supported content type for {filename}. Skipping.")
            continue

        # 2. Get Upload URLs
        signed_url, readable_url = get_upload_urls(filename, content_type, API_KEY)
        if not signed_url or not readable_url:
            print(f"Failed to get upload URLs for {filename}. Skipping.")
            continue

        # 3. Upload the file
        upload_success = upload_file_to_signed_url(signed_url, local_filepath, content_type)
        if not upload_success:
            print(f"File upload failed for {filename}. Skipping.")
            continue

        print(f"Using readable URL: {readable_url}")

        # 4. Prepare and send payload to /masteringpreview
        preview_payload = {
            "masteringData": {
                "trackData": [
                    {
                        "trackURL": readable_url
                    }
                ],
                "musicalStyle": args.style,
                "desiredLoudness": args.loudness,
                "sampleRate": args.sample_rate
                # "webhookURL": args.webhook # Add if using webhook
            }
        }
        preview_url = f"{BASE_URL}/masteringpreview"
        task_id = None

        print(f"Requesting mastering preview for {filename}...")
        try:
            response = requests.post(preview_url, json=preview_payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            task_id = data.get("mastering_task_id")
            if not task_id:
                print(f"Error: Missing mastering_task_id in response for {filename}: {data}")
                continue # Skip to next file
            print(f"Mastering preview task created with ID: {task_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error requesting mastering preview for {filename}: {e}")
            if response is not None: print(f"Response: {response.status_code} {response.text}")
            continue # Skip to next file
        except json.JSONDecodeError:
             print(f"Error decoding JSON response from /masteringpreview: {response.text}")
             continue # Skip to next file

        # 5. Poll for Preview Master Ready (unless webhook is used)
        # Note: If using webhooks, you'd skip this polling step.
        preview_results = poll_preview_master(task_id, headers)
        if not preview_results:
            print(f"Could not retrieve preview master for {filename} (Task ID: {task_id}). Skipping final master retrieval.")
            continue

        # Print preview result details (optional)
        preview_url = preview_results.get('previewMasterTrackURL')
        print(f"Preview master ready for {filename}. URL: {preview_url if preview_url else 'Not available'}")
        # You could download the preview here if needed using download_file()

        # 6. Retrieve Final Master
        final_results = retrieve_final_master(task_id, headers)
        if final_results:
            final_url = final_results.get('download_url_mastered')
            if final_url:
                print(f"Final master ready for {filename}. URL: {final_url}")
                # Construct a local filename based on the original
                base, _ = os.path.splitext(filename)
                output_filename = os.path.join(output_dir, f"{base}_mastered{ext}")
                print(f"Downloading final master to: {output_filename}")
                download_file(final_url, output_filename)
            else:
                print(f"Final master result received for {filename}, but URL is missing.")
        else:
            print(f"Failed to retrieve final master for {filename} (Task ID: {task_id}).")

    print("\nBatch mastering process finished.")

# Standard Python entry point for script execution.
if __name__ == "__main__":
    main()
