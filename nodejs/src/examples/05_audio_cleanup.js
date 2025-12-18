#!/usr/bin/env node
/**
 * 05_audio_cleanup.js - Clean Up Audio with the Tonn API
 *
 * This example demonstrates the Audio Clean-Up feature which removes
 * unwanted noise, hum, clicks, and other artifacts from audio.
 *
 * Usage:
 *   node 05_audio_cleanup.js <audio_file>
 *
 * Example:
 *   node 05_audio_cleanup.js noisy_recording.wav
 */

import { existsSync } from 'fs';
import { basename } from 'path';
import { TonnClient } from '../shared/client.js';

/**
 * Start an audio cleanup job.
 */
async function startCleanup(client, audioUrl, options = {}) {
  const payload = {
    audioCleanUpData: {
      audioFileLocation: audioUrl,
      noiseReduction: options.noiseReduction ?? 0.5,
      humReduction: options.humReduction ?? 0.3,
      clickReduction: options.clickReduction ?? 0.5,
      clipRepair: options.clipRepair ?? 0.5
    }
  };

  console.log('🧹 Starting audio cleanup...');
  console.log('  Settings:');
  console.log(`    - Noise reduction: ${payload.audioCleanUpData.noiseReduction}`);
  console.log(`    - Hum reduction: ${payload.audioCleanUpData.humReduction}`);
  console.log(`    - Click reduction: ${payload.audioCleanUpData.clickReduction}`);
  console.log(`    - Clip repair: ${payload.audioCleanUpData.clipRepair}`);

  const response = await client.post('/audio-cleanup', payload);

  if (response && !response.error) {
    const taskId = response.audio_clean_up_task_id;
    console.log(`✓ Cleanup task created. Task ID: ${taskId}`);
    return taskId;
  } else {
    console.error(`❌ Failed to start cleanup: ${response?.message || 'No response'}`);
    return null;
  }
}

/**
 * Poll for cleanup result.
 */
async function pollCleanupResult(client, taskId) {
  const payload = {
    audioCleanUpData: {
      audioCleanUpTaskId: taskId
    }
  };

  // For cleanup, we poll the same endpoint
  console.log('\n⏳ Processing audio...');

  for (let attempt = 0; attempt < 30; attempt++) {
    const response = await client.post('/audio-cleanup', payload);

    if (response) {
      if (response.error) {
        // Keep polling if still processing
        if (response.message?.includes('processing')) {
          console.log(`  Attempt ${attempt + 1}/30: Still processing...`);
        } else {
          console.error(`❌ Error: ${response.message}`);
          return null;
        }
      } else if (response.cleanedAudioUrl) {
        console.log('✓ Processing complete!');
        return {
          download_url: response.cleanedAudioUrl,
          status: 'completed'
        };
      }
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  console.log('Timed out waiting for results');
  return null;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 1 || args.includes('--help')) {
    console.log(`
Usage: node 05_audio_cleanup.js <audio_file> [options]

Arguments:
  audio_file  Path to audio file (.mp3, .wav, .flac)

Options (coming soon):
  --noise <0-1>  Noise reduction strength (default: 0.5)
  --hum <0-1>    Hum reduction strength (default: 0.3)
  --click <0-1>  Click reduction strength (default: 0.5)
  --clip <0-1>   Clip repair strength (default: 0.5)

Example:
  node 05_audio_cleanup.js noisy_vocal.wav
    `);
    process.exit(args.includes('--help') ? 0 : 1);
  }

  const inputFile = args[0];

  if (!existsSync(inputFile)) {
    console.error(`Error: File not found: ${inputFile}`);
    process.exit(1);
  }

  const client = new TonnClient();

  console.log('\n' + '='.repeat(60));
  console.log('AUDIO CLEANUP');
  console.log('='.repeat(60));

  // Upload the file
  console.log(`\n📤 Uploading ${inputFile}...`);
  const readableUrl = await client.uploadLocalFile(inputFile);

  if (!readableUrl) {
    console.error('Failed to upload file. Exiting.');
    process.exit(1);
  }

  // Start cleanup
  const taskId = await startCleanup(client, readableUrl);
  if (!taskId) {
    console.error('\nFailed to start cleanup. Check your API key and try again.');
    process.exit(1);
  }

  // Poll for results
  const results = await pollCleanupResult(client, taskId);

  if (!results) {
    console.error('\nCleanup timed out or failed.');
    process.exit(1);
  }

  console.log('\n📊 Cleanup Results:');
  console.log(`  Status: ${results.status}`);

  // Download cleaned file
  if (results.download_url) {
    const outputName = `cleaned_${basename(inputFile)}`;
    console.log(`\n📥 Downloading cleaned audio...`);
    await client.downloadFile(results.download_url, outputName);
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ Audio Cleanup Complete!');
  console.log('='.repeat(60));
}

main().catch(console.error);

