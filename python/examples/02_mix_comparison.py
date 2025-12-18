#!/usr/bin/env python3
"""
02_mix_comparison.py - Compare Two Mixes with the Tonn API

This example demonstrates how to compare two audio files (mixes or masters)
to identify differences in loudness, dynamics, stereo field, and tonal profile.

Use cases:
- Compare your mix to a reference track
- Compare two versions of the same mix
- A/B test different mastering approaches

Usage:
    python 02_mix_comparison.py <file_a> <file_b> <musical_style> [--is-master]

Example:
    python 02_mix_comparison.py my_mix.wav reference.wav POP
    python 02_mix_comparison.py v1.wav v2.wav ROCK --is-master
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared import TonnClient


# ANSI colors for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def analyze_mix(client: TonnClient, audio_url: str, musical_style: str, is_master: bool) -> dict:
    """Analyze a single mix and return the diagnosis results."""
    payload = {
        "mixDiagnosisData": {
            "audioFileLocation": audio_url,
            "musicalStyle": musical_style,
            "isMaster": is_master
        }
    }
    
    response = client.post("/mixanalysis", payload)
    if response and "mixDiagnosisResults" in response:
        return response["mixDiagnosisResults"]
    return {}


def extract_metrics(diagnosis: dict) -> dict:
    """Extract production metrics from diagnosis payload."""
    payload = diagnosis.get("payload", {})
    keys = [
        "bit_depth", "clipping", "if_master_drc", "if_master_loudness",
        "integrated_loudness_lufs", "mono_compatible", "peak_loudness_dbfs",
        "phase_issues", "sample_rate", "stereo_field"
    ]
    return {key: payload.get(key, "N/A") for key in keys}


def extract_tonal_profile(diagnosis: dict) -> dict:
    """Extract tonal profile from diagnosis payload."""
    return diagnosis.get("payload", {}).get("tonal_profile", {})


def compare_value(key: str, val_a, val_b) -> tuple:
    """Compare two values and return formatted strings with interpretation."""
    # Thresholds for numeric comparisons
    thresholds = {
        "integrated_loudness_lufs": 1.0,
        "peak_loudness_dbfs": 0.5,
        "bit_depth": 0
    }
    
    # Try numeric comparison
    try:
        num_a, num_b = float(val_a), float(val_b)
        diff = abs(num_a - num_b)
        threshold = thresholds.get(key, 0.0)
        
        if threshold and diff > threshold:
            fmt_a = f"{Colors.RED}{val_a}{Colors.RESET}"
            fmt_b = f"{Colors.RED}{val_b}{Colors.RESET}"
            interpretation = f"Difference of {diff:.2f} exceeds threshold"
        else:
            fmt_a = f"{Colors.GREEN}{val_a}{Colors.RESET}"
            fmt_b = f"{Colors.GREEN}{val_b}{Colors.RESET}"
            interpretation = "Within acceptable range" if diff > 0 else "Identical"
        
        return fmt_a, fmt_b, interpretation
        
    except (ValueError, TypeError):
        # Non-numeric comparison
        if str(val_a) == str(val_b):
            fmt_a = f"{Colors.GREEN}{val_a}{Colors.RESET}"
            fmt_b = f"{Colors.GREEN}{val_b}{Colors.RESET}"
            interpretation = "Identical"
        else:
            fmt_a = f"{Colors.YELLOW}{val_a}{Colors.RESET}"
            fmt_b = f"{Colors.YELLOW}{val_b}{Colors.RESET}"
            interpretation = "Values differ"
        
        return fmt_a, fmt_b, interpretation


def compare_dicts(dict_a: dict, dict_b: dict, title: str) -> None:
    """Print a side-by-side comparison of two dictionaries."""
    print(f"\n{Colors.BOLD}=== {title} ==={Colors.RESET}\n")
    
    all_keys = sorted(set(dict_a.keys()) | set(dict_b.keys()))
    
    for key in all_keys:
        val_a = dict_a.get(key, "N/A")
        val_b = dict_b.get(key, "N/A")
        fmt_a, fmt_b, interpretation = compare_value(key, val_a, val_b)
        
        print(f"{key}:")
        print(f"  File A: {fmt_a}")
        print(f"  File B: {fmt_b}")
        print(f"  → {interpretation}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare two audio mixes using the Tonn API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 02_mix_comparison.py my_mix.wav reference.wav POP
  python 02_mix_comparison.py v1.mp3 v2.mp3 ROCK --is-master
        """
    )
    parser.add_argument("file_a", help="First audio file to compare")
    parser.add_argument("file_b", help="Second audio file to compare")
    parser.add_argument("musical_style", help="Musical style (e.g., ROCK, POP)")
    parser.add_argument("--is-master", action="store_true",
                       help="Flag if comparing mastered tracks")

    args = parser.parse_args()

    # Validate files exist
    for filepath in [args.file_a, args.file_b]:
        if not os.path.isfile(filepath):
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

    client = TonnClient()
    results = {}
    readable_urls = {}

    # Upload both files
    for label, filepath in [("A", args.file_a), ("B", args.file_b)]:
        print(f"\n📤 Uploading File {label}: {os.path.basename(filepath)}...")
        url = client.upload_local_file(filepath)
        if not url:
            print(f"Failed to upload {filepath}. Exiting.")
            sys.exit(1)
        readable_urls[label] = url

    # Analyze both files
    print(f"\n🔍 Analyzing both files...")
    for label, url in readable_urls.items():
        print(f"  Analyzing File {label}...")
        diagnosis = analyze_mix(client, url, args.musical_style.upper(), args.is_master)
        if not diagnosis:
            print(f"Analysis failed for File {label}")
            sys.exit(1)
        results[label] = diagnosis

    # Compare results
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}MIX COMPARISON RESULTS{Colors.RESET}")
    print("=" * 60)

    # Production metrics comparison
    metrics_a = extract_metrics(results["A"])
    metrics_b = extract_metrics(results["B"])
    compare_dicts(metrics_a, metrics_b, "Production Metrics")

    # Tonal profile comparison
    tonal_a = extract_tonal_profile(results["A"])
    tonal_b = extract_tonal_profile(results["B"])
    if tonal_a or tonal_b:
        compare_dicts(tonal_a, tonal_b, "Tonal Profile")

    print("=" * 60)
    print("Comparison complete!")


if __name__ == "__main__":
    main()

