# Tonn API - Node.js Examples

Modern ES Module examples for integrating with the Tonn API using Node.js.

## Requirements

- **Node.js 18+** (uses native fetch)
- Tonn API key ([Get one here](https://tonn-portal.roexaudio.com))

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Set your API key
export TONN_API_KEY=your_api_key_here

# 3. Run an example
node src/examples/01_mix_analysis.js your_track.wav POP
```

## Examples

| Script | Description |
|--------|-------------|
| `01_mix_analysis.js` | Analyze a mix for technical issues |
| `02_mix_comparison.js` | Compare two mixes side-by-side |
| `03_mix_enhance.js` | Auto-enhance a stereo mix |
| `04_multitrack_mix.js` | Mix stems into a final track |
| `05_audio_cleanup.js` | Remove noise/hum/clicks |
| `06_batch_mastering.js` | Master multiple tracks for an album |

### npm Scripts

```bash
npm run example:analysis    # Mix analysis
npm run example:comparison  # Compare mixes
npm run example:enhance     # Mix enhancement
npm run example:multitrack  # Multitrack mixing
npm run example:cleanup     # Audio cleanup
npm run example:mastering   # Batch mastering
```

## Example Usage

### Mix Analysis

```bash
# Analyze a mix
node src/examples/01_mix_analysis.js track.wav POP

# Analyze a master
node src/examples/01_mix_analysis.js master.wav ROCK --is-master
```

### Mix Comparison

```bash
node src/examples/02_mix_comparison.js my_mix.wav reference.wav POP
```

### Mix Enhancement

```bash
# Use demo track
node src/examples/03_mix_enhance.js

# Or provide your own URL
node src/examples/03_mix_enhance.js https://example.com/track.mp3
```

### Multitrack Mixing

```bash
# Uses default payload
node src/examples/04_multitrack_mix.js

# Or specify custom payload
node src/examples/04_multitrack_mix.js payloads/multitrack_mix.json
```

### Audio Cleanup

```bash
node src/examples/05_audio_cleanup.js noisy_recording.wav
```

### Batch Mastering

```bash
# Uses default payload
node src/examples/06_batch_mastering.js

# Or specify custom payload
node src/examples/06_batch_mastering.js payloads/album_mastering.json
```

## Project Structure

```
nodejs/
├── package.json           # Dependencies and scripts
├── payloads/              # Example JSON payloads
│   ├── album_mastering.json
│   ├── final_mix_settings.json
│   └── multitrack_mix.json
└── src/
    ├── shared/
    │   ├── client.js      # Shared API client
    │   └── config.js      # Configuration utilities
    └── examples/
        ├── 01_mix_analysis.js
        ├── 02_mix_comparison.js
        ├── 03_mix_enhance.js
        ├── 04_multitrack_mix.js
        ├── 05_audio_cleanup.js
        └── 06_batch_mastering.js
```

## Using the Shared Client

The examples use a shared `TonnClient` class that handles common operations:

```javascript
import { TonnClient } from '../shared/client.js';

const client = new TonnClient();

// Upload a file and get its URL
const url = await client.uploadLocalFile('track.wav');

// Make an API call
const response = await client.post('/mixanalysis', payload);

// Poll for async results
const result = await client.pollForResult({
  endpoint: '/retrieveenhancedtrack',
  payload: { mixReviveData: { mixReviveTaskId: taskId } },
  resultKey: 'revivedTrackTaskResults',
  maxAttempts: 30,
  pollInterval: 5000
});

// Download a file
await client.downloadFile(url, 'output.wav');
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TONN_API_KEY` | Your Tonn API key (required) |

You can also create a `.env` file:

```bash
TONN_API_KEY=your_api_key_here
```

## Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)

## Troubleshooting

### "TONN_API_KEY environment variable not set"

Make sure you've set the environment variable:

```bash
export TONN_API_KEY=your_api_key_here
```

### "File not found" errors

- Check the file path is correct
- Make sure the file exists
- Use absolute paths if needed

### API timeout

Some operations take time. The examples poll automatically, but for very long tasks you may need to increase `maxAttempts` in the polling options.
