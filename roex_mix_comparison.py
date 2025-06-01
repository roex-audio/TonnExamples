import requests
import json
import os
import argparse
import mimetypes

# BASE_URL points to the API host. Replace with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
# Read API Key from environment variable for better security
API_KEY = os.environ.get("TONN_API_KEY")

if not API_KEY:
    print("Error: TONN_API_KEY environment variable not set.")
    print("GO TO https://tonn-portal.roexaudio.com to get an API key")
    exit(1)

# === Helper Functions ===

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

def extract_production_metrics(diagnosis):
    """
    Extracts production-related metrics from the diagnosis payload.
    Excludes the 'summary' field.
    Args:
        diagnosis (dict): The mix diagnosis results.
    Returns:
        dict: Production metrics.
    """
    payload = diagnosis.get("payload", {})
    production_keys = [
        "bit_depth", "clipping", "if_master_drc", "if_master_loudness",
        "if_mix_drc", "if_mix_loudness", "integrated_loudness_lufs", "mix_style",
        "mono_compatible", "musical_style", "peak_loudness_dbfs", "phase_issues",
        "sample_rate", "stereo_field"
    ]
    metrics = {key: payload.get(key, "N/A") for key in production_keys}
    return metrics

def extract_tonal_profile(diagnosis):
    """
    Extracts the tonal profile from the diagnosis payload.
    Args:
        diagnosis (dict): The mix diagnosis results.
    Returns:
        dict: Tonal profile data.
    """
    payload = diagnosis.get("payload", {})
    return payload.get("tonal_profile", {})

def smart_compare_value(key, val_a, val_b):
    """
    Compares two values and returns formatted (color-coded) strings and a basic interpretation.
    For numeric values, if the difference exceeds a threshold, the values are marked in red.
    For non-numeric values, any difference is highlighted in red.
    Args:
        key (str): The field name.
        val_a: Value from Mix A.
        val_b: Value from Mix B.
    Returns:
        tuple: (formatted_val_a, formatted_val_b, interpretation)
    """
    # ANSI escape codes for coloring
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    # Pre-defined numeric thresholds for specific keys
    numeric_thresholds = {
        "integrated_loudness_lufs": 1.0,
        "peak_loudness_dbfs": 0.5,
        "bit_depth": 0  # any difference is significant
    }

    interpretation = ""

    # Try numeric comparison if possible
    try:
        num_a = float(val_a)
        num_b = float(val_b)
        is_numeric = True
    except (ValueError, TypeError):
        is_numeric = False

    if is_numeric:
        diff = abs(num_a - num_b)
        threshold = numeric_thresholds.get(key, 0.0)
        if threshold and diff > threshold:
            formatted_a = f"{RED}{val_a}{RESET}"
            formatted_b = f"{RED}{val_b}{RESET}"
            interpretation = f"Difference of {diff:.2f} exceeds threshold of {threshold}"
        else:
            formatted_a = f"{GREEN}{val_a}{RESET}"
            formatted_b = f"{GREEN}{val_b}{RESET}"
            if diff > 0:
                interpretation = f"Difference of {diff:.2f} is within acceptable range."
            else:
                interpretation = "Values are identical."
    else:
        # For non-numeric values, a simple equality check.
        if val_a == val_b:
            formatted_a = f"{GREEN}{val_a}{RESET}"
            formatted_b = f"{GREEN}{val_b}{RESET}"
            interpretation = "Values are identical."
        else:
            formatted_a = f"{RED}{val_a}{RESET}"
            formatted_b = f"{RED}{val_b}{RESET}"
            interpretation = "Values differ."

    # Handle potential N/A values explicitly
    if val_a == "N/A" or val_b == "N/A":
        formatted_a = f"{val_a}" # No color for N/A
        formatted_b = f"{val_b}"
        if val_a != val_b:
             interpretation = "One value is N/A."
        else:
             interpretation = "Both values are N/A."

    return formatted_a, formatted_b, interpretation

