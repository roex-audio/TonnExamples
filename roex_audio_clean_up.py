import requests
import json

# BASE_URL points to the API host. Replace it with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "GO TO https://tonn-portal.roexaudio.com to get an API key"

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
    if download_url:
        print(f"Download URL: {download_url}")
        download_file(download_url, "cleaned_audio.wav")
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
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")
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

    1. Builds a cleanup payload with the required fields.
    2. Sends it to the /audio-cleanup endpoint.
    3. Prints results on success.
    """

    # Example cleanup payload. Adjust fields to match your audio file and sound source.
    cleanup_payload = {
        "audioCleanupData": {
            "audioFileLocation": "https://your-audio-file-location/vocal_track.wav",  # Replace with your file URL
            "soundSource": "VOCAL_GROUP"  # Or choose from other groups like SNARE_GROUP, E_GUITAR_GROUP, etc.
        }
    }

    # Define HTTP headers with the API key.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Call the clean_up_audio function to post our payload.
    response_data = clean_up_audio(cleanup_payload, headers)
    if not response_data:
        print("No valid response from audio cleanup.")
        return

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
        # Pretty-print the cleanup results.
        print_audio_cleanup_results(audio_cleanup_results)
    else:
        print("No 'audioCleanupResults' found in the response.")

if __name__ == "__main__":
    main()
