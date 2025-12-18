#!/usr/bin/env python3
"""
01_mix_analysis.py - Analyze Your Mix with the Tonn API

This example demonstrates how to analyze a mixed or mastered audio track
using the Tonn API's mix diagnosis feature (powered by Mix Check Studio).

What this does:
- Uploads your audio file to cloud storage
- Analyzes loudness, dynamic range, stereo field, and tonal balance
- Provides actionable feedback for improving your mix

Usage:
    python 01_mix_analysis.py <audio_file> <musical_style> [--is-master]

Example:
    python 01_mix_analysis.py my_track.wav POP --is-master
    python 01_mix_analysis.py demo.mp3 ROCK

Musical styles: ROCK, POP, ELECTRONIC, HIPHOP_GRIME, ACOUSTIC, ROCK_INDIE, etc.
"""

import sys
import os
import argparse

# Add the parent directory to path so we can import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


def print_diagnosis_results(diagnosis: dict) -> None:
    """Pretty-print the mix diagnosis results."""
    if not isinstance(diagnosis, dict):
        print("No valid diagnosis results found.")
        return

    print("\n" + "=" * 60)
    print("MIX DIAGNOSIS RESULTS")
    print("=" * 60)

    # Completion info
    print(f"\nCompletion Time: {diagnosis.get('completion_time', 'N/A')}")
    if diagnosis.get('error'):
        print(f"⚠️  Error: {diagnosis.get('info', 'Unknown error')}")
        return

    # Payload details
    payload = diagnosis.get("payload", {})
    if payload:
        print("\n--- Technical Details ---")
        
        # Key metrics
        metrics = [
            ("Bit Depth", payload.get("bit_depth")),
            ("Sample Rate", payload.get("sample_rate")),
            ("Integrated Loudness (LUFS)", payload.get("integrated_loudness_lufs")),
            ("Peak Loudness (dBFS)", payload.get("peak_loudness_dbfs")),
            ("Clipping", payload.get("clipping")),
            ("Stereo Field", payload.get("stereo_field")),
            ("Mono Compatible", payload.get("mono_compatible")),
            ("Phase Issues", payload.get("phase_issues")),
        ]
        
        for name, value in metrics:
            if value is not None:
                print(f"  {name}: {value}")
        
        # Mastering evaluation
        if payload.get("if_master_drc"):
            print(f"\n  Master DRC Evaluation: {payload.get('if_master_drc')}")
        if payload.get("if_master_loudness"):
            print(f"  Master Loudness Evaluation: {payload.get('if_master_loudness')}")

    # Summary
    summary = payload.get("summary", {})
    if summary:
        print("\n--- Recommendations ---")
        for idx, (key, value) in enumerate(summary.items(), 1):
            print(f"  {idx}. {value}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a mix/master using the Tonn API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 01_mix_analysis.py track.wav POP
  python 01_mix_analysis.py master.mp3 ROCK --is-master
  python 01_mix_analysis.py demo.flac ELECTRONIC

Musical Styles:
  ROCK, POP, ELECTRONIC, HIPHOP_GRIME, ACOUSTIC, ROCK_INDIE, 
  SINGER_SONGWRITER, JAZZ, CLASSICAL, and more.
        """
    )
    parser.add_argument("input_file", help="Path to audio file (.mp3, .wav, .flac)")
    parser.add_argument("musical_style", help="Musical style (e.g., ROCK, POP)")
    parser.add_argument("--is-master", action="store_true", 
                       help="Flag if the input is a mastered track")

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: File not found: {args.input_file}")
        sys.exit(1)

    # Initialize client
    client = TonnClient()

    # Upload the file
    print(f"\n📤 Uploading {os.path.basename(args.input_file)}...")
    readable_url = client.upload_local_file(args.input_file)
    if not readable_url:
        print("Failed to upload file. Exiting.")
        sys.exit(1)

    # Build the analysis payload
    payload = {
        "mixDiagnosisData": {
            "audioFileLocation": readable_url,
            "musicalStyle": args.musical_style.upper(),
            "isMaster": args.is_master
        }
    }

    # Run the analysis
    print(f"\n🔍 Analyzing your {'master' if args.is_master else 'mix'}...")
    response = client.post("/mixanalysis", payload)
    
    if not response:
        print("Analysis failed. Check your API key and try again.")
        sys.exit(1)

    # Display results
    if response.get("error"):
        print(f"❌ Error: {response.get('message', 'Unknown error')}")
        sys.exit(1)

    print(f"✅ {response.get('message', 'Analysis complete')}")
    
    diagnosis_results = response.get("mixDiagnosisResults")
    if diagnosis_results:
        print_diagnosis_results(diagnosis_results)
    else:
        print("No diagnosis results in response.")


if __name__ == "__main__":
    main()

