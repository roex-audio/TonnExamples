# Tonn API Examples

Code examples for integrating with the [Tonn API](https://tonn-portal.roexaudio.com) - professional audio mixing, mastering, and analysis powered by AI.

## What Can You Build?

- **Mix Analysis**: Get detailed feedback on your mixes (loudness, dynamics, stereo, tonal balance)
- **Multitrack Mixing**: Send stems, get a professional mix with AI-suggested settings
- **Mix Enhancement**: Automatically improve stereo mixes without stems
- **Audio Cleanup**: Remove noise from vocals, drums, and other recordings
- **Batch Mastering**: Master an entire album with consistent settings

## Quick Start

Get running in 5 minutes: **[QUICKSTART.md](QUICKSTART.md)**

```bash
# 1. Clone the repo
git clone https://github.com/roex-audio/TonnExamples.git
cd TonnExamples

# 2. Install dependencies
pip install requests

# 3. Set your API key (get one at https://tonn-portal.roexaudio.com)
export TONN_API_KEY=your_api_key_here

# 4. Run an example
cd python/examples
python 01_mix_analysis.py your_track.wav POP
```

## Examples by Language

| Language | Status | Location |
|----------|--------|----------|
| Python | Ready | [python/](python/) |
| Node.js | Coming Soon | [nodejs/](nodejs/) |

## Python Examples

| Example | Description |
|---------|-------------|
| [01_mix_analysis.py](python/examples/01_mix_analysis.py) | Analyze your mix for issues |
| [02_mix_comparison.py](python/examples/02_mix_comparison.py) | Compare two mixes side-by-side |
| [03_mix_enhance.py](python/examples/03_mix_enhance.py) | Auto-enhance a stereo mix |
| [04_multitrack_mix.py](python/examples/04_multitrack_mix.py) | Mix multiple stems with audio effects |
| [05_audio_cleanup.py](python/examples/05_audio_cleanup.py) | Clean up noisy recordings |
| [06_batch_mastering.py](python/examples/06_batch_mastering.py) | Master an entire album |

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[Python README](python/README.md)** - Python-specific setup and details
- **[Audio Effects Guide](docs/AUDIO_EFFECTS_GUIDE.md)** - EQ, compression, panning reference

### Tutorials

- [Mix Analysis Tutorial](docs/tutorials/mix_analysis.md)
- [Mix Comparison Tutorial](docs/tutorials/mix_comparison.md)
- [Mix Enhance Tutorial](docs/tutorials/mix_enhance.md)
- [Multitrack Mixing Tutorial](docs/tutorials/multitrack_mixing.md)
- [Batch Mastering Tutorial](docs/tutorials/batch_mastering.md)
- [Audio Cleanup Tutorial](docs/tutorials/audio_cleanup.md)

## Repository Structure

```
TonnExamples/
├── README.md               # This file
├── QUICKSTART.md           # 5-minute getting started
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── python/                 # Python examples
│   ├── README.md           # Python-specific docs
│   ├── examples/           # Runnable scripts
│   ├── shared/             # Reusable utilities
│   └── payloads/           # Example JSON payloads
│
├── docs/                   # Documentation
│   ├── AUDIO_EFFECTS_GUIDE.md
│   └── tutorials/          # Step-by-step guides
│
└── nodejs/                 # Node.js examples (coming soon)
```

## Get an API Key

1. Go to [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
2. Create an account
3. Copy your API key
4. Set it as an environment variable: `export TONN_API_KEY=your_key`

## Support

- **API Documentation**: [tonn-portal.roexaudio.com](https://tonn-portal.roexaudio.com)
- **Email**: support@roexaudio.com
- **Issues**: [GitHub Issues](https://github.com/roex-audio/TonnExamples/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.
