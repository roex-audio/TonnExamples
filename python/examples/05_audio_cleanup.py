#!/usr/bin/env python3
"""
05_audio_cleanup.py - Clean Up Audio with the Tonn API

This example demonstrates how to clean up noisy or problematic audio 
recordings using the Tonn API's audio cleanup feature.

Common use cases:
- Remove background noise from vocals
- Clean up outdoor recordings (wind, traffic)
- Fix microphone bleed in live recordings
- Reduce hum, hiss, and other unwanted sounds

Supported sound sources:
- VOCAL_GROUP: Lead vocals
- BACKING_VOCALS_GROUP: Background vocals
- DRUMS_GROUP: Drum kit
- KICK_GROUP: Kick drum
- SNARE_GROUP: Snare drum
- PERCS_GROUP: Percussion
- E_GUITAR_GROUP: Electric guitar
- A_GUITAR_GROUP: Acoustic guitar
- STRINGS_GROUP: String instruments

Usage:
    python 05_audio_cleanup.py <audio_file> [--source SOUND_SOURCE]

Examples:
    python 05_audio_cleanup.py noisy_vocals.wav
    python 05_audio_cleanup.py drums.wav --source DRUMS_GROUP
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


SOUND_SOURCES = [
    "VOCAL_GROUP",
    "BACKING_VOCALS_GROUP", 
    "DRUMS_GROUP",
    "KICK_GROUP",
    "SNARE_GROUP",
    "PERCS_GROUP",
    "E_GUITAR_GROUP",
    "A_GUITAR_GROUP",
    "STRINGS_GROUP"
]


def print_cleanup_results(results: dict, input_filename: str) -> None:
    """Display the cleanup results."""
    print("\n" + "=" * 50)
    print("AUDIO CLEANUP RESULTS")
    print("=" * 50)
    
    print(f"\nCompletion Time: {results.get('completion_time', 'N/A')}")
    
    if results.get("error"):
        print(f"⚠️  Error: {results.get('info', 'Unknown error')}")
        return
    
    print(f"Info: {results.get('info', 'Cleanup complete')}")
    
    download_url = results.get("cleaned_audio_file_location")
    if download_url:
        print(f"\n📥 Download URL: {download_url}")
    else:
        print("\n⚠️  No download URL in response")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up audio using the Tonn API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Sound Sources:
  {chr(10).join(f'  - {s}' for s in SOUND_SOURCES)}

Examples:
  python 05_audio_cleanup.py vocals.wav
  python 05_audio_cleanup.py drums.flac --source DRUMS_GROUP
        """
    )
    parser.add_argument("input_file", help="Path to audio file (.wav, .flac only)")
    parser.add_argument("-s", "--source", default="VOCAL_GROUP",
                       choices=SOUND_SOURCES,
                       help="Sound source type (default: VOCAL_GROUP)")

    args = parser.parse_args()

    # Validate file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)
    
    # Check file type (cleanup only supports WAV and FLAC)
    ext = os.path.splitext(args.input_file)[1].lower()
    if ext not in ['.wav', '.flac']:
        print(f"Error: Audio cleanup only supports .wav and .flac files")
        print(f"Your file: {ext}")
        sys.exit(1)

    client = TonnClient()
    filename = os.path.basename(args.input_file)

    print(f"\n🎤 Audio Cleanup")
    print(f"   File: {filename}")
    print(f"   Source Type: {args.source}")
    print()

    # Upload the file
    print("📤 Uploading file...")
    readable_url = client.upload_local_file(args.input_file)
    if not readable_url:
        print("Failed to upload file. Exiting.")
        sys.exit(1)

    # Build cleanup payload
    payload = {
        "audioCleanupData": {
            "audioFileLocation": readable_url,
            "soundSource": args.source
        }
    }

    # Run cleanup
    print("\n🧹 Running audio cleanup...")
    response = client.post("/audio-cleanup", payload)

    if not response:
        print("Cleanup request failed. Check your API key and try again.")
        sys.exit(1)

    # Display top-level response
    print(f"\n{'=' * 50}")
    print(f"Error: {response.get('error', False)}")
    print(f"Message: {response.get('message', 'No message')}")
    print(f"Info: {response.get('info', 'No info')}")

    # Display cleanup results
    cleanup_results = response.get("audioCleanupResults")
    if cleanup_results:
        print_cleanup_results(cleanup_results, filename)
        
        # Download the cleaned file
        download_url = cleanup_results.get("cleaned_audio_file_location")
        if download_url:
            output_filename = f"cleaned_{filename}"
            print(f"\n📥 Downloading cleaned audio...")
            client.download_file(download_url, output_filename)
            print(f"\n✅ Cleaned audio saved to: {output_filename}")
    else:
        print("\n⚠️  No cleanup results in response")


if __name__ == "__main__":
    main()

