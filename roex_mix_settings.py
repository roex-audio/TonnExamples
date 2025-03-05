import requests
import json
import time

# BASE_URL points to the API host. Replace it with your actual API host if different.
BASE_URL = "https://tonn.roexaudio.com"
API_KEY = "GO TO https://tonn-portal.roexaudio.com get an API key"

def print_mix_output_settings(settings):
    """
    Pretty-print mix output settings for each track.

    Args:
        settings (dict): A dictionary containing mix settings for each track.
    """
    for track, config in settings.items():
        print(f"\nTrack: {track}")
        # Iterate over each section of settings (e.g., drc_settings, eq_settings, etc.)
        for section, section_settings in config.items():
            print(f"  {section}:")
            # Check if the section contains a nested dictionary of settings.
            if isinstance(section_settings, dict):
                for key, value in section_settings.items():
                    print(f"    {key}: {value}")
            else:
                print(f"    {section_settings}")


def poll_preview_mix(task_id, headers, max_attempts=30, poll_interval=5):
    """
    Poll the /retrievepreviewmix endpoint until the preview mix is ready.

    This function sends a POST request with the task ID to the /retrievepreviewmix endpoint.
    It will repeatedly poll the endpoint until either the preview mix is ready (status code 200 with
    'MIX_TASK_PREVIEW_COMPLETED') or the maximum number of attempts is reached.

    NOTE: If you provide a webhookURL in the mix preview payload when creating the preview mix,
    the API will send a callback to that URL once the preview mix is ready. In that case, you would not
    need to poll this endpoint manually. Polling is used here for demonstration purposes.

    Args:
        task_id (str): The multitrack task ID returned from the preview mix creation.
        headers (dict): HTTP headers including Content-Type and API key.
        max_attempts (int): Maximum number of polling attempts.
        poll_interval (int): Seconds to wait between attempts.

    Returns:
        dict or None: The preview mix task results if ready, else None.
    """
    # Define the URL and payload for polling the preview mix.
    retrieve_url = f"{BASE_URL}/retrievepreviewmix"
    retrieve_payload = {
        "multitrackData": {
            "multitrackTaskId": task_id,
            "retrieveFXSettings": True  # Set to False unless FX settings are needed
        }
    }

    print("Polling for the preview mix URL...")
    attempt = 0
    while attempt < max_attempts:
        try:
            # Send a POST request to the /retrievepreviewmix endpoint.
            retrieve_response = requests.post(retrieve_url, json=retrieve_payload, headers=headers)
        except Exception as e:
            print("Error during POST request to /retrievepreviewmix:", e)
            return None

        try:
            # Parse the JSON response from the API.
            retrieve_data = retrieve_response.json()
        except Exception as e:
            print("Error parsing JSON response:", e)
            return None

        # Check if the response indicates that the task is still processing.
        if retrieve_response.status_code == 202:
            current_status = retrieve_data.get("status", "Processing")
            print(f"Attempt {attempt + 1}/{max_attempts}: Task still processing. Status: {current_status}.")
        elif retrieve_response.status_code == 200:
            # When the task is complete, verify the status.
            results = retrieve_data.get("previewMixTaskResults", {})
            status = results.get("status", "")
            if status == "MIX_TASK_PREVIEW_COMPLETED":
                print("Preview mix is complete.")
                return results
            else:
                print("Received 200 but unexpected status in response:", status)
                return None
        else:
            # Handle any unexpected HTTP status codes.
            print("Unexpected response code:", retrieve_response.status_code)
            print("Response:", retrieve_response.text)
            return None

        # Wait before trying again.
        time.sleep(poll_interval)
        attempt += 1

    print("Preview mix URL was not available after polling. Please try again later.")
    return None


