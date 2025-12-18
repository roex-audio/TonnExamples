# Troubleshooting Guide

Common issues and how to fix them.

## API Key Issues

### "TONN_API_KEY environment variable not set"

**Cause:** The API key hasn't been set in your environment.

**Fix:**

```bash
# Option 1: Set in terminal (temporary, current session only)
export TONN_API_KEY=your_api_key_here

# Option 2: Create a .env file (persistent, recommended)
echo "TONN_API_KEY=your_api_key_here" > .env
```

Then re-run your script.

### "API key expired" or "Unauthorized"

**Cause:** Your API key is no longer valid.

**Fix:**
1. Go to [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
2. Log in and generate a new API key
3. Update your environment variable or `.env` file

### "Invalid API key format"

**Cause:** The API key may have extra spaces or quotes.

**Fix:** Ensure no extra characters:

```bash
# Wrong (has quotes in value)
export TONN_API_KEY="your_key"

# Correct
export TONN_API_KEY=your_key
```

---

## File Issues

### "File not found"

**Cause:** The script can't locate your audio file.

**Fix:**
- Use absolute paths: `/Users/you/Music/track.wav`
- Or ensure you're in the correct directory
- Check the filename spelling (case-sensitive on Linux/Mac)

### "Unsupported file type"

**Cause:** Only `.mp3`, `.wav`, and `.flac` files are supported.

**Fix:** Convert your file to a supported format:

```bash
# Using ffmpeg
ffmpeg -i input.m4a -acodec pcm_s16le output.wav
```

### "Upload failed"

**Cause:** File too large, network issue, or storage quota exceeded.

**Fix:**
- Check your internet connection
- Try a smaller file first
- Contact support if the issue persists

---

## Processing Issues

### "Timed out waiting for results"

**Cause:** The processing took longer than expected.

**Possible reasons:**
- Large file size
- Complex audio content
- Server load

**Fix:**
- For Python: Increase `max_attempts` in `poll_for_result()` calls
- For Node.js: Increase `maxAttempts` in polling options
- Wait a few minutes and try again

### "Processing failed"

**Cause:** The API encountered an error processing your file.

**Fix:**
- Check your audio file isn't corrupted
- Ensure the file has actual audio content (not silence)
- Try a different file to isolate the issue

### "Status stuck on PENDING"

**Cause:** The job is queued but hasn't started processing.

**Fix:**
- Wait a few more minutes (high traffic periods)
- Check [status.roexaudio.com](https://status.roexaudio.com) for outages
- Contact support if stuck for more than 10 minutes

---

## Installation Issues

### Python: "ModuleNotFoundError: No module named 'requests'"

**Fix:**

```bash
pip install requests
# Or with python-dotenv support
pip install -r requirements.txt
```

### Python: "ModuleNotFoundError: No module named 'shared'"

**Cause:** Running from wrong directory or Python path issue.

**Fix:**

```bash
# Make sure you're in the examples directory
cd python/examples
python 01_mix_analysis.py ...
```

### Node.js: "Cannot find module"

**Fix:**

```bash
cd nodejs
npm install
```

### Node.js: "fetch is not defined"

**Cause:** Node.js version too old (needs 18+).

**Fix:** Update Node.js to version 18 or later:

```bash
# Using nvm
nvm install 18
nvm use 18
```

---

## Network Issues

### "Connection refused" or "ECONNREFUSED"

**Cause:** Can't reach the API server.

**Fix:**
- Check your internet connection
- Ensure no firewall/VPN is blocking `tonn.roexaudio.com`
- Try: `curl https://tonn.roexaudio.com` to test connectivity

### "SSL/TLS error"

**Cause:** Certificate verification issue.

**Fix:**
- Update your system's CA certificates
- If on corporate network, check proxy settings

---

## Download Issues

### "Downloaded file is empty or corrupted"

**Cause:** Download interrupted or URL expired.

**Fix:**
- Re-run the script to get a fresh download URL
- Check you have write permissions in the output directory
- Ensure enough disk space

### "Permission denied" when saving file

**Fix:**

```bash
# Check current directory is writable
ls -la .

# Or specify a different output directory
mkdir -p ~/Downloads/tonn_output
cd ~/Downloads/tonn_output
```

---

## Getting More Help

### Enable Verbose Output

The shared client prints progress by default. For more details, you can modify the scripts to print full API responses.

### Check API Response

If something fails, the scripts show error messages from the API. Look for:
- `❌ API Error: [message]` - This shows what the API returned

### Contact Support

If you've tried the above and still have issues:

1. **Email:** support@roexaudio.com
2. **Include:**
   - The exact error message
   - Which script you ran
   - Your audio file format and size
   - Python/Node.js version

### API Status

Check for service outages: [status.roexaudio.com](https://status.roexaudio.com)

