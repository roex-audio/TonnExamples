#!/usr/bin/env node
/**
 * 02_mix_comparison.js - Compare Two Mixes with the Tonn API
 *
 * This example demonstrates how to compare two audio files to identify
 * differences in loudness, dynamics, stereo field, and tonal profile.
 *
 * Usage:
 *   node 02_mix_comparison.js <file_a> <file_b> <musical_style> [--is-master]
 *
 * Example:
 *   node 02_mix_comparison.js my_mix.wav reference.wav POP
 */

import { existsSync } from 'fs';
import { TonnClient } from '../shared/client.js';

// ANSI colors
const colors = {
  red: '\x1b[91m',
  green: '\x1b[92m',
  yellow: '\x1b[93m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

/**
 * Analyze a single mix.
 */
async function analyzeMix(client, audioUrl, musicalStyle, isMaster) {
  const payload = {
    mixDiagnosisData: {
      audioFileLocation: audioUrl,
      musicalStyle,
      isMaster
    }
  };

  const response = await client.post('/mixanalysis', payload);
  return response?.mixDiagnosisResults || {};
}

/**
 * Extract production metrics from diagnosis.
 */
function extractMetrics(diagnosis) {
  const payload = diagnosis.payload || {};
  const keys = [
    'bit_depth', 'clipping', 'if_master_drc', 'if_master_loudness',
    'integrated_loudness_lufs', 'mono_compatible', 'peak_loudness_dbfs',
    'phase_issues', 'sample_rate', 'stereo_field'
  ];
  const metrics = {};
  for (const key of keys) {
    metrics[key] = payload[key] ?? 'N/A';
  }
  return metrics;
}

/**
 * Compare two values and return formatted output.
 */
function compareValue(key, valA, valB) {
  const thresholds = {
    integrated_loudness_lufs: 1.0,
    peak_loudness_dbfs: 0.5,
    bit_depth: 0
  };

  // Try numeric comparison
  const numA = parseFloat(valA);
  const numB = parseFloat(valB);

  if (!isNaN(numA) && !isNaN(numB)) {
    const diff = Math.abs(numA - numB);
    const threshold = thresholds[key] || 0;

    if (threshold && diff > threshold) {
      return {
        fmtA: `${colors.red}${valA}${colors.reset}`,
        fmtB: `${colors.red}${valB}${colors.reset}`,
        interpretation: `Difference of ${diff.toFixed(2)} exceeds threshold`
      };
    } else {
      return {
        fmtA: `${colors.green}${valA}${colors.reset}`,
        fmtB: `${colors.green}${valB}${colors.reset}`,
        interpretation: diff > 0 ? 'Within acceptable range' : 'Identical'
      };
    }
  }

  // String comparison
  if (String(valA) === String(valB)) {
    return {
      fmtA: `${colors.green}${valA}${colors.reset}`,
      fmtB: `${colors.green}${valB}${colors.reset}`,
      interpretation: 'Identical'
    };
  } else {
    return {
      fmtA: `${colors.yellow}${valA}${colors.reset}`,
      fmtB: `${colors.yellow}${valB}${colors.reset}`,
      interpretation: 'Values differ'
    };
  }
}

/**
 * Print comparison of two dictionaries.
 */
function compareDicts(dictA, dictB, title) {
  console.log(`\n${colors.bold}=== ${title} ===${colors.reset}\n`);

  const allKeys = [...new Set([...Object.keys(dictA), ...Object.keys(dictB)])].sort();

  for (const key of allKeys) {
    const valA = dictA[key] ?? 'N/A';
    const valB = dictB[key] ?? 'N/A';
    const { fmtA, fmtB, interpretation } = compareValue(key, valA, valB);

    console.log(`${key}:`);
    console.log(`  File A: ${fmtA}`);
    console.log(`  File B: ${fmtB}`);
    console.log(`  → ${interpretation}\n`);
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 3 || args.includes('--help')) {
    console.log(`
Usage: node 02_mix_comparison.js <file_a> <file_b> <musical_style> [--is-master]

Arguments:
  file_a         First audio file to compare
  file_b         Second audio file to compare
  musical_style  Musical style (e.g., ROCK, POP)
  --is-master    Flag if comparing mastered tracks

Examples:
  node 02_mix_comparison.js my_mix.wav reference.wav POP
  node 02_mix_comparison.js v1.mp3 v2.mp3 ROCK --is-master
    `);
    process.exit(args.includes('--help') ? 0 : 1);
  }

  const fileA = args[0];
  const fileB = args[1];
  const musicalStyle = args[2].toUpperCase();
  const isMaster = args.includes('--is-master');

  // Validate files
  for (const filepath of [fileA, fileB]) {
    if (!existsSync(filepath)) {
      console.error(`Error: File not found: ${filepath}`);
      process.exit(1);
    }
  }

  const client = new TonnClient();
  const readableUrls = {};
  const results = {};

  // Upload both files
  for (const [label, filepath] of [['A', fileA], ['B', fileB]]) {
    console.log(`\n📤 Uploading File ${label}: ${filepath}...`);
    const url = await client.uploadLocalFile(filepath);
    if (!url) {
      console.error(`Failed to upload ${filepath}. Exiting.`);
      process.exit(1);
    }
    readableUrls[label] = url;
  }

  // Analyze both files
  console.log('\n🔍 Analyzing both files...');
  for (const [label, url] of Object.entries(readableUrls)) {
    console.log(`  Analyzing File ${label}...`);
    const diagnosis = await analyzeMix(client, url, musicalStyle, isMaster);
    if (!diagnosis || Object.keys(diagnosis).length === 0) {
      console.error(`Analysis failed for File ${label}`);
      process.exit(1);
    }
    results[label] = diagnosis;
  }

  // Compare results
  console.log('\n' + '='.repeat(60));
  console.log(`${colors.bold}MIX COMPARISON RESULTS${colors.reset}`);
  console.log('='.repeat(60));

  const metricsA = extractMetrics(results.A);
  const metricsB = extractMetrics(results.B);
  compareDicts(metricsA, metricsB, 'Production Metrics');

  const tonalA = results.A.payload?.tonal_profile || {};
  const tonalB = results.B.payload?.tonal_profile || {};
  if (Object.keys(tonalA).length || Object.keys(tonalB).length) {
    compareDicts(tonalA, tonalB, 'Tonal Profile');
  }

  console.log('='.repeat(60));
  console.log('Comparison complete!');
}

main().catch(console.error);

