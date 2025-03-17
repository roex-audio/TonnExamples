import requests
import json
import time

# BASE_URL points to the API host. Replace it with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "GO TO https://tonn-portal.roexaudio.com get an API key"

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

    1. Builds a mixanalysis payload with the required fields.
    2. Sends it to the /mixanalysis endpoint.
    3. Prints results on success.
    """

    # Example mixanalysis payload. Adjust fields to match your audio file and style.
    mixanalysis_payload = {
        "mixDiagnosisData": {
            "audioFileLocation": "https://your-audio-file-location/audio.wav",
            "musicalStyle": "ROCK",
            "isMaster": True
        }
    }

    # Define HTTP headers with the API key.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Call the analyze_mix function to post our payload.
    response_data = analyze_mix(mixanalysis_payload, headers)
    if not response_data:
        print("No valid response from mix analysis.")
        return

    # Check if the API indicated any error or message directly in the top-level response.
    error_flag = response_data.get("error", False)
    message = response_data.get("message", "No message provided.")
    info = response_data.get("info", "No additional info provided.")
    print(f"\n=== Mix Analysis Top-Level Response ===")
    print(f"Error: {error_flag}")
    print(f"Message: {message}")
    print(f"Info: {info}")

    # Retrieve the mixDiagnosisResults if present.
    mix_diagnosis_results = response_data.get("mixDiagnosisResults")
    if mix_diagnosis_results:
        # Pretty-print the diagnosis details.
        print_mix_diagnosis_results(mix_diagnosis_results)
    else:
        print("No 'mixDiagnosisResults' found in the response.")

if __name__ == "__main__":
    main()
