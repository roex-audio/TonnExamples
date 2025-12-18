/**
 * Configuration module for Tonn API examples.
 * Handles API key loading and base URL configuration.
 */

import { config } from 'dotenv';

// Load .env file if present
config();

/** Base URL for the Tonn API */
export const BASE_URL = 'https://tonn.roexaudio.com';

/**
 * Get the Tonn API key from environment variables.
 * @returns {string} The API key
 * @throws {Error} If the API key is not set
 */
export function getApiKey() {
  const apiKey = process.env.TONN_API_KEY;

  if (!apiKey) {
    console.error('='.repeat(60));
    console.error('ERROR: TONN_API_KEY environment variable not set');
    console.error('='.repeat(60));
    console.error();
    console.error('To fix this:');
    console.error('  1. Get an API key from: https://tonn-portal.roexaudio.com');
    console.error('  2. Set the environment variable:');
    console.error();
    console.error('     On macOS/Linux:');
    console.error('       export TONN_API_KEY=your_api_key_here');
    console.error();
    console.error('     On Windows (Command Prompt):');
    console.error('       set TONN_API_KEY=your_api_key_here');
    console.error();
    console.error('     On Windows (PowerShell):');
    console.error('       $env:TONN_API_KEY="your_api_key_here"');
    console.error();
    console.error('  3. Or create a .env file with:');
    console.error('       TONN_API_KEY=your_api_key_here');
    console.error();
    process.exit(1);
  }

  return apiKey;
}

/**
 * Get standard headers for Tonn API requests.
 * @param {string} [apiKey] - Optional API key. If not provided, will be loaded from environment.
 * @returns {Object} Headers object for API requests
 */
export function getHeaders(apiKey = null) {
  const key = apiKey || getApiKey();
  return {
    'Content-Type': 'application/json',
    'x-api-key': key
  };
}

