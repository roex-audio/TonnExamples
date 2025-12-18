#!/usr/bin/env python3
"""
06_batch_mastering.py - Batch Master an Album with the Tonn API

This example demonstrates how to master multiple tracks (an EP or album)
with consistent settings for a cohesive release.

Benefits of batch mastering:
- Consistent loudness across all tracks
- Unified sonic character for the release
- Efficient processing of multiple files

The workflow for each track:
1. Upload the audio file
2. Create a mastering preview
3. Poll until preview is ready
4. Retrieve the final master
5. Download the mastered file

Usage:
    python 06_batch_mastering.py <input_directory> [options]

Options:
    -o, --output-dir   Output directory (default: ./mastered_output)
    --style           Musical style (default: ROCK_INDIE)
    --loudness        Desired loudness: QUIET, MEDIUM, LOUD (default: MEDIUM)

Examples:
    python 06_batch_mastering.py ./my_album
    python 06_batch_mastering.py ./tracks -o ./masters --style POP --loudness MEDIUM
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


SUPPORTED_EXTENSIONS = ['.mp3', '.wav', '.flac']


def poll_preview_master(client: TonnClient, task_id: str) -> dict:
    """Poll for mastering preview completion."""
    payload = {
        "masteringData": {
            "masteringTaskId": task_id
        }
    }
    
    return client.poll_for_result(
        endpoint="/retrievepreviewmaster",
        payload=payload,
        result_key="previewMasterTaskResults",
        max_attempts=30,
        poll_interval=5
    )


def retrieve_final_master(client: TonnClient, task_id: str) -> dict:
    """Retrieve the final mastered track."""
    payload = {
        "masteringData": {
            "masteringTaskId": task_id
        }
    }
    
    print("📥 Retrieving final master...")
    response = client.post("/retrievefinalmaster", payload)
    
    if response:
        return response.get("finalMasterTaskResults")
    return None


def process_track(client: TonnClient, filepath: str, output_dir: str, 
                  style: str, loudness: str, sample_rate: str) -> bool:
    """Process a single track through mastering."""
    filename = os.path.basename(filepath)
    name_without_ext, ext = os.path.splitext(filename)
    
    print(f"\n{'=' * 60}")
    print(f"Processing: {filename}")
    print(f"{'=' * 60}")
    
    # Upload the file
    print("\n📤 Uploading...")
    readable_url = client.upload_local_file(filepath)
    if not readable_url:
        print(f"❌ Failed to upload {filename}")
        return False
    
    # Create mastering preview
    preview_payload = {
        "masteringData": {
            "trackData": [{"trackURL": readable_url}],
            "musicalStyle": style,
            "desiredLoudness": loudness,
            "sampleRate": sample_rate
        }
    }
    
    print("\n🎚️  Creating mastering preview...")
    response = client.post("/masteringpreview", preview_payload)
    
    if not response:
        print(f"❌ Failed to create preview for {filename}")
        return False
    
    task_id = response.get("mastering_task_id")
    if not task_id:
        print(f"❌ No task ID in response for {filename}")
        return False
    
    print(f"✓ Preview task created: {task_id}")
    
    # Poll for preview
    print("\n⏳ Waiting for preview...")
    preview_results = poll_preview_master(client, task_id)
    
    if not preview_results:
        print(f"❌ Preview timed out for {filename}")
        return False
    
    preview_url = preview_results.get("previewMasterTrackURL")
    print(f"✓ Preview ready: {preview_url[:50]}..." if preview_url else "✓ Preview ready")
    
    # Retrieve final master
    final_results = retrieve_final_master(client, task_id)
    
    if not final_results:
        print(f"❌ Failed to retrieve final master for {filename}")
        return False
    
    final_url = final_results.get("download_url_mastered")
    if not final_url:
        print(f"❌ No download URL for {filename}")
        return False
    
    # Download the mastered file
    output_filename = os.path.join(output_dir, f"{name_without_ext}_mastered{ext}")
    print(f"\n📥 Downloading mastered track...")
    
    if client.download_file(final_url, output_filename):
        print(f"✅ Saved: {output_filename}")
        return True
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Batch master audio files using the Tonn API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Musical Styles:
  ROCK, ROCK_INDIE, POP, ELECTRONIC, HIPHOP_GRIME, ACOUSTIC,
  SINGER_SONGWRITER, JAZZ, CLASSICAL, and more.

Loudness Options:
  QUIET   - For classical, jazz, acoustic
  MEDIUM  - Industry standard (~-14 LUFS for streaming)
  LOUD    - For rock, electronic, hip-hop

Examples:
  python 06_batch_mastering.py ./my_album
  python 06_batch_mastering.py ./tracks -o ./masters --style POP
  python 06_batch_mastering.py ./ep --loudness LOUD --style ELECTRONIC
        """
    )
    parser.add_argument("input_dir", help="Directory containing audio files")
    parser.add_argument("-o", "--output-dir", default="./mastered_output",
                       help="Output directory (default: ./mastered_output)")
    parser.add_argument("--style", default="ROCK_INDIE",
                       help="Musical style (default: ROCK_INDIE)")
    parser.add_argument("--loudness", default="MEDIUM",
                       choices=["QUIET", "MEDIUM", "LOUD"],
                       help="Desired loudness (default: MEDIUM)")
    parser.add_argument("--sample-rate", default="44100",
                       help="Sample rate (default: 44100)")

    args = parser.parse_args()

    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find audio files
    audio_files = []
    for filename in sorted(os.listdir(args.input_dir)):
        _, ext = os.path.splitext(filename)
        if ext.lower() in SUPPORTED_EXTENSIONS:
            audio_files.append(os.path.join(args.input_dir, filename))
    
    if not audio_files:
        print(f"No supported audio files found in {args.input_dir}")
        print(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("BATCH MASTERING")
    print("=" * 60)
    print(f"\nInput:     {args.input_dir}")
    print(f"Output:    {args.output_dir}")
    print(f"Style:     {args.style}")
    print(f"Loudness:  {args.loudness}")
    print(f"Tracks:    {len(audio_files)}")
    
    client = TonnClient()
    
    # Process each track
    success_count = 0
    failed_count = 0
    
    for filepath in audio_files:
        if process_track(client, filepath, args.output_dir, 
                        args.style, args.loudness, args.sample_rate):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH MASTERING COMPLETE")
    print("=" * 60)
    print(f"\n✅ Successful: {success_count}")
    if failed_count:
        print(f"❌ Failed: {failed_count}")
    print(f"\nMastered files saved to: {args.output_dir}")


if __name__ == "__main__":
    main()

