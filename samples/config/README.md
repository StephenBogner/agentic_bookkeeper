# Configuration Samples

This directory contains sample configuration files for the Agentic Bookkeeper application.

## Files

### .env.sample

Sample environment configuration file with all available settings.

**How to use:**

1. Copy `.env.sample` to the project root directory:

   ```bash
   cp samples/config/.env.sample .env
   ```

2. Edit `.env` with your actual configuration:
   - Add your LLM provider API key(s)
   - Set your preferred tax jurisdiction (CRA or IRS)
   - Set your currency (CAD or USD)
   - Configure watch folder and database paths
   - Adjust logging and advanced settings as needed

3. The application will automatically load settings from `.env` on startup

**Important:** Never commit your actual `.env` file to version control. It contains
sensitive API keys and should remain private.

## Configuration Options

### LLM Providers

You only need to configure ONE provider to get started. The application supports:

- **OpenAI** (GPT-4o-mini recommended) - Fast, cost-effective
- **Anthropic** (Claude Haiku recommended) - Fast, high-quality
- **XAI** (Grok-beta) - Fast, competitive
- **Google** (Gemini Flash) - Free tier available

### Tax Jurisdictions

- **CRA** - Canada Revenue Agency (Canadian tax codes)
- **IRS** - Internal Revenue Service (US tax codes)

### Currency

- **CAD** - Canadian Dollars
- **USD** - United States Dollars

## Security Notes

- API keys are automatically encrypted when stored in the database
- The `.env` file itself is NOT encrypted - keep it secure
- Never share your `.env` file or commit it to version control
- The `.env` file is automatically ignored by git (see `.gitignore`)

## Getting API Keys

### OpenAI

1. Visit <https://platform.openai.com/api-keys>
2. Sign up or log in
3. Create a new API key
4. Copy the key to `OPENAI_API_KEY` in your `.env` file

**Cost:** ~$0.15 per 1M input tokens (approximately 500-1000 documents)

### Anthropic

1. Visit <https://console.anthropic.com/>
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to `ANTHROPIC_API_KEY` in your `.env` file

**Cost:** ~$0.25 per 1M input tokens (approximately 500-1000 documents)

### XAI

1. Visit <https://x.ai/>
2. Sign up for API access
3. Create an API key
4. Copy the key to `XAI_API_KEY` in your `.env` file

**Cost:** ~$5 per 1M input tokens (approximately 500-1000 documents)

### Google Gemini

1. Visit <https://makersuite.google.com/app/apikey>
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to `GOOGLE_API_KEY` in your `.env` file

**Cost:** Free tier available, then ~$0.075 per 1M tokens

## First-Time Setup

For complete setup instructions, see the [User Guide](../../docs/USER_GUIDE.md).

Quick start:

1. Copy `.env.sample` to `.env`
2. Add at least one LLM provider API key
3. Run the application: `python -m agentic_bookkeeper`
4. Follow the first-time setup wizard

## Troubleshooting

### "API key not found" error

- Verify your `.env` file is in the project root (not in samples/config/)
- Check that your API key is correctly copied (no extra spaces or quotes)
- Make sure the provider is spelled correctly (openai, anthropic, xai, google)

### "Permission denied" error

- Ensure the `.env` file has proper permissions
- On Linux/Mac: `chmod 600 .env` (owner read/write only)

### LLM requests failing

- Check your API key is valid and has available credits
- Verify your internet connection
- Check the LOG_FILE for detailed error messages
- Try a different LLM provider

## Support

For more help:

- See the [User Guide](../../docs/USER_GUIDE.md)
- See the [Troubleshooting section](../../docs/USER_GUIDE.md#troubleshooting)
- Check [Known Issues](../../docs/KNOWN_ISSUES.md)
- Report issues at the project repository

---

**Last Updated:** 2025-10-29