def retrieve_final_mix(final_payload, headers):
    """
    Call the /retrievefinalmix endpoint to retrieve the final mix.

    This function sends a POST request to the /retrievefinalmix endpoint with the provided payload.
    It expects a 200 status code and returns the final mix task results if successful.

    Args:
        final_payload (dict): The payload containing final mix settings.
        headers (dict): HTTP headers including Content-Type and API key.

    Returns:
        dict or None: The final mix task results if ready, else None.
    """
    retrieve_url = f"{BASE_URL}/retrievefinalmix"
    print("Requesting final mix...")
    try:
        response = requests.post(retrieve_url, json=final_payload, headers=headers)
    except Exception as e:
        print("Error during POST request to /retrievefinalmix:", e)
        return None

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            print("Error parsing final mix JSON response:", e)
            return None
        # The final mix results are returned under 'applyAudioEffectsResults'
        results = data.get("applyAudioEffectsResults", {})
        return results
    else:
        print("Failed to retrieve final mix.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return None


def main():
    """
    Main function to handle preview and final mix creation.

    This function performs the following steps:
      1. Loads the preview mix payload and sends it to the /mixpreview endpoint.
      2. Polls the /retrievepreviewmix endpoint until the preview mix is ready.
         (Note: If you provided a webhookURL in the preview mix payload, you wouldn't need to poll.)
      3. Prints the preview mix URL, mix output settings, and stem URLs.
      4. If a final payload file is provided, updates it with the task ID and retrieves the final mix.
    """

    payload_file = "./initial_multitrack_mix_payload.json"
    final_payload = "./final_mix_settings.json"

    # Load the preview mix payload from the provided JSON file.
    try:
        with open(payload_file, "r") as f:
            preview_payload = json.load(f)
    except Exception as e:
        print("Error reading preview payload JSON file:", e)
        return

    # NOTE:
    # If you include a 'webhookURL' in your preview_payload, the API will send the preview mix results
    # to that URL once ready, and you wouldn't need to poll the /retrievepreviewmix endpoint.
    # Polling is used here for demonstration purposes.

    # Define HTTP headers with the API key.
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    # Create the preview mix by sending a POST request to the /mixpreview endpoint.
    mixpreview_url = f"{BASE_URL}/mixpreview"
    print(f"Sending POST request to {mixpreview_url} for preview mix...")
    try:
        response = requests.post(mixpreview_url, json=preview_payload, headers=headers)
    except Exception as e:
        print("Error during POST request to /mixpreview:", e)
        return

    # Check if the preview mix task was successfully created.
    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            print("Error parsing preview mix JSON response:", e)
            return
        task_id = data.get("multitrack_task_id")
        if not task_id:
            print("Error: Task ID not found in response:", data)
            return
        print("Mix preview task created successfully. Task ID:", task_id)
    else:
        print("Failed to create mix preview task.")
        print("Status code:", response.status_code)
        print("Response:", response.text)
        return

    # Poll for the preview mix results.
    preview_results = poll_preview_mix(task_id, headers)
    if preview_results is None:
        return

    # Print the preview mix URL.
    download_url = preview_results.get("download_url_preview_mixed")
    if download_url:
        print("\nPreview mix URL:", download_url)
    else:
        print("Preview mix URL is missing in the response.")

    # Print the preview mix output settings.
    mix_output_settings = preview_results.get("mix_output_settings", {})
    if mix_output_settings:
        print("\nMix Output Settings (Preview):")
        print_mix_output_settings(mix_output_settings)
    else:
        print("No mix output settings returned in preview mix.")

    # Print any preview stem URLs if available.
    stems = preview_results.get("stems", {})
    if stems:
        print("\nStems (Preview):")
        for name, url in stems.items():
            print(f"  {name}: {url}")

    # If a final mix payload file is provided, proceed to retrieve the final mix.
    if final_payload:
        try:
            with open(final_payload, "r") as f:
                final_payload = json.load(f)
        except Exception as e:
            print("Error reading final payload JSON file:", e)
            return

        # Update the final mix payload with the task ID from the preview mix.
        if "applyAudioEffectsData" in final_payload:
            final_payload["applyAudioEffectsData"]["multitrackTaskId"] = task_id
        else:
            print("Error: 'applyAudioEffectsData' key not found in final payload.")
            return

        # Retrieve the final mix using the updated payload.
        final_results = retrieve_final_mix(final_payload, headers)
        if final_results is None:
            return

        # Print the final mix URL.
        final_download_url = final_results.get("download_url_mixed")
        if final_download_url:
            print("\nFinal mix URL:", final_download_url)
        else:
            print("Final mix URL is missing in the response.")

        # Print the final mix output settings.
        final_mix_output_settings = final_results.get("mix_output_settings", {})
        if final_mix_output_settings:
            print("\nMix Output Settings (Final):")
            print_mix_output_settings(final_mix_output_settings)
        else:
            print("No mix output settings returned in final mix.")

        # Print any final stem URLs if available.
        final_stems = final_results.get("stems", {})
        if final_stems:
            print("\nStems (Final):")
            for name, url in final_stems.items():
                print(f"  {name}: {url}")


if __name__ == "__main__":
    main()
