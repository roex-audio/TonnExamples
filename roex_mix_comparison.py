import requests
import json

# BASE_URL points to the API host. Replace with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key from https://tonn-portal.roexaudio.com


def analyze_mix(audio_url, musical_style="ROCK", is_master=True):
    """
    Sends a POST request to the /mixanalysis endpoint for the given audio file.

    Args:
        audio_url (str): URL of the audio file to analyze.
        musical_style (str): Musical style (e.g., "ROCK", "TECHNO").
        is_master (bool): Flag indicating if the track is mastered.

    Returns:
        dict: The 'mixDiagnosisResults' portion of the API response if successful; otherwise, an empty dict.
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    payload = {
        "mixDiagnosisData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": is_master
        }
    }

    mixanalysis_url = f"{BASE_URL}/mixanalysis"
    print(f"Sending POST request to {mixanalysis_url} for audio file: {audio_url}")

    try:
        response = requests.post(mixanalysis_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
    except Exception as e:
        print(f"Error analyzing {audio_url}: {e}")
        return {}

    if "mixDiagnosisResults" in data:
        return data["mixDiagnosisResults"]
    else:
        print(f"No 'mixDiagnosisResults' found in the response for {audio_url}.")
        return {}


def print_mix_diagnosis_results(diagnosis):
    """
    Pretty-prints the mix diagnosis results.

    Args:
        diagnosis (dict): The mix diagnosis results.
    """
    if not isinstance(diagnosis, dict):
        print("Invalid mix diagnosis results.")
        return

    completion_time = diagnosis.get("completion_time", "N/A")
    error_flag = diagnosis.get("error", False)
    info = diagnosis.get("info", "No additional info")
    print("\n=== Mix Diagnosis Results ===")
    print(f"Completion Time: {completion_time}")
    print(f"Error Flag: {error_flag}")
    print(f"Info: {info}")

    payload = diagnosis.get("payload", {})
    if payload:
        print("\n--- Payload Details ---")
        for key, value in payload.items():
            print(f"{key}: {value}")
    else:
        print("No payload details available.")

    summary = payload.get("summary", {})
    if summary:
        print("\n--- Summary ---")
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        print("No summary available.")


def extract_summary(diagnosis):
    """
    Extracts the summary from mix diagnosis results.

    Args:
        diagnosis (dict): The mix diagnosis results.

    Returns:
        dict: The summary extracted from the payload, or an empty dict if not present.
    """
    payload = diagnosis.get("payload", {})
    return payload.get("summary", {})


def compare_summaries(summary_a, summary_b):
    """
    Compares two summary dictionaries from mix analysis and prints a side-by-side comparison.

    Args:
        summary_a (dict): Summary from Mix A.
        summary_b (dict): Summary from Mix B.
    """
    print("\n=== Mix Comparison Summary ===")
    # Create a set of all keys that exist in either summary.
    all_keys = set(summary_a.keys()).union(summary_b.keys())

    for key in all_keys:
        val_a = summary_a.get(key, "N/A")
        val_b = summary_b.get(key, "N/A")
        print(f"{key}:")
        print(f"  Mix A: {val_a}")
        print(f"  Mix B: {val_b}\n")


def main():
    """
    Main function to analyze and compare two audio mixes.

    Steps:
    1. Define two audio file URLs (e.g., different mixes or a reference track).
    2. Call the Tonn API to analyze each mix.
    3. Print full diagnosis details for both mixes.
    4. Extract summary data and compare the two mixes.
    """
    # Define the two audio file URLs.
    mix_a_url = "https://your-audio-file-location/mix_a.wav"  # Replace with your Mix A URL
    mix_b_url = "https://your-audio-file-location/mix_b.wav"  # Replace with your Mix B or reference track URL

    musical_style = "ROCK"  # Modify as needed (e.g., "TECHNO", "POP")
    is_master = True  # Modify based on whether your tracks are mastered

    print("Analyzing Mix A...")
    diagnosis_a = analyze_mix(mix_a_url, musical_style, is_master)

    print("\nAnalyzing Mix B...")
    diagnosis_b = analyze_mix(mix_b_url, musical_style, is_master)

    # Print full diagnosis details for each mix.
    print("\nFull Diagnosis for Mix A:")
    print_mix_diagnosis_results(diagnosis_a)

    print("\nFull Diagnosis for Mix B:")
    print_mix_diagnosis_results(diagnosis_b)

    # Extract summary data for comparison.
    summary_a = extract_summary(diagnosis_a)
    summary_b = extract_summary(diagnosis_b)

    # Compare the summaries.
    compare_summaries(summary_a, summary_b)


if __name__ == "__main__":
    main()
