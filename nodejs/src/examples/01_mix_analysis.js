#!/usr/bin/env node
/**
 * 01_mix_analysis.js - Analyze Your Mix with the Tonn API
 *
 * This example demonstrates how to analyze a mixed or mastered audio track
 * using the Tonn API's mix diagnosis feature (powered by Mix Check Studio).
 *
 * Usage:
 *   node 01_mix_analysis.js <audio_file> <musical_style> [--is-master]
 *
 * Example:
 *   node 01_mix_analysis.js my_track.wav POP --is-master
 *   node 01_mix_analysis.js demo.mp3 ROCK
 */

import { existsSync } from 'fs';
import { TonnClient } from '../shared/client.js';

/**
 * Print diagnosis results in a readable format.
 */
function printDiagnosisResults(diagnosis) {
  if (!diagnosis || typeof diagnosis !== 'object') {
    console.log('No valid diagnosis results found.');
    return;
  }

  console.log('\n' + '='.repeat(60));
  console.log('MIX DIAGNOSIS RESULTS');
  console.log('='.repeat(60));

  console.log(`\nCompletion Time: ${diagnosis.completion_time || 'N/A'}`);

  if (diagnosis.error) {
    console.log(`⚠️  Error: ${diagnosis.info || 'Unknown error'}`);
    return;
  }

  const payload = diagnosis.payload || {};
  if (Object.keys(payload).length > 0) {
    console.log('\n--- Technical Details ---');

    const metrics = [
      ['Bit Depth', payload.bit_depth],
      ['Sample Rate', payload.sample_rate],
      ['Integrated Loudness (LUFS)', payload.integrated_loudness_lufs?.toFixed(1)],
      ['Peak Loudness (dBFS)', payload.peak_loudness_dbfs],
      ['Clipping', payload.clipping],
      ['Stereo Field', payload.stereo_field],
      ['Mono Compatible', payload.mono_compatible],
      ['Phase Issues', payload.phase_issues]
    ];

    for (const [name, value] of metrics) {
      if (value !== undefined && value !== null) {
        console.log(`  ${name}: ${value}`);
      }
    }

    if (payload.if_master_drc) {
      console.log(`\n  Master DRC Evaluation: ${payload.if_master_drc}`);
    }
    if (payload.if_master_loudness) {
      console.log(`  Master Loudness Evaluation: ${payload.if_master_loudness}`);
    }
  }

  const summary = payload.summary || {};
  if (Object.keys(summary).length > 0) {
    console.log('\n--- Recommendations ---');
    let idx = 1;
    for (const value of Object.values(summary)) {
      console.log(`  ${idx}. ${value}`);
      idx++;
    }
  }

  console.log('\n' + '='.repeat(60));
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: node 01_mix_analysis.js <audio_file> <musical_style> [--is-master]

Arguments:
  audio_file     Path to audio file (.mp3, .wav, .flac)
  musical_style  Musical style (e.g., ROCK, POP, ELECTRONIC)
  --is-master    Flag if the input is a mastered track

Examples:
  node 01_mix_analysis.js track.wav POP
  node 01_mix_analysis.js master.mp3 ROCK --is-master

Musical Styles:
  ROCK, POP, ELECTRONIC, HIPHOP_GRIME, ACOUSTIC, ROCK_INDIE,
  SINGER_SONGWRITER, JAZZ, CLASSICAL, and more.
    `);
    process.exit(args.includes('--help') ? 0 : 1);
  }

  const inputFile = args[0];
  const musicalStyle = args[1].toUpperCase();
  const isMaster = args.includes('--is-master');

  // Validate input file
  if (!existsSync(inputFile)) {
    console.error(`Error: File not found: ${inputFile}`);
    process.exit(1);
  }

  const client = new TonnClient();

  // Upload the file
  console.log(`\n📤 Uploading ${inputFile}...`);
  const readableUrl = await client.uploadLocalFile(inputFile);

  if (!readableUrl) {
    console.error('Failed to upload file. Exiting.');
    process.exit(1);
  }

  // Build the analysis payload
  const payload = {
    mixDiagnosisData: {
      audioFileLocation: readableUrl,
      musicalStyle,
      isMaster
    }
  };

  // Run the analysis
  console.log(`\n🔍 Analyzing your ${isMaster ? 'master' : 'mix'}...`);
  const response = await client.post('/mixanalysis', payload);

  if (!response) {
    console.error('Analysis failed. Check your API key and try again.');
    process.exit(1);
  }

  if (response.error) {
    console.error(`❌ Error: ${response.message || 'Unknown error'}`);
    process.exit(1);
  }

  console.log(`✅ ${response.message || 'Analysis complete'}`);

  const diagnosisResults = response.mixDiagnosisResults;
  if (diagnosisResults) {
    printDiagnosisResults(diagnosisResults);
  } else {
    console.log('No diagnosis results in response.');
  }
}

main().catch(console.error);

