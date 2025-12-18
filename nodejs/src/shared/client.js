/**
 * Tonn API Client
 * 
 * A shared client class with common utilities for interacting with the Tonn API.
 * This module eliminates code duplication across example scripts.
 */

import { createWriteStream } from 'fs';
import { readFile, stat } from 'fs/promises';
import { basename, extname } from 'path';
import { pipeline } from 'stream/promises';
import { BASE_URL, getApiKey, getHeaders } from './config.js';

/** Supported audio file types */
const SUPPORTED_EXTENSIONS = {
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.flac': 'audio/flac'
};

/**
 * Client for interacting with the Tonn API.
 */
export class TonnClient {
  /**
   * Create a new Tonn API client.
   * @param {string} [apiKey] - Optional API key. If not provided, will be loaded from environment.
   */
  constructor(apiKey = null) {
    this.apiKey = apiKey || getApiKey();
    this.baseUrl = BASE_URL;
    this.headers = getHeaders(this.apiKey);
  }

  // =========================================================================
  // File Utilities
  // =========================================================================

  /**
   * Determine the MIME type based on file extension.
   * @param {string} filename - Name of the audio file
   * @returns {string|null} The MIME type string, or null if unsupported
   */
  getContentType(filename) {
    const ext = extname(filename).toLowerCase();
    return SUPPORTED_EXTENSIONS[ext] || null;
  }

