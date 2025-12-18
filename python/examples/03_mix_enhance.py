#!/usr/bin/env python3
"""
03_mix_enhance.py - Enhance Your Mix with the Tonn API

This example demonstrates the Mix Enhance feature which automatically
improves your stereo mix without needing individual stems.

What Mix Enhance does:
- Fixes loudness issues for streaming platforms
- Corrects stereo width problems
- Improves tonal balance
- Optionally applies mastering
- Can perform stem separation and processing

The workflow:
1. First create a PREVIEW (quick, free to experiment)
2. Review the preview
3. Then create the FULL enhancement

Usage:
    python 03_mix_enhance.py [audio_url]

If no URL provided, uses a demo track from the test bucket.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


def start_enhance_preview(client: TonnClient, audio_url: str, musical_style: str = "POP") -> str:
    """
    Start a Mix Enhance preview job.
    
    Returns the task ID for tracking the job.
    """
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": False,
            "fixClippingIssues": True,
            "fixDRCIssues": True,
            "fixStereoWidthIssues": True,
            "fixTonalProfileIssues": True,
            "fixLoudnessIssues": True,
            "applyMastering": True,
            "loudnessPreference": "STREAMING_LOUDNESS",
            "stemProcessing": False
        }
    }
    
    print("🎚️  Starting Mix Enhance preview...")
    response = client.post("/mixenhancepreview", payload)
    
    if response and not response.get("error"):
        task_id = response.get("mixrevive_task_id")
        print(f"✓ Preview task created. Task ID: {task_id}")
        return task_id
    else:
        error_msg = response.get("message") if response else "No response"
        print(f"❌ Failed to start preview: {error_msg}")
        return None


def start_full_enhance(client: TonnClient, audio_url: str, musical_style: str = "POP") -> str:
    """
    Start a full Mix Enhance job (uses credits).
    
    Returns the task ID for tracking the job.
    """
    payload = {
        "mixReviveData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": False,
            "fixClippingIssues": True,
            "fixDRCIssues": True,
            "fixStereoWidthIssues": True,
            "fixTonalProfileIssues": True,
            "fixLoudnessIssues": True,
            "applyMastering": True,
            "loudnessPreference": "STREAMING_LOUDNESS",
            "stemProcessing": False
        }
    }
    
    print("🎚️  Starting full Mix Enhance...")
    response = client.post("/mixenhance", payload)
    
    if response and not response.get("error"):
        task_id = response.get("mixrevive_task_id")
        print(f"✓ Full enhance task created. Task ID: {task_id}")
        return task_id
    else:
        error_msg = response.get("message") if response else "No response"
        print(f"❌ Failed to start enhancement: {error_msg}")
        return None


def poll_enhanced_track(client: TonnClient, task_id: str, max_attempts: int = 70) -> dict:
    """Poll for the enhanced track result."""
    payload = {
        "mixReviveData": {
            "mixReviveTaskId": task_id
        }
    }
    
    return client.poll_for_result(
        endpoint="/retrieveenhancedtrack",
        payload=payload,
        result_key="revivedTrackTaskResults",
        max_attempts=max_attempts,
        poll_interval=5,
        processing_status_codes=(202, 404, 503)
    )


def download_results(client: TonnClient, results: dict, prefix: str) -> None:
    """Download the enhanced track and any stems."""
    # Main enhanced track
    preview_url = results.get("download_url_preview_revived")
    full_url = results.get("download_url_revived")
    
    download_url = full_url or preview_url
    if download_url:
        filename = f"{prefix}_enhanced.wav"
        client.download_file(download_url, filename)
    
    # Stems (if any)
    stems = results.get("stems", {})
    for stem_name, stem_url in stems.items():
        filename = f"{prefix}_stem_{stem_name}.wav"
        client.download_file(stem_url, filename)


def main():
    # Demo audio URL (or use command line argument)
    demo_url = "https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3"
    
    if len(sys.argv) > 1:
        audio_url = sys.argv[1]
        print(f"Using provided URL: {audio_url}")
    else:
        audio_url = demo_url
        print(f"Using demo track: {audio_url}")
    
    client = TonnClient()
    
    print("\n" + "=" * 60)
    print("STEP 1: Create Preview Enhancement")
    print("=" * 60)
    
    # Start preview
    preview_task_id = start_enhance_preview(client, audio_url, "HIPHOP_GRIME")
    if not preview_task_id:
        print("Failed to create preview. Exiting.")
        sys.exit(1)
    
    # Poll for preview results
    print("\n⏳ Waiting for preview to complete...")
    preview_results = poll_enhanced_track(client, preview_task_id)
    
    if not preview_results:
        print("Preview timed out or failed.")
        sys.exit(1)
    
    print("\n📊 Preview Results:")
    print(f"  Status: {preview_results.get('status', 'Unknown')}")
    
    # Download preview
    download_results(client, preview_results, "preview")
    
    print("\n" + "=" * 60)
    print("STEP 2: Create Full Enhancement")
    print("=" * 60)
    
    # Start full enhancement
    full_task_id = start_full_enhance(client, audio_url, "HIPHOP_GRIME")
    if not full_task_id:
        print("Failed to start full enhancement. Exiting.")
        sys.exit(1)
    
    # Poll for full results
    print("\n⏳ Waiting for full enhancement to complete...")
    full_results = poll_enhanced_track(client, full_task_id, max_attempts=50)
    
    if not full_results:
        print("Full enhancement timed out or failed.")
        sys.exit(1)
    
    print("\n📊 Full Enhancement Results:")
    print(f"  Status: {full_results.get('status', 'Unknown')}")
    
    # Download full results
    download_results(client, full_results, "enhanced")
    
    print("\n" + "=" * 60)
    print("✅ Mix Enhance Complete!")
    print("=" * 60)
    print("\nYour enhanced files have been saved to the current directory.")


if __name__ == "__main__":
    main()

