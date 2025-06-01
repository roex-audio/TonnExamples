import requests
import json
import time
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

# === Helper Functions (Copied/Adapted from other scripts) ===

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
        return None

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

# === End Helper Functions ===


# === Existing Functions (print_mix_diagnosis_results, analyze_mix) ===

def print_mix_diagnosis_results(diagnosis):
    """
    Pretty-print mix diagnosis results.

    Args:
        diagnosis (dict): The 'mixDiagnosisResults' portion of the JSON response from /mixanalysis.
    """
    # Basic sanity check: ensure we have something to work with.
    if not isinstance(diagnosis, dict):
        print("No valid mix diagnosis results found.")
        return

    print("\n=== Mix Diagnosis Results ===")
    # For example, print out top-level info and payload if it exists.
    completion_time = diagnosis.get("completion_time", "N/A")
    print(f"Completion Time: {completion_time}")
    error = diagnosis.get("error", False)
    print(f"Error Flag: {error}")
    info = diagnosis.get("info", "None")
    print(f"Info: {info}")

    payload = diagnosis.get("payload", {})
    if payload:
        print("\n--- Payload Details ---")
        for key, value in payload.items():
            print(f"{key}: {value}")
    else:
        print("No payload data available.")

    summary = payload.get("summary", {})
    if summary:
        print("\n--- Summary ---")
        for s_key, s_value in summary.items():
            print(f"{s_key}: {s_value}")
    else:
        print("\nNo summary data available.")

def analyze_mix(mixanalysis_payload, headers):
    """
    Send a POST request to the /mixanalysis endpoint with the provided payload.

    Args:
        mixanalysis_payload (dict): Payload containing the mixDiagnosisData.
        headers (dict): HTTP headers including Content-Type and API key.

    Returns:
        dict or None: JSON response if request is successful; otherwise None.
    """
    # Construct the full URL for the /mixanalysis endpoint.
    mixanalysis_url = f"{BASE_URL}/mixanalysis"
    print(f"Sending POST request to {mixanalysis_url} for mix analysis...")

    try:
        response = requests.post(mixanalysis_url, json=mixanalysis_payload, headers=headers)
    except Exception as e:
        print("Error during POST request to /mixanalysis:", e)
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
        print("Failed to initiate mix analysis.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return None

def main():
    """
    Main function to demonstrate how to call the /mixanalysis endpoint.

    1. Parses arguments for input file path and musical style.
    2. Gets upload URLs and uploads the file.
    3. Builds a mixanalysis payload using the readable URL and style.
    4. Sends it to the /mixanalysis endpoint.
    5. Prints results on success.
    """
    parser = argparse.ArgumentParser(description="Analyze a mix file using the Tonn Roex API.")
    parser.add_argument("input_file", help="Path to the input audio file (.mp3, .wav, .flac)")
    parser.add_argument("musical_style", help="Musical style (e.g., ROCK, POP, ELECTRONIC)")
    parser.add_argument("--is-master", action='store_true', help="Flag if the input file is a master (default: False)")

    args = parser.parse_args()

    local_filepath = args.input_file
    filename = os.path.basename(local_filepath)

    # Check if file exists locally
    if not os.path.isfile(local_filepath):
        print(f"Error: Input file not found: {local_filepath}")
        return

    # Determine content type
    content_type = get_content_type(filename)
    if not content_type:
        print(f"Error: Unsupported file type or could not determine content type for {filename}.")
        print("Supported types: .mp3, .wav, .flac")
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

    # 3. Build the mix analysis payload
    mixanalysis_payload = {
        "mixDiagnosisData": {
            "audioFileLocation": readable_url,
            "musicalStyle": args.musical_style,
            "isMaster": args.is_master
        }
    }

    # Define HTTP headers with the API key
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # 4. Call the analyze_mix function
    response_data = analyze_mix(mixanalysis_payload, headers)
    if not response_data:
        print("No valid response from mix analysis.")
        return

    # 5. Process Response
    error_flag = response_data.get("error", False)
    message = response_data.get("message", "No message provided.")
    info = response_data.get("info", "No additional info provided.")
    print(f"\n=== Mix Analysis Top-Level Response ===")
    print(f"Error: {error_flag}")
    print(f"Message: {message}")
    print(f"Info: {info}")

    mix_diagnosis_results = response_data.get("mixDiagnosisResults")
    if mix_diagnosis_results:
        print_mix_diagnosis_results(mix_diagnosis_results)
    else:
        print("No 'mixDiagnosisResults' found in the response.")

if __name__ == "__main__":
    main()