  /**
   * Get signed and readable URLs for file upload.
   * @param {string} filename - Name of the file to upload
   * @param {string} [contentType] - Optional MIME type
   * @returns {Promise<{signedUrl: string, readableUrl: string}|null>}
   */
  async getUploadUrls(filename, contentType = null) {
    const type = contentType || this.getContentType(filename);
    if (!type) {
      console.error(`Error: Unsupported file type for ${filename}`);
      console.error(`Supported types: ${Object.keys(SUPPORTED_EXTENSIONS).join(', ')}`);
      return null;
    }

    const url = `${this.baseUrl}/upload?key=${this.apiKey}`;
    const payload = { filename, contentType: type };

    console.log(`Requesting upload URLs for ${filename}...`);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (data.error) {
        console.error(`API Error: ${data.message || 'Unknown error'}`);
        return null;
      }

      const { signed_url: signedUrl, readable_url: readableUrl } = data;

      if (!signedUrl || !readableUrl) {
        console.error('Error: Missing URLs in response');
        return null;
      }

      console.log('✓ Upload URLs obtained successfully');
      return { signedUrl, readableUrl };
    } catch (error) {
      console.error(`Error requesting upload URLs: ${error.message}`);
      return null;
    }
  }

  /**
   * Upload a local file to the signed URL.
   * @param {string} signedUrl - The pre-signed URL
   * @param {string} localFilepath - Path to the local file
   * @param {string} [contentType] - Optional MIME type
   * @returns {Promise<boolean>}
   */
  async uploadFile(signedUrl, localFilepath, contentType = null) {
    const type = contentType || this.getContentType(localFilepath);
    const filename = basename(localFilepath);

    console.log(`Uploading ${filename}...`);

    try {
      const fileBuffer = await readFile(localFilepath);

      const response = await fetch(signedUrl, {
        method: 'PUT',
        headers: { 'Content-Type': type },
        body: fileBuffer
      });

      if (!response.ok) {
        console.error(`Upload failed: ${response.status} ${response.statusText}`);
        return false;
      }

      console.log('✓ File uploaded successfully');
      return true;
    } catch (error) {
      console.error(`Error uploading file: ${error.message}`);
      return false;
    }
  }

  /**
   * Convenience method to upload a local file and get its readable URL.
   * @param {string} localFilepath - Path to the local audio file
   * @returns {Promise<string|null>} The readable URL, or null on failure
   */
  async uploadLocalFile(localFilepath) {
    const filename = basename(localFilepath);
    const contentType = this.getContentType(filename);

    if (!contentType) {
      console.error(`Error: Unsupported file type: ${filename}`);
      return null;
    }

    // Check file exists
    try {
      await stat(localFilepath);
    } catch {
      console.error(`Error: File not found: ${localFilepath}`);
      return null;
    }

    const urls = await this.getUploadUrls(filename, contentType);
    if (!urls) return null;

    const success = await this.uploadFile(urls.signedUrl, localFilepath, contentType);
    if (!success) return null;

    return urls.readableUrl;
  }

  /**
   * Download a file from URL to local storage.
   * @param {string} url - URL to download from
   * @param {string} localFilename - Local path to save the file
   * @returns {Promise<boolean>}
   */
  async downloadFile(url, localFilename) {
    console.log(`Downloading to ${localFilename}...`);

    try {
      const response = await fetch(url);

      if (!response.ok) {
        console.error(`Download failed: ${response.status}`);
        return false;
      }

      const fileStream = createWriteStream(localFilename);
      await pipeline(response.body, fileStream);

      console.log(`✓ Downloaded: ${localFilename}`);
      return true;
    } catch (error) {
      console.error(`Error downloading file: ${error.message}`);
      return false;
    }
  }

  // =========================================================================
  // API Request Utilities
  // =========================================================================

  /**
   * Send a POST request to the Tonn API.
   * @param {string} endpoint - API endpoint (e.g., "/mixanalysis")
   * @param {Object} payload - Request payload
   * @returns {Promise<Object|null>} Response data, or null on failure
   */
  async post(endpoint, payload) {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(payload)
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (response.status >= 400) {
        const message = data?.message || `HTTP ${response.status}`;
        console.error(`❌ API Error: ${message}`);
        return null;
      }

      return data;
    } catch (error) {
      console.error(`❌ Request failed: ${error.message}`);
      return null;
    }
  }

  /**
   * Poll an endpoint until a result is ready.
   * @param {Object} options - Polling options
   * @param {string} options.endpoint - API endpoint to poll
   * @param {Object} options.payload - Request payload
   * @param {string} options.resultKey - Key in response that contains the result
   * @param {number} [options.maxAttempts=30] - Maximum poll attempts
   * @param {number} [options.pollInterval=5000] - Milliseconds between attempts
   * @returns {Promise<Object|null>} The result, or null on failure/timeout
   */
  async pollForResult({
    endpoint,
    payload,
    resultKey,
    maxAttempts = 30,
    pollInterval = 5000
  }) {
    console.log(`Polling for results (max ${maxAttempts} attempts)...`);
    let consecutiveErrors = 0;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify(payload)
        });

        let data;
        try {
          data = await response.json();
        } catch {
          data = {};
        }

        if (response.status === 200) {
          if (!data.error) {
            const result = data[resultKey] || {};
            const status = result.status || '';

            // Check for download URLs or completed status
            const hasDownload = Object.entries(result).some(
              ([k, v]) => k.startsWith('download_url') && v
            );
            const isComplete = status.toUpperCase().includes('COMPLETED');

            if (hasDownload || isComplete) {
              console.log('✓ Processing complete!');
              return result;
            } else if (Object.keys(result).length > 0) {
              console.log(`  Attempt ${attempt + 1}/${maxAttempts}: ${status || 'Processing'}`);
              consecutiveErrors = 0;
            } else {
              console.log(`  Attempt ${attempt + 1}/${maxAttempts}: Waiting...`);
            }
          } else {
            const errorMsg = data.message || 'Unknown error';
            if (errorMsg.toLowerCase().includes('expired')) {
              consecutiveErrors++;
              if (consecutiveErrors >= 3) {
                console.error(`❌ API Error: ${errorMsg}`);
                return null;
              }
              console.log(`  Attempt ${attempt + 1}/${maxAttempts}: Retrying...`);
            } else {
              console.error(`❌ API Error: ${errorMsg}`);
              return null;
            }
          }
        } else if (response.status === 202) {
          const status = data.status || 'Processing';
          console.log(`  Attempt ${attempt + 1}/${maxAttempts}: ${status}`);
          consecutiveErrors = 0;
        } else {
          consecutiveErrors++;
          if (consecutiveErrors >= 3) {
            console.error(`❌ API Error: HTTP ${response.status}`);
            return null;
          }
          console.log(`  Attempt ${attempt + 1}/${maxAttempts}: Retrying...`);
        }
      } catch (error) {
        consecutiveErrors++;
        if (consecutiveErrors >= 3) {
          console.error(`❌ Error during polling: ${error.message}`);
          return null;
        }
        console.log(`  Attempt ${attempt + 1}/${maxAttempts}: Retrying...`);
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    console.log(`Timed out after ${maxAttempts} attempts`);
    return null;
  }
}

/**
 * Create a new Tonn API client.
 * @param {string} [apiKey] - Optional API key
 * @returns {TonnClient}
 */
export function createClient(apiKey = null) {
  return new TonnClient(apiKey);
}

export default TonnClient;

