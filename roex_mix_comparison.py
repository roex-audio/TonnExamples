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


def print_mix_diagnosis_results(diagnosis):
    """
    Pretty-prints the full mix diagnosis results.

    Args:
        diagnosis (dict): The mix diagnosis results.
    """
    if not isinstance(diagnosis, dict):
        print("Invalid mix diagnosis results.")
        return

    print("\n=== Full Mix Diagnosis Results ===")
    completion_time = diagnosis.get("completion_time", "N/A")
    error_flag = diagnosis.get("error", False)
    info = diagnosis.get("info", "No additional info")
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

    # Extract production metrics from each diagnosis.
    production_metrics_a = extract_production_metrics(diagnosis_a)
    production_metrics_b = extract_production_metrics(diagnosis_b)

    # Compare the production metrics using smart difference analysis.
    compare_dicts_with_smart_diff(production_metrics_a, production_metrics_b, title="Production Metrics Comparison")

    # Extract and compare tonal profile data.
    tonal_profile_a = extract_tonal_profile(diagnosis_a)
    tonal_profile_b = extract_tonal_profile(diagnosis_b)
    compare_dicts_with_smart_diff(tonal_profile_a, tonal_profile_b, title="Tonal Profile Comparison")


if __name__ == "__main__":
    main()
