import requests
import json
import os
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


def get_content_type(filename):
    """
    Determine the appropriate content type based on the file extension.

    Args:
        filename (str): The name of the file.

    Returns:
        str or None: The determined content type or None if unsupported.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.mp3':
        return 'audio/mpeg'
    elif ext == '.wav':
        return 'audio/wav'
    elif ext == '.flac':
        return 'audio/flac'
    else:
        # Fallback using mimetypes, though the API might reject it
        content_type, _ = mimetypes.guess_type(filename)
        # Explicitly return None if it's not one of the supported types
        if content_type not in ['audio/mpeg', 'audio/wav', 'audio/flac']:
            print(f"Warning: Guessed content type '{content_type}' for {filename} might not be supported by the API.")
            return None # Or maybe return the guessed type and let the API decide?
        return content_type

def get_upload_urls(filename, content_type, api_key):
    """
    Calls the /upload endpoint to get signed and readable URLs.

    Args:
        filename (str): The name of the file to be uploaded.
        content_type (str): The MIME type of the file.
        api_key (str): The API key.

    Returns:
        tuple: (signed_url, readable_url) or (None, None) on failure.
    """
    upload_url = f"{BASE_URL}/upload"
    params = {"key": api_key}
    payload = {
        "filename": filename,
        "contentType": content_type
    }
    headers = {"Content-Type": "application/json"}

    print(f"Requesting upload URLs for {filename} ({content_type})...")
    try:
        response = requests.post(upload_url, params=params, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
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
        if response is not None:
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
        return None, None
    except json.JSONDecodeError:
        print("Error decoding JSON response from /upload endpoint.")
        print(f"Response text: {response.text}")
        return None, None

def upload_file_to_signed_url(signed_url, local_filepath, content_type):
    """
    Uploads the local file to the provided signed URL using PUT.

    Args:
        signed_url (str): The pre-signed URL for uploading.
        local_filepath (str): The path to the local file to upload.
        content_type (str): The MIME type of the file.

    Returns:
        bool: True if upload was successful, False otherwise.
    """
    print(f"Uploading {local_filepath} to signed URL...")
    headers = {'Content-Type': content_type}
    try:
        with open(local_filepath, 'rb') as f:
            response = requests.put(signed_url, data=f, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        print("File uploaded successfully.")
        return True
    except FileNotFoundError:
        print(f"Error: Local file not found at {local_filepath}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        if response is not None:
             print(f"Response status: {response.status_code}")
             print(f"Response text: {response.text}")
        return False

def print_audio_cleanup_results(cleanup_results):
    """
    Pretty-print audio cleanup results.

    Args:
        cleanup_results (dict): The 'audioCleanupResults' portion of the JSON response from /audio-cleanup.
    """
    # Basic sanity check: ensure we have something to work with.
    if not isinstance(cleanup_results, dict):
        print("No valid cleanup results found.")
        return

    print("\n=== Audio Cleanup Results ===")
    # For example, print out top-level info and payload if it exists.
    completion_time = cleanup_results.get("completion_time", "N/A")
    print(f"Completion Time: {completion_time}")
    error = cleanup_results.get("error", False)
    print(f"Error Flag: {error}")
    info = cleanup_results.get("info", "None")
    print(f"Info: {info}")

    # If a download URL is available, download the result file
    download_url = cleanup_results.get("cleaned_audio_file_location")
    output_filename = "cleaned_" + os.path.basename(cleanup_results.get("input_filename", "audio.wav")) # Try to base output name on input
    if download_url:
        print(f"Download URL: {download_url}")
        download_file(download_url, output_filename)
    else:
        print("No download URL found for the cleaned audio.")

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

def clean_up_audio(cleanup_payload, headers):
    """
    Send a POST request to the /audio-cleanup endpoint with the provided payload.

    Args:
        cleanup_payload (dict): Payload containing the audio cleanup data.
        headers (dict): HTTP headers including Content-Type and API key.

    Returns:
        dict or None: JSON response if request is successful; otherwise None.
    """
    # Construct the full URL for the /audio-cleanup endpoint.
    cleanup_url = f"{BASE_URL}/audio-cleanup"
    print(f"Sending POST request to {cleanup_url} for audio cleanup...")

    try:
        response = requests.post(cleanup_url, json=cleanup_payload, headers=headers)
    except Exception as e:
        print("Error during POST request to /audio-cleanup:", e)
        return None

    # Check if the response indicates a successful request.
    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            print("Error parsing JSON response:", e)
            return None
        return data
    else:
        print("Failed to initiate audio cleanup.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return None

def main():
    """
    Main function to demonstrate how to call the /audio-cleanup endpoint.

    1. Parses command-line argument for the input audio file.
    2. Gets upload URLs from the /upload endpoint.
    3. Uploads the file using the signed URL.
    4. Builds a cleanup payload using the readable URL.
    5. Sends it to the /audio-cleanup endpoint.
    6. Prints results on success.
    """
    parser = argparse.ArgumentParser(description="Clean up an audio file using the Tonn Roex API.")
    parser.add_argument("input_file", help="Path to the input audio file (.mp3, .wav, .flac)")
    parser.add_argument("-s", "--source", default="VOCAL_GROUP",
                        help="Sound source type (e.g., VOCAL_GROUP, SNARE_GROUP). Default: VOCAL_GROUP")
    args = parser.parse_args()

    local_filepath = args.input_file
    filename = os.path.basename(local_filepath)
    sound_source = args.source

    # Check if file exists locally before proceeding
    if not os.path.isfile(local_filepath):
        print(f"Error: Input file not found: {local_filepath}")
        return

    # Determine content type
    content_type = get_content_type(filename)
    if not content_type:
        print(f"Error: Unsupported file type or could not determine content type for {filename}.")
        print("Supported types: .mp3 (audio/mpeg), .wav (audio/wav), .flac (audio/flac)")
        return

    # 1. Get Upload URLs
    signed_url, readable_url = get_upload_urls(filename, content_type, API_KEY)
    if not signed_url or not readable_url:
        print("Failed to get upload URLs. Exiting.")
        return

    # 2. Upload the file
    upload_success = upload_file_to_signed_url(signed_url, local_filepath, content_type)
    if not upload_success:
        print("File upload failed. Exiting.")
        return

    print(f"Using readable URL: {readable_url}")

    # 3. Build the cleanup payload using the readable URL
    cleanup_payload = {
        "audioCleanupData": {
            "audioFileLocation": readable_url,
            "soundSource": sound_source
        }
    }

    # Define HTTP headers with the API key for the cleanup endpoint
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # 4. Call the clean_up_audio function
    response_data = clean_up_audio(cleanup_payload, headers)
    if not response_data:
        print("No valid response from audio cleanup.")
        return

    # --- Process Response (remains largely the same) ---
    # Check if the API indicated any error or message directly in the top-level response.
    error_flag = response_data.get("error", False)
    message = response_data.get("message", "No message provided.")
    info = response_data.get("info", "No additional info provided.")
    print(f"\n=== Audio Cleanup Top-Level Response ===")
    print(f"Error: {error_flag}")
    print(f"Message: {message}")
    print(f"Info: {info}")

    # Retrieve the audio cleanup results if present.
    audio_cleanup_results = response_data.get("audioCleanupResults")
    if audio_cleanup_results:
        # Add input filename to results for context if possible
        audio_cleanup_results['input_filename'] = filename
        # Pretty-print the cleanup results.
        print_audio_cleanup_results(audio_cleanup_results)
    else:
        print("No 'audioCleanupResults' found in the response.")

if __name__ == "__main__":
    main()
