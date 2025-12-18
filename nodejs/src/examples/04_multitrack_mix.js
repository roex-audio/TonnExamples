#!/usr/bin/env node
/**
 * 04_multitrack_mix.js - Mix from Stems with the Tonn API
 *
 * This example demonstrates the Multitrack Mix feature which takes individual
 * stems (vocals, drums, bass, etc.) and creates a professional mix.
 *
 * Usage:
 *   node 04_multitrack_mix.js [payload_file]
 *
 * If no payload file is provided, uses the default multitrack_mix.json
 */

import { existsSync } from 'fs';
import { readFile } from 'fs/promises';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { TonnClient } from '../shared/client.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_PAYLOAD = resolve(__dirname, '../../payloads/multitrack_mix.json');

/**
 * Start a multitrack mix preview job.
 */
async function startMixPreview(client, mixData) {
  console.log('🎚️  Starting multitrack mix preview...');
  const response = await client.post('/mixpreview', mixData);

  if (response && !response.error) {
    const taskId = response.multitrack_task_id;
    console.log(`✓ Mix task created. Task ID: ${taskId}`);
    return taskId;
  } else {
    console.error(`❌ Failed to start mix: ${response?.message || 'No response'}`);
    return null;
  }
}

/**
 * Poll for mix preview result.
 */
async function pollMixPreview(client, taskId) {
  const payload = {
    multitrackData: {
      multitrackTaskId: taskId,
      retrieveFXSettings: true
    }
  };

  return client.pollForResult({
    endpoint: '/retrievepreviewmix',
    payload,
    resultKey: 'previewMixTaskResults',
    maxAttempts: 40,
    pollInterval: 5000
  });
}

async function main() {
  const payloadPath = process.argv[2] || DEFAULT_PAYLOAD;

  if (!existsSync(payloadPath)) {
    console.error(`Error: Payload file not found: ${payloadPath}`);
    console.error('\nUsage: node 04_multitrack_mix.js [payload_file]');
    console.error('\nExample payloads are in the payloads/ directory.');
    process.exit(1);
  }

  console.log(`📂 Loading payload from: ${payloadPath}`);

  let mixData;
  try {
    const content = await readFile(payloadPath, 'utf-8');
    mixData = JSON.parse(content);
  } catch (error) {
    console.error(`Error reading payload file: ${error.message}`);
    process.exit(1);
  }

  const client = new TonnClient();

  console.log('\n' + '='.repeat(60));
  console.log('MULTITRACK MIX');
  console.log('='.repeat(60));

  // Summary of the job
  const trackData = mixData.multitrackData?.trackData || [];
  console.log(`\nStems: ${trackData.length} tracks`);
  for (const track of trackData) {
    const filename = track.trackURL?.split('/').pop() || 'No file';
    console.log(`  - ${track.instrumentGroup || 'Unknown'}: ${filename}`);
  }

  // Start the mix preview
  const taskId = await startMixPreview(client, mixData);
  if (!taskId) {
    console.error('\nFailed to start mix. Check your payload and try again.');
    process.exit(1);
  }

  // Poll for results
  console.log('\n⏳ Processing stems...');

  const results = await pollMixPreview(client, taskId);

  if (!results) {
    console.error('\nMix timed out or failed.');
    process.exit(1);
  }

  console.log('\n📊 Mix Results:');
  console.log(`  Status: ${results.status || 'Unknown'}`);

  // Download the final mix
  const downloadUrl = results.download_url_preview_mixed || results.download_url_final_mix;
  if (downloadUrl) {
    const filename = 'multitrack_mix_output.mp3';
    console.log('\n📥 Downloading mix...');
    await client.downloadFile(downloadUrl, filename);
  } else {
    console.log('\n⚠️  No download URL in response');
    console.log('Results:', JSON.stringify(results, null, 2));
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ Multitrack Mix Complete!');
  console.log('='.repeat(60));
}

main().catch(console.error);

