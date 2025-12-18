# Tonn API Examples

Code examples for integrating with the [Tonn API](https://tonn-portal.roexaudio.com) — professional audio mixing, mastering, and analysis powered by AI.

**Perfect for:** Junior developers, indie musicians, and anyone building audio apps.

## What Can You Build?

| Feature | What It Does | Use Case |
|---------|--------------|----------|
| **Mix Analysis** | Get feedback on loudness, dynamics, stereo, tonal balance | Check if your mix is ready for release |
| **Mix Enhancement** | Auto-improve stereo mixes without stems | Polish rough mixes quickly |
| **Multitrack Mixing** | Send stems, get a professional mix | Let AI balance your tracks |
| **Audio Cleanup** | Remove noise, hum, clicks from recordings | Clean up vocals or live recordings |
| **Batch Mastering** | Master an album with consistent settings | Release-ready EP/album mastering |

## Quick Start

### Python

```bash
git clone https://github.com/roex-audio/TonnExamples.git
cd TonnExamples

pip install -r requirements.txt

export TONN_API_KEY=your_api_key_here   # Or create a .env file

cd python/examples
python 01_mix_analysis.py your_track.wav POP
```

### Node.js

```bash
git clone https://github.com/roex-audio/TonnExamples.git
cd TonnExamples/nodejs

npm install

export TONN_API_KEY=your_api_key_here   # Or create a .env file

node src/examples/01_mix_analysis.js your_track.wav POP
```

**Get your API key:** [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)

**Need detailed setup?** See [QUICKSTART.md](QUICKSTART.md)

## Examples

Both Python and Node.js have identical examples:

| # | Example | Description | Typical Runtime |
|---|---------|-------------|-----------------|
| 01 | Mix Analysis | Analyze your mix for issues | ~30 seconds |
| 02 | Mix Comparison | Compare two mixes side-by-side | ~1 minute |
| 03 | Mix Enhance | Auto-enhance a stereo mix | ~3 minutes |
| 04 | Multitrack Mix | Mix stems with AI settings | ~2 minutes |
| 05 | Audio Cleanup | Remove noise/hum/clicks | ~1 minute |
| 06 | Batch Mastering | Master an entire album | ~2 min/track |

### Python Examples → [python/examples/](python/examples/)

```bash
cd python/examples
python 01_mix_analysis.py track.wav POP
python 03_mix_enhance.py                    # Uses demo track
python 06_batch_mastering.py ./my_album
```

### Node.js Examples → [nodejs/src/examples/](nodejs/src/examples/)

```bash
cd nodejs
node src/examples/01_mix_analysis.js track.wav POP
node src/examples/03_mix_enhance.js         # Uses demo track
node src/examples/06_batch_mastering.js
```

## Using Your API Key

**Option 1: Environment variable**
```bash
export TONN_API_KEY=your_api_key_here
```

**Option 2: Create a \`.env\` file** (recommended)
```bash
echo "TONN_API_KEY=your_api_key_here" > .env
```

Both Python and Node.js will automatically load the \`.env\` file.

## Documentation

| Doc | Description |
|-----|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 minutes |
| [Python README](python/README.md) | Python setup and usage |
| [Node.js README](nodejs/README.md) | Node.js setup and usage |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [Audio Effects Guide](docs/AUDIO_EFFECTS_GUIDE.md) | EQ, compression, panning reference |

### Tutorials

- [Mix Analysis](docs/tutorials/mix_analysis.md) — Check your mix against industry standards
- [Mix Comparison](docs/tutorials/mix_comparison.md) — A/B compare two versions
- [Mix Enhance](docs/tutorials/mix_enhance.md) — Auto-improve your mix
- [Multitrack Mixing](docs/tutorials/multitrack_mixing.md) — AI-assisted stem mixing
- [Batch Mastering](docs/tutorials/batch_mastering.md) — Master your album
- [Audio Cleanup](docs/tutorials/audio_cleanup.md) — Remove unwanted noise

## Repository Structure

```
TonnExamples/
├── README.md                 # You are here
├── QUICKSTART.md             # 5-minute setup guide
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── .env.example              # API key template
│
├── python/
│   ├── README.md             # Python docs
│   ├── examples/             # 6 runnable scripts
│   ├── shared/               # TonnClient utility class
│   └── payloads/             # Example JSON configs
│
├── nodejs/
│   ├── README.md             # Node.js docs
│   ├── package.json          # Dependencies
│   ├── src/examples/         # 6 runnable scripts
│   ├── src/shared/           # TonnClient utility class
│   └── payloads/             # Example JSON configs
│
└── docs/
    ├── TROUBLESHOOTING.md    # Common issues
    ├── AUDIO_EFFECTS_GUIDE.md
    └── tutorials/            # Step-by-step guides
```

## Support

- **Having issues?** → [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- **API docs** → [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- **Email** → support@roexaudio.com
- **Bugs** → [GitHub Issues](https://github.com/roex-audio/TonnExamples/issues)

## License

MIT License — see [LICENSE](LICENSE) for details.