def compare_dicts_with_smart_diff(dict_a, dict_b, title="Comparison"):
    """
    Compares two dictionaries field by field using smart difference analysis,
    printing color-coded differences and basic interpretations.
    Args:
        dict_a (dict): Dictionary for Mix A.
        dict_b (dict): Dictionary for Mix B.
        title (str): Title for the comparison block.
    """
    print(f"\n=== {title} ===")
    all_keys = set(dict_a.keys()).union(dict_b.keys())
    for key in sorted(all_keys):
        val_a = dict_a.get(key, "N/A")
        val_b = dict_b.get(key, "N/A")
        formatted_a, formatted_b, interpretation = smart_compare_value(key, val_a, val_b)
        print(f"{key}:")
        print(f"  Mix A: {formatted_a}")
        print(f"  Mix B: {formatted_b}")
        print(f"  Interpretation: {interpretation}\n")

def main():
    """
    Main function to analyze and compare two audio mixes.
    Steps:
    1. Define two audio file URLs (e.g., different mixes or a reference track).
    2. Call the Tonn API to analyze each mix.
    3. Print full diagnosis details for both mixes.
    4. Extract summary data and compare the two mixes.
    """
    # --- Command Line Argument Parsing ---
    parser = argparse.ArgumentParser(description="Compare two audio mixes using the Tonn Roex API.")
    parser.add_argument("input_file_a", help="Path to the first input audio file (.mp3, .wav, .flac)")
    parser.add_argument("input_file_b", help="Path to the second input audio file (.mp3, .wav, .flac)")
    parser.add_argument("musical_style", help="Musical style for analysis (e.g., ROCK, POP)")
    parser.add_argument("--is-master", action='store_true', help="Flag if the input files are masters (default: False)")

    args = parser.parse_args()

    files_to_process = {
        "A": args.input_file_a,
        "B": args.input_file_b
    }
    readable_urls = {}
    analysis_results = {}

    # --- Upload Files and Get Readable URLs ---
    for mix_label, local_filepath in files_to_process.items():
        print(f"\n--- Processing Mix {mix_label}: {local_filepath} ---")
        filename = os.path.basename(local_filepath)

        if not os.path.isfile(local_filepath):
            print(f"Error: Input file not found: {local_filepath}")
            return # Exit if any file is missing

        content_type = get_content_type(filename)
        if not content_type:
            print(f"Error: Unsupported file type for {filename}. Skipping analysis.")
            return

        signed_url, readable_url = get_upload_urls(filename, content_type, API_KEY)
        if not signed_url or not readable_url:
            print(f"Failed to get upload URLs for {filename}. Skipping analysis.")
            return

        upload_success = upload_file_to_signed_url(signed_url, local_filepath, content_type)
        if not upload_success:
            print(f"File upload failed for {filename}. Skipping analysis.")
            return

        readable_urls[mix_label] = readable_url
        print(f"Using readable URL for Mix {mix_label}: {readable_url}")

    # --- Analyze Mixes using Readable URLs ---
    print("\n--- Starting Mix Analysis ---")
    for mix_label, readable_url in readable_urls.items():
        print(f"\nAnalyzing Mix {mix_label}...")
        diagnosis = analyze_mix(readable_url, args.musical_style, args.is_master)
        if diagnosis:
            analysis_results[mix_label] = diagnosis
            print(f"Analysis complete for Mix {mix_label}.")
            # Optional: Print full details immediately
            # print_mix_diagnosis_results(diagnosis)
        else:
            print(f"Analysis failed for Mix {mix_label}. Cannot perform comparison.")
            return # Exit if analysis fails

    # --- Comparison --- (Only proceeds if both analyses were successful)
    if len(analysis_results) == 2:
        print("\n" + "=" * 60)
        print("Mix Comparison Results")
        print("=" * 60)

        diagnosis_a = analysis_results["A"]
        diagnosis_b = analysis_results["B"]

        # Compare Production Metrics
        metrics_a = extract_production_metrics(diagnosis_a)
        metrics_b = extract_production_metrics(diagnosis_b)
        compare_dicts_with_smart_diff(metrics_a, metrics_b, "Production Metrics Comparison")

        # Compare Tonal Profiles
        tonal_a = extract_tonal_profile(diagnosis_a)
        tonal_b = extract_tonal_profile(diagnosis_b)
        compare_dicts_with_smart_diff(tonal_a, tonal_b, "Tonal Profile Comparison")

        print("\n" + "=" * 60)
        print("End of Comparison")
        print("=" * 60)
    else:
        print("\nComparison could not be performed because one or both analyses failed.")


if __name__ == "__main__":
    main()
