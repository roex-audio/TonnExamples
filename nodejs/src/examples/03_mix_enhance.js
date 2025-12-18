#!/usr/bin/env node
/**
 * 03_mix_enhance.js - Enhance Your Mix with the Tonn API
 *
 * This example demonstrates the Mix Enhance feature which automatically
 * improves your stereo mix without needing individual stems.
 *
 * Usage:
 *   node 03_mix_enhance.js [audio_url]
 *
 * If no URL provided, uses a demo track from the test bucket.
 */

import { TonnClient } from '../shared/client.js';

/**
 * Start a Mix Enhance preview job.
 */
async function startEnhancePreview(client, audioUrl, musicalStyle = 'POP') {
  const payload = {
    mixReviveData: {
      audioFileLocation: audioUrl,
      musicalStyle,
      isMaster: false,
      fixClippingIssues: true,
      fixStereoWidthIssues: true,
      fixTonalProfileIssues: true,
      fixLoudnessIssues: true,
      applyMastering: true,
      stemProcessing: false
    }
  };

  console.log('🎚️  Starting Mix Enhance preview...');
  const response = await client.post('/mixenhancepreview', payload);

  if (response && !response.error) {
    const taskId = response.mixrevive_task_id;
    console.log(`✓ Preview task created. Task ID: ${taskId}`);
    return taskId;
  } else {
    const errorMsg = response?.message || 'No response';
    console.error(`❌ Failed to start preview: ${errorMsg}`);
    return null;
  }
}

/**
 * Start a full Mix Enhance job.
 */
async function startFullEnhance(client, audioUrl, musicalStyle = 'POP') {
  const payload = {
    mixReviveData: {
      audioFileLocation: audioUrl,
      musicalStyle,
      isMaster: false,
      fixClippingIssues: true,
      fixStereoWidthIssues: true,
      fixTonalProfileIssues: true,
      fixLoudnessIssues: true,
      applyMastering: true,
      stemProcessing: false
    }
  };

  console.log('🎚️  Starting full Mix Enhance...');
  const response = await client.post('/mixenhance', payload);

  if (response && !response.error) {
    const taskId = response.mixrevive_task_id;
    console.log(`✓ Full enhance task created. Task ID: ${taskId}`);
    return taskId;
  } else {
    const errorMsg = response?.message || 'No response';
    console.error(`❌ Failed to start enhancement: ${errorMsg}`);
    return null;
  }
}

/**
 * Poll for enhanced track result.
 */
async function pollEnhancedTrack(client, taskId, maxAttempts = 70) {
  const payload = {
    mixReviveData: {
      mixReviveTaskId: taskId
    }
  };

  return client.pollForResult({
    endpoint: '/retrieveenhancedtrack',
    payload,
    resultKey: 'revivedTrackTaskResults',
    maxAttempts,
    pollInterval: 5000
  });
}

/**
 * Download results.
 */
async function downloadResults(client, results, prefix) {
  const previewUrl = results.download_url_preview_revived;
  const fullUrl = results.download_url_revived;
  const downloadUrl = fullUrl || previewUrl;

  if (downloadUrl) {
    const filename = `${prefix}_enhanced.wav`;
    await client.downloadFile(downloadUrl, filename);
  }

  // Download stems if any
  const stems = results.stems || {};
  for (const [stemName, stemUrl] of Object.entries(stems)) {
    const filename = `${prefix}_stem_${stemName}.wav`;
    await client.downloadFile(stemUrl, filename);
  }
}

async function main() {
  const demoUrl = 'https://storage.googleapis.com/test-bucket-api-roex/album/audio_track_1.mp3';
  const audioUrl = process.argv[2] || demoUrl;

  if (process.argv[2]) {
    console.log(`Using provided URL: ${audioUrl}`);
  } else {
    console.log(`Using demo track: ${audioUrl}`);
  }

  const client = new TonnClient();

  console.log('\n' + '='.repeat(60));
  console.log('STEP 1: Create Preview Enhancement');
  console.log('='.repeat(60));

  // Start preview
  const previewTaskId = await startEnhancePreview(client, audioUrl, 'HIPHOP_GRIME');
  if (!previewTaskId) {
    console.error('Failed to create preview. Exiting.');
    process.exit(1);
  }

  // Poll for preview results
  console.log('\n⏳ Waiting for preview to complete...');
  const previewResults = await pollEnhancedTrack(client, previewTaskId);

  if (!previewResults) {
    console.error('Preview timed out or failed.');
    process.exit(1);
  }

  console.log('\n📊 Preview Results:');
  console.log(`  Status: ${previewResults.status || 'Unknown'}`);

  // Download preview
  await downloadResults(client, previewResults, 'preview');

  console.log('\n' + '='.repeat(60));
  console.log('STEP 2: Create Full Enhancement');
  console.log('='.repeat(60));

  // Start full enhancement
  const fullTaskId = await startFullEnhance(client, audioUrl, 'HIPHOP_GRIME');
  if (!fullTaskId) {
    console.error('Failed to start full enhancement. Exiting.');
    process.exit(1);
  }

  // Poll for full results
  console.log('\n⏳ Waiting for full enhancement to complete...');
  const fullResults = await pollEnhancedTrack(client, fullTaskId, 50);

  if (!fullResults) {
    console.error('Full enhancement timed out or failed.');
    process.exit(1);
  }

  console.log('\n📊 Full Enhancement Results:');
  console.log(`  Status: ${fullResults.status || 'Unknown'}`);

  // Download full results
  await downloadResults(client, fullResults, 'enhanced');

  console.log('\n' + '='.repeat(60));
  console.log('✅ Mix Enhance Complete!');
  console.log('='.repeat(60));
  console.log('\nYour enhanced files have been saved to the current directory.');
}

main().catch(console.error);

