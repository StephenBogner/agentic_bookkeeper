# Environment Variable Setup Guide

This guide explains how to configure API keys and other settings for Agentic Bookkeeper using environment variables.

## Environment Variable Precedence

Configuration values are loaded in the following order (highest to lowest priority):

1. **System environment variables** (Recommended for Production/Staging)
2. **Session environment variables** (Recommended for Testing)
3. **.env file** (Development only)

The system automatically respects this hierarchy - environment variables always take precedence over `.env` file values.

---

## Production Setup (Recommended)

### Option 1: System-wide Environment Variables

Add to `/etc/environment` (requires root):

```bash
sudo nano /etc/environment
```

Add your variables:

```bash
OPENAI_API_KEY="sk-your-actual-key-here"
ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"
LLM_PROVIDER="openai"
TAX_JURISDICTION="CRA"
```

Then reload:

```bash
source /etc/environment
```

### Option 2: User Profile Variables

Add to `~/.bashrc` or `~/.profile`:

```bash
nano ~/.bashrc
```

Add your variables:

```bash
export OPENAI_API_KEY="sk-your-actual-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"
export XAI_API_KEY="xai-your-actual-key-here"
export GOOGLE_API_KEY="AIza-your-actual-key-here"
export LLM_PROVIDER="openai"
export TAX_JURISDICTION="CRA"
```

Then reload:

```bash
source ~/.bashrc
```

### Option 3: Systemd Service (for production daemons)

Create a systemd service file with environment variables:

```ini
[Service]
Environment="OPENAI_API_KEY=sk-your-actual-key-here"
Environment="ANTHROPIC_API_KEY=sk-ant-your-actual-key-here"
Environment="LLM_PROVIDER=openai"
```

---

## Session Setup (Testing)

For temporary testing without modifying system files:

```bash
# Set for current shell session only
export OPENAI_API_KEY="sk-test-key-here"
export ANTHROPIC_API_KEY="sk-ant-test-key-here"
export LLM_PROVIDER="openai"

# Run your application
python cli.py process document.pdf
```

These variables will be lost when you close the terminal.

---

## Development Setup

### Using .env File (Development Only)

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your development keys:

   ```bash
   nano .env
   ```

3. Add your keys:

   ```bash
   OPENAI_API_KEY=sk-your-dev-key-here
   ANTHROPIC_API_KEY=sk-ant-your-dev-key-here
   LLM_PROVIDER=openai
   ```

**Important**: The `.env` file is in `.gitignore` and will never be committed to version control.

---

## Verifying Your Setup

### Check Current Environment

```bash
# Show what's currently set (masks sensitive values)
python verify_env_precedence.py
```

### Manual Check

```bash
# Check if variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# List all environment variables
env | grep API_KEY
```

### Test Precedence

```bash
# Set session variable (should override .env)
export OPENAI_API_KEY="session-key"

# Run verification
python verify_env_precedence.py
```

---

## Security Best Practices

### ✅ DO

- Use system/session environment variables in production
- Use `.env` file only for local development
- Add `.env` to `.gitignore` (already done)
- Regularly rotate API keys
- Use different keys for dev/staging/production
- Limit API key permissions to minimum required

### ❌ DON'T

- Never commit `.env` to version control
- Never hardcode API keys in source code
- Never share API keys in chat/email/Slack
- Never use production keys in development
- Never log API keys to files or console

---

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-api03-...` |
| `XAI_API_KEY` | xAI (Grok) API key | `xai-...` |
| `GOOGLE_API_KEY` | Google AI API key | `AIza...` |

### Configuration

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `LLM_PROVIDER` | Which LLM to use | `openai` | `openai`, `anthropic`, `xai`, `google` |
| `TAX_JURISDICTION` | Tax authority | `CRA` | `CRA`, `IRS` |
| `FISCAL_YEAR_START` | Fiscal year start date | `01-01` | `MM-DD` format |
| `WATCH_DIRECTORY` | Directory to monitor | `./data/watch` | Any valid path |
| `PROCESSED_DIRECTORY` | Processed files | `./data/processed` | Any valid path |
| `DATABASE_PATH` | SQLite database | `./data/bookkeeper.db` | Any valid path |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FILE` | Log file location | `./logs/agentic_bookkeeper.log` | Any valid path |

---

## Troubleshooting

### "API key not found" error

1. Check if variable is set:

   ```bash
   echo $OPENAI_API_KEY
   ```

2. If empty, set it:

   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. Verify config loading:

   ```bash
   python verify_env_precedence.py
   ```

### Variables not persisting after reboot

- System variables in `/etc/environment` persist
- User variables in `~/.bashrc` persist
- Session variables with `export` do NOT persist

### .env file not being read

This is normal if environment variables are already set. Environment variables always take precedence over `.env` file values.

---

## Quick Start Examples

### Local Development

```bash
# Quick setup for development
cp .env.example .env
nano .env  # Add your dev keys
python cli.py --help
```

### Production Deployment

```bash
# Set environment variables
export OPENAI_API_KEY="sk-prod-key-here"
export ANTHROPIC_API_KEY="sk-ant-prod-key-here"
export LLM_PROVIDER="openai"
export TAX_JURISDICTION="CRA"

# No .env file needed
python cli.py process --watch
```

### Docker Container

```dockerfile
# In your Dockerfile
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""

# Pass at runtime
docker run -e OPENAI_API_KEY="$OPENAI_API_KEY" agentic-bookkeeper
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Additional Resources

- [python-dotenv documentation](https://github.com/theskumar/python-dotenv)
- [Environment Variables in Linux](https://wiki.archlinux.org/title/Environment_variables)
- [API Key Security Best Practices](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_cryptographic_key)

---

**Last Updated**: 2025-10-27
**Maintained by**: Stephen Bogner, P.Eng.
