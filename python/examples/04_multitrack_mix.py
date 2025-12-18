#!/usr/bin/env python3
"""
04_multitrack_mix.py - Create a Multitrack Mix with the Tonn API

This example demonstrates how to mix multiple audio stems (drums, bass, 
vocals, etc.) into a cohesive mix using the Tonn API.

The workflow:
1. Create a PREVIEW mix (AI suggests mix settings)
2. Review the mix output settings
3. Apply custom audio effects (EQ, compression, panning)
4. Retrieve the FINAL mix

Audio Effects Available:
- Gain Control: -60 to +12 dB per track
- Panning: -60° (left) to +60° (right)
- 6-Band Parametric EQ: 20Hz - 20kHz
- Compression: Threshold, ratio, attack, release

Usage:
    python 04_multitrack_mix.py

This script uses JSON payload files from the payloads/ directory.
Edit those files to customize your mix.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


def print_audio_effects(track_data: list) -> None:
    """Display the audio effects settings for each track."""
    for idx, track in enumerate(track_data, 1):
        track_url = track.get("trackURL", "Unknown")
        track_name = track_url.split("/")[-1] if "/" in track_url else track_url
        
        print(f"\n{'=' * 50}")
        print(f"Track {idx}: {track_name}")
        print(f"{'=' * 50}")
        
        # Gain
        gain = track.get("gainDb", 0)
        print(f"  Gain: {gain:+.1f} dB")
        
        # Panning
        panning = track.get("panning_settings", {})
        if panning:
            angle = panning.get("panning_angle", 0)
            position = "Center" if angle == 0 else f"{abs(angle)}° {'Left' if angle < 0 else 'Right'}"
            print(f"  Panning: {position}")
        
        # EQ settings
        eq = track.get("eq_settings", {})
        if eq:
            print(f"\n  EQ (6-band Parametric):")
            for band_num in range(1, 7):
                band = eq.get(f"band_{band_num}", {})
                if band:
                    freq = band.get("centre_freq", 0)
                    gain = band.get("gain", 0)
                    q = band.get("q", 0)
                    print(f"    Band {band_num}: {freq:>5} Hz | {gain:+5.1f} dB | Q: {q:.1f}")
        
        # Compression
        comp = track.get("compression_settings", {})
        if comp:
            print(f"\n  Compression:")
            print(f"    Threshold: {comp.get('threshold', 0):+.1f} dB")
            print(f"    Ratio:     {comp.get('ratio', 1):.1f}:1")
            print(f"    Attack:    {comp.get('attack_ms', 0):.1f} ms")
            print(f"    Release:   {comp.get('release_ms', 0):.1f} ms")


def print_mix_output_settings(settings: dict) -> None:
    """Display the mix output settings returned by the API."""
    for track_name, config in settings.items():
        print(f"\nTrack: {track_name}")
        for section, values in config.items():
            print(f"  {section}:")
            if isinstance(values, dict):
                for key, val in values.items():
                    print(f"    {key}: {val}")
            else:
                print(f"    {values}")


def poll_preview_mix(client: TonnClient, task_id: str) -> dict:
    """Poll for preview mix completion."""
    payload = {
        "multitrackData": {
            "multitrackTaskId": task_id,
            "retrieveFXSettings": True
        }
    }
    
    return client.poll_for_result(
        endpoint="/retrievepreviewmix",
        payload=payload,
        result_key="previewMixTaskResults",
        max_attempts=30,
        poll_interval=5
    )


def main():
    # Paths to payload files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    payloads_dir = os.path.join(os.path.dirname(script_dir), "payloads")
    
    preview_payload_path = os.path.join(payloads_dir, "multitrack_mix.json")
    final_payload_path = os.path.join(payloads_dir, "final_mix_settings.json")
    
    # Load preview payload
    try:
        with open(preview_payload_path, "r") as f:
            preview_payload = json.load(f)
    except FileNotFoundError:
        print(f"Error: Payload file not found: {preview_payload_path}")
        print("Make sure you're running from the examples directory.")
        sys.exit(1)
    
    client = TonnClient()
    
    print("\n" + "=" * 60)
    print("STEP 1: Create Preview Mix")
    print("=" * 60)
    
    # Create preview mix
    print("\n📤 Sending tracks for preview mix...")
    response = client.post("/mixpreview", preview_payload)
    
    if not response or response.get("error"):
        print(f"❌ Failed to create preview: {response}")
        sys.exit(1)
    
    task_id = response.get("multitrack_task_id")
    if not task_id:
        print("❌ No task ID in response")
        sys.exit(1)
    
    print(f"✓ Preview task created. Task ID: {task_id}")
    
    # Poll for preview results
    print("\n⏳ Waiting for preview mix...")
    preview_results = poll_preview_mix(client, task_id)
    
    if not preview_results:
        print("Preview timed out. Try again later.")
        sys.exit(1)
    
    # Display preview results
    preview_url = preview_results.get("download_url_preview_mixed")
    if preview_url:
        print(f"\n🎵 Preview Mix URL: {preview_url}")
    
    mix_settings = preview_results.get("mix_output_settings", {})
    if mix_settings:
        print("\n📊 AI-Suggested Mix Settings:")
        print_mix_output_settings(mix_settings)
    
    stems = preview_results.get("stems", {})
    if stems:
        print("\n🎛️  Stems:")
        for name, url in stems.items():
            print(f"  {name}: {url}")
    
    print("\n" + "=" * 60)
    print("STEP 2: Apply Custom Audio Effects")
    print("=" * 60)
    
    # Load final mix settings
    try:
        with open(final_payload_path, "r") as f:
            final_payload = json.load(f)
    except FileNotFoundError:
        print(f"Skipping final mix - payload not found: {final_payload_path}")
        return
    
    # Update with the task ID
    if "applyAudioEffectsData" in final_payload:
        final_payload["applyAudioEffectsData"]["multitrackTaskId"] = task_id
        
        # Show what effects will be applied
        track_data = final_payload["applyAudioEffectsData"].get("trackData", [])
        if track_data:
            print("\n🎚️  Applying Audio Effects:")
            print_audio_effects(track_data)
    else:
        print("❌ Invalid final payload format")
        sys.exit(1)
    
    # Retrieve final mix
    print("\n\n📤 Requesting final mix with custom effects...")
    final_response = client.post("/retrievefinalmix", final_payload)
    
    if not final_response:
        print("❌ Failed to retrieve final mix")
        sys.exit(1)
    
    final_results = final_response.get("applyAudioEffectsResults", {})
    
    # Display final mix results
    final_url = final_results.get("download_url_mixed")
    if final_url:
        print(f"\n🎵 Final Mix URL: {final_url}")
        
        # Optionally download
        # client.download_file(final_url, "final_mix.wav")
    
    final_stems = final_results.get("stems", {})
    if final_stems:
        print("\n🎛️  Final Stems:")
        for name, url in final_stems.items():
            print(f"  {name}: {url}")
    
    print("\n" + "=" * 60)
    print("✅ Multitrack Mix Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

