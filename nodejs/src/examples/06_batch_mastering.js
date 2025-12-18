#!/usr/bin/env node
/**
 * 06_batch_mastering.js - Batch Master an Album with the Tonn API
 *
 * This example demonstrates how to master multiple tracks consistently,
 * ensuring they sound cohesive as an album or EP.
 *
 * Usage:
 *   node 06_batch_mastering.js [payload_file]
 *
 * If no payload file is provided, uses the default album_mastering.json
 */

import { existsSync, mkdirSync } from 'fs';
import { readFile } from 'fs/promises';
import { resolve, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { TonnClient } from '../shared/client.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_PAYLOAD = resolve(__dirname, '../../payloads/album_mastering.json');

/**
 * Process a single track for mastering.
 */
async function masterTrack(client, trackData, index, total, outputDir) {
  const trackName = basename(trackData.audioFileLocation).replace(/\.[^.]+$/, '');
  console.log(`\n--- Track ${index + 1}/${total}: ${trackName} ---`);

  // Step 1: Start mastering preview
  console.log('📤 Starting mastering preview...');
  const previewPayload = {
    masterTrackData: {
      audioFileLocation: trackData.audioFileLocation,
      musicalStyle: trackData.musicalStyle || 'POP',
      isMaster: false,
      userSelectedMasteringPresetLevel: trackData.masteringPresetLevel || 'moderate',
      webhookURL: trackData.webhookURL || ''
    }
  };

  const previewResponse = await client.post('/masteringpreview', previewPayload);
  if (!previewResponse || previewResponse.error) {
    console.error(`❌ Failed to start preview: ${previewResponse?.message || 'No response'}`);
    return null;
  }

  const masteringTaskId = previewResponse.mastering_task_id;
  console.log(`✓ Task ID: ${masteringTaskId}`);

  // Step 2: Poll for preview result
  console.log('⏳ Waiting for preview...');
  const pollPayload = {
    masterTrackData: { masteringTaskId }
  };

  const previewResult = await client.pollForResult({
    endpoint: '/retrievepreviewmaster',
    payload: pollPayload,
    resultKey: 'masteringTaskResults',
    maxAttempts: 30,
    pollInterval: 5000
  });

  if (!previewResult) {
    console.error('❌ Preview timed out');
    return null;
  }

  // Download preview
  const previewUrl = previewResult.download_url_mastered_preview;
  if (previewUrl) {
    const previewFilename = resolve(outputDir, `${trackName}_preview.wav`);
    await client.downloadFile(previewUrl, previewFilename);
  }

  // Step 3: Approve and get final master
  console.log('📤 Approving for final master...');
  const finalPayload = {
    masterTrackData: {
      masteringTaskId,
      approved: true
    }
  };

  const finalResult = await client.pollForResult({
    endpoint: '/retrievefinalmaster',
    payload: finalPayload,
    resultKey: 'masteringTaskResults',
    maxAttempts: 30,
    pollInterval: 5000
  });

  if (!finalResult) {
    console.error('❌ Final master timed out');
    return { preview: true, final: false };
  }

  // Download final master
  const finalUrl = finalResult.download_url_mastered_track || finalResult.download_url_final;
  if (finalUrl) {
    const finalFilename = resolve(outputDir, `${trackName}_mastered.wav`);
    await client.downloadFile(finalUrl, finalFilename);
    console.log(`✅ Track ${index + 1} mastered successfully!`);
    return { preview: true, final: true };
  }

  return { preview: true, final: false };
}

async function main() {
  const payloadPath = process.argv[2] || DEFAULT_PAYLOAD;

  if (!existsSync(payloadPath)) {
    console.error(`Error: Payload file not found: ${payloadPath}`);
    console.error('\nUsage: node 06_batch_mastering.js [payload_file]');
    console.error('\nExample payloads are in the payloads/ directory.');
    process.exit(1);
  }

  console.log(`📂 Loading payload from: ${payloadPath}`);

  let albumData;
  try {
    const content = await readFile(payloadPath, 'utf-8');
    albumData = JSON.parse(content);
  } catch (error) {
    console.error(`Error reading payload file: ${error.message}`);
    process.exit(1);
  }

  const tracks = albumData.tracks || [];
  if (tracks.length === 0) {
    console.error('Error: No tracks found in payload');
    process.exit(1);
  }

  // Create output directory
  const outputDir = resolve(process.cwd(), 'mastered_output');
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }

  const client = new TonnClient();

  console.log('\n' + '='.repeat(60));
  console.log('BATCH ALBUM MASTERING');
  console.log('='.repeat(60));
  console.log(`\nTracks to master: ${tracks.length}`);
  console.log(`Output directory: ${outputDir}`);

  const results = { success: 0, failed: 0 };

  for (let i = 0; i < tracks.length; i++) {
    const result = await masterTrack(client, tracks[i], i, tracks.length, outputDir);
    if (result?.final) {
      results.success++;
    } else {
      results.failed++;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('BATCH MASTERING COMPLETE');
  console.log('='.repeat(60));
  console.log(`\n✅ Successfully mastered: ${results.success}/${tracks.length}`);
  if (results.failed > 0) {
    console.log(`❌ Failed: ${results.failed}/${tracks.length}`);
  }
  console.log(`\nOutput saved to: ${outputDir}`);
}

main().catch(console.error);

