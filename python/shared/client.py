"""
Tonn API Client

A shared client class with common utilities for interacting with the Tonn API.
This module eliminates code duplication across example scripts.
"""

import os
import time
import json
import requests
from typing import Optional, Tuple, Dict, Any

from .config import BASE_URL, get_api_key, get_headers


class TonnClient:
    """
    Client for interacting with the Tonn API.
    
    This class provides common functionality used across all examples:
    - File upload handling
    - API request utilities
    - File downloads
    - Polling for async operations
    
    Example:
        >>> client = TonnClient()
        >>> signed_url, readable_url = client.get_upload_urls("my_track.wav")
        >>> client.upload_file(signed_url, "path/to/my_track.wav")
    """
    
    # Supported audio file types
    SUPPORTED_EXTENSIONS = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac'
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Tonn API client.
        
        Args:
            api_key: Optional API key. If not provided, will be loaded from 
                     the TONN_API_KEY environment variable.
        """
        self.api_key = api_key or get_api_key()
        self.base_url = BASE_URL
        self.headers = get_headers(self.api_key)
    
    # =========================================================================
    # File Utilities
    # =========================================================================
    
    def get_content_type(self, filename: str) -> Optional[str]:
        """
        Determine the MIME type based on file extension.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            The MIME type string, or None if unsupported
            
        Supported formats:
            - .mp3 -> audio/mpeg
            - .wav -> audio/wav  
            - .flac -> audio/flac
        """
        ext = os.path.splitext(filename)[1].lower()
        return self.SUPPORTED_EXTENSIONS.get(ext)
    
    def get_upload_urls(self, filename: str, content_type: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Get signed and readable URLs for file upload.
        
        The Tonn API requires files to be uploaded to cloud storage.
        This method gets pre-signed URLs for uploading your audio file.
        
        Args:
            filename: Name of the file to upload
            content_type: Optional MIME type. If not provided, will be detected from extension.
            
        Returns:
            Tuple of (signed_url, readable_url) or (None, None) on failure
            - signed_url: Use this to upload your file via PUT request
            - readable_url: Use this URL in API requests as the audio file location
        """
        if content_type is None:
            content_type = self.get_content_type(filename)
            if content_type is None:
                print(f"Error: Unsupported file type for {filename}")
                print(f"Supported types: {', '.join(self.SUPPORTED_EXTENSIONS.keys())}")
                return None, None
        
        url = f"{self.base_url}/upload"
        params = {"key": self.api_key}
        payload = {"filename": filename, "contentType": content_type}
        headers = {"Content-Type": "application/json"}
        
        print(f"Requesting upload URLs for {filename}...")
        
        try:
            response = requests.post(url, params=params, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error"):
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return None, None
            
            signed_url = data.get("signed_url")
            readable_url = data.get("readable_url")
            
            if not signed_url or not readable_url:
                print(f"Error: Missing URLs in response: {data}")
                return None, None
            
            print("✓ Upload URLs obtained successfully")
            return signed_url, readable_url
            
        except requests.exceptions.RequestException as e:
            print(f"Error requesting upload URLs: {e}")
            return None, None
        except json.JSONDecodeError:
            print("Error: Invalid JSON response from server")
            return None, None
    
    def upload_file(self, signed_url: str, local_filepath: str, content_type: str = None) -> bool:
        """
        Upload a local file to the signed URL.
        
        Args:
            signed_url: The pre-signed URL from get_upload_urls()
            local_filepath: Path to the local file to upload
            content_type: Optional MIME type. If not provided, will be detected.
            
        Returns:
            True if upload succeeded, False otherwise
        """
        if content_type is None:
            content_type = self.get_content_type(local_filepath)
        
        print(f"Uploading {os.path.basename(local_filepath)}...")
        
        try:
            with open(local_filepath, 'rb') as f:
                response = requests.put(
                    signed_url,
                    data=f,
                    headers={'Content-Type': content_type}
                )
                response.raise_for_status()
            
            print("✓ File uploaded successfully")
            return True
            
        except FileNotFoundError:
            print(f"Error: File not found: {local_filepath}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file: {e}")
            return False
    
    def upload_local_file(self, local_filepath: str) -> Optional[str]:
        """
        Convenience method to upload a local file and get its readable URL.
        
        This combines get_upload_urls() and upload_file() into one call.
        
        Args:
            local_filepath: Path to the local audio file
            
        Returns:
            The readable URL to use in API requests, or None on failure
        """
        filename = os.path.basename(local_filepath)
        content_type = self.get_content_type(filename)
        
        if content_type is None:
            print(f"Error: Unsupported file type: {filename}")
            return None
        
        signed_url, readable_url = self.get_upload_urls(filename, content_type)
        if not signed_url:
            return None
        
        if not self.upload_file(signed_url, local_filepath, content_type):
            return None
        
        return readable_url
    
    def download_file(self, url: str, local_filename: str) -> bool:
        """
        Download a file from URL to local storage.
        
        Args:
            url: URL to download from
            local_filename: Local path to save the file
            
        Returns:
            True if download succeeded, False otherwise
        """
        print(f"Downloading to {local_filename}...")
        
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            print(f"✓ Downloaded: {local_filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return False
        except IOError as e:
            print(f"Error writing file: {e}")
            return False
    
    # =========================================================================
    # API Request Utilities
    # =========================================================================
    
    def post(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a POST request to the Tonn API.
        
        Args:
            endpoint: API endpoint (e.g., "/mixanalysis")
            payload: Request payload as dictionary
            
        Returns:
            Response data as dictionary, or None on failure
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            # Try to get JSON response even on error status
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = None
            
            # Handle HTTP errors with better messages
            if response.status_code >= 400:
                if data and 'message' in data:
                    print(f"❌ API Error: {data['message']}")
                else:
                    print(f"❌ API Error: HTTP {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def poll_for_result(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        result_key: str,
        max_attempts: int = 30,
        poll_interval: int = 5,
        processing_status_codes: tuple = (202,)
    ) -> Optional[Dict[str, Any]]:
        """
        Poll an endpoint until a result is ready.
        
        Many Tonn API operations are asynchronous. This method handles
        the polling loop for you.
        
        Args:
            endpoint: API endpoint to poll
            payload: Request payload
            result_key: Key in response that contains the result
            max_attempts: Maximum number of poll attempts
            poll_interval: Seconds between attempts
            processing_status_codes: Status codes that indicate still processing
            
        Returns:
            The result dictionary, or None if polling failed/timed out
        """
        url = f"{self.base_url}{endpoint}"
        
        print(f"Polling for results (max {max_attempts} attempts)...")
        consecutive_errors = 0
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=payload, headers=self.headers)
                
                # Try to parse JSON
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {}
                
                if response.status_code in processing_status_codes:
                    status = data.get("status", "Processing")
                    print(f"  Attempt {attempt + 1}/{max_attempts}: {status}")
                    consecutive_errors = 0
                    
                elif response.status_code == 200:
                    if not data.get("error", False):
                        result = data.get(result_key, {})
                        # Check if we have actual results (not just status)
                        status = result.get("status", "") if isinstance(result, dict) else ""
                        
                        # Check for download URLs or completed status
                        has_download = any(k.startswith("download_url") and v for k, v in result.items()) if isinstance(result, dict) else False
                        is_complete = "COMPLETED" in status.upper() if status else False
                        
                        if has_download or is_complete:
                            print("✓ Processing complete!")
                            return result
                        elif result:
                            print(f"  Attempt {attempt + 1}/{max_attempts}: {status or 'Processing'}")
                            consecutive_errors = 0
                        else:
                            print(f"  Attempt {attempt + 1}/{max_attempts}: Waiting...")
                    else:
                        # Some errors are transient, keep polling
                        error_msg = data.get('message', 'Unknown error')
                        if 'expired' in error_msg.lower():
                            consecutive_errors += 1
                            if consecutive_errors >= 3:
                                print(f"❌ API Error: {error_msg}")
                                return None
                            # Transient error, continue polling
                            print(f"  Attempt {attempt + 1}/{max_attempts}: Retrying...")
                        else:
                            print(f"❌ API Error: {error_msg}")
                            return None
                else:
                    # Non-200 status, but might be transient
                    error_msg = data.get('message', f'HTTP {response.status_code}')
                    consecutive_errors += 1
                    if consecutive_errors >= 3:
                        print(f"❌ API Error: {error_msg}")
                        return None
                    print(f"  Attempt {attempt + 1}/{max_attempts}: Retrying ({error_msg[:50]}...)")
                    
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print(f"❌ Error during polling: {e}")
                    return None
                print(f"  Attempt {attempt + 1}/{max_attempts}: Retrying...")
            
            time.sleep(poll_interval)
        
        print(f"Timed out after {max_attempts} attempts")
        return None


# Convenience function for quick client creation
def create_client(api_key: str = None) -> TonnClient:
    """
    Create a new Tonn API client.
    
    Args:
        api_key: Optional API key. If not provided, will be loaded from environment.
        
    Returns:
        A configured TonnClient instance
    """
    return TonnClient(api_key)

