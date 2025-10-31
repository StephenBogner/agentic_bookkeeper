# Bug: API Key Validation Using Incorrect Config Access Method

## Bug Description

When a user clicks "Start Monitoring" in the Dashboard with a valid API key set as an environment variable (e.g., `XAI_API_KEY`), the application incorrectly reports "API key not configured for xai" and prevents monitoring from starting.

**Symptoms:**
- User has `XAI_API_KEY` environment variable set
- Application loads the API key on startup (confirmed by Config class)
- User clicks "Start Monitoring" button
- Dashboard shows warning: "Cannot start monitoring: API key not configured for xai"
- Monitoring fails to start despite valid configuration

**Expected Behavior:**
- Dashboard should recognize the API key from environment variable
- Validation should pass
- DocumentMonitor should initialize successfully
- Monitoring should start

**Actual Behavior:**
- Dashboard fails to detect the API key
- Validation fails with false negative
- User cannot start monitoring despite correct configuration

## Problem Statement

The `_validate_monitoring_configuration()` method in `dashboard_widget.py` attempts to access API keys using the wrong method. It uses `self.config.get(f"{llm_provider}_api_key")` which tries to access a top-level configuration key, but API keys are stored in a nested dictionary structure `self._config["api_keys"][provider]` and should be accessed via the `get_api_key(provider)` method.

Similarly, `_initialize_document_monitor()` has the same bug when attempting to retrieve the API key for initialization.

## Solution Statement

Replace incorrect API key access in two methods:

1. **In `_validate_monitoring_configuration()`:** Change line 548 from:
   ```python
   api_key = self.config.get(api_key_field)
   ```
   to:
   ```python
   api_key = self.config.get_api_key(llm_provider)
   ```

2. **In `_initialize_document_monitor()`:** Change line 589 from:
   ```python
   api_key = self.config.get(f"{llm_provider_name}_api_key")
   ```
   to:
   ```python
   api_key = self.config.get_api_key(llm_provider_name)
   ```

This ensures API keys are retrieved using the correct Config API that properly accesses the nested `api_keys` dictionary and loads from environment variables.

## Steps to Reproduce

1. Set API key as environment variable:
   ```bash
   export XAI_API_KEY="your-api-key-here"
   ```

2. Start the application:
   ```bash
   ./run_bookkeeper.sh
   ```

3. Configure LLM provider in Settings:
   - Go to File → Settings
   - Set LLM Provider to "xai"
   - Note: Do NOT enter API key in settings (rely on environment variable)
   - Set watch and processed directories
   - Save settings

4. Click "Start Monitoring" button on Dashboard

5. Observe error:
   ```
   2025-10-30 13:38:44 - agentic_bookkeeper.gui.dashboard_widget - INFO - DocumentMonitor not initialized - attempting on-demand initialization
   2025-10-30 13:38:44 - agentic_bookkeeper.gui.dashboard_widget - WARNING - Cannot start monitoring: API key not configured for xai
   ```

## Root Cause Analysis

**Root Cause:** Incorrect API key retrieval method in dashboard_widget.py

**How Config Stores API Keys:**

In `src/agentic_bookkeeper/utils/config.py:94-99`:
```python
self._config["api_keys"] = {
    "openai": os.getenv("OPENAI_API_KEY", ""),
    "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
    "xai": os.getenv("XAI_API_KEY", ""),
    "google": os.getenv("GOOGLE_API_KEY", ""),
}
```

API keys are stored in a nested dictionary under the `"api_keys"` key.

**Correct Access Method:**

`config.py:209-219` provides the proper API:
```python
def get_api_key(self, provider: str) -> str:
    """Get API key for a provider."""
    return self._config["api_keys"].get(provider, "")
```

**Incorrect Access in Bug:**

`dashboard_widget.py:547-548`:
```python
api_key_field = f"{llm_provider}_api_key"  # Creates "xai_api_key"
api_key = self.config.get(api_key_field)   # Tries to get top-level key "xai_api_key"
```

The `get()` method returns `self._config.get(key, default)` which looks for top-level keys. The key `"xai_api_key"` doesn't exist at the top level - it should access `self._config["api_keys"]["xai"]` instead.

**Why Environment Variables Don't Work:**

When Config initializes (config.py:96), it loads `XAI_API_KEY` from environment and stores it as:
```python
self._config["api_keys"]["xai"] = os.getenv("XAI_API_KEY", "")
```

But the validation code tries to access:
```python
self._config["xai_api_key"]  # This doesn't exist!
```

This causes the validation to always return `None` or empty string, triggering the false negative.

## Relevant Files

### Files to Modify

- **`src/agentic_bookkeeper/gui/dashboard_widget.py`** (Lines 547-548, 589)
  - Contains `_validate_monitoring_configuration()` method with incorrect API key access (line 547-548)
  - Contains `_initialize_document_monitor()` method with incorrect API key access (line 589)
  - Both methods need to use `self.config.get_api_key(provider)` instead of `self.config.get(f"{provider}_api_key")`

### Files to Reference (No Changes)

- **`src/agentic_bookkeeper/utils/config.py`** (Lines 94-99, 209-219)
  - Shows how API keys are stored in nested dictionary structure
  - Provides the correct `get_api_key(provider)` method to use
  - Reference to understand correct access pattern

### New Files

None. This is a surgical bug fix requiring only 2 line changes.

## Step by Step Tasks

### Step 1: Fix API Key Validation Method

- Open `src/agentic_bookkeeper/gui/dashboard_widget.py`
- Locate `_validate_monitoring_configuration()` method (around line 521)
- Find lines 547-548:
  ```python
  api_key_field = f"{llm_provider}_api_key"
  api_key = self.config.get(api_key_field)
  ```
- Replace with:
  ```python
  api_key = self.config.get_api_key(llm_provider)
  ```
- Remove the now-unused `api_key_field` variable
- Verify the error message on line 550 still references `llm_provider` correctly

### Step 2: Fix API Key Retrieval in Initialization Method

- In same file `src/agentic_bookkeeper/gui/dashboard_widget.py`
- Locate `_initialize_document_monitor()` method (around line 570)
- Find line 589:
  ```python
  api_key = self.config.get(f"{llm_provider_name}_api_key")
  ```
- Replace with:
  ```python
  api_key = self.config.get_api_key(llm_provider_name)
  ```

### Step 3: Verify Python Syntax

- Compile the modified file to check for syntax errors:
  ```bash
  python -m py_compile src/agentic_bookkeeper/gui/dashboard_widget.py
  ```
- Test import:
  ```bash
  python -c "from agentic_bookkeeper.gui.dashboard_widget import DashboardWidget; print('Import OK')"
  ```

### Step 4: Test Bug Fix with Environment Variables

- Set test environment variable:
  ```bash
  export XAI_API_KEY="test-key-12345"
  ```
- Run the application:
  ```bash
  ./run_bookkeeper.sh
  ```
- Configure settings with XAI provider
- Click "Start Monitoring" - should no longer show "API key not configured" error
- Verify monitoring initialization proceeds (may fail later due to invalid test key, but validation should pass)

### Step 5: Test Bug Fix with All Providers

- Test with each provider to ensure fix works for all:
  ```bash
  export OPENAI_API_KEY="test-openai"
  export ANTHROPIC_API_KEY="test-anthropic"
  export GOOGLE_API_KEY="test-google"
  ```
- For each provider, verify validation passes and detects the API key
- Verify error message only appears if API key is actually missing

### Step 6: Run Validation Commands

- Execute all validation commands listed below to ensure zero regressions
- All commands must pass without errors

## Validation Commands

Execute every command to validate the bug is fixed with zero regressions.

### Test 1: Verify Python Syntax
```bash
python -m py_compile src/agentic_bookkeeper/gui/dashboard_widget.py
```
**Expected:** No output (successful compilation)

### Test 2: Verify Imports
```bash
python -c "from agentic_bookkeeper.gui.dashboard_widget import DashboardWidget; print('✓ DashboardWidget import successful')"
```
**Expected:** `✓ DashboardWidget import successful`

### Test 3: Verify Config API Key Method Exists
```bash
python -c "from agentic_bookkeeper.utils.config import Config; c = Config(); assert hasattr(c, 'get_api_key'), 'get_api_key method missing'; print('✓ Config.get_api_key() method exists')"
```
**Expected:** `✓ Config.get_api_key() method exists`

### Test 4: Reproduce Bug Before Fix (Manual)
```bash
# Set environment variable
export XAI_API_KEY="test-xai-key-12345"

# Run application and try to start monitoring
./run_bookkeeper.sh

# Expected before fix: "API key not configured for xai" error
# Expected after fix: Validation passes, initialization proceeds
```

### Test 5: Verify API Key Detection After Fix
```bash
# Create test script to verify API key detection
python << 'EOF'
import os
os.environ['XAI_API_KEY'] = 'test-key-from-env'

from agentic_bookkeeper.utils.config import Config

config = Config()

# Verify API key loaded from environment
api_key = config.get_api_key('xai')
assert api_key == 'test-key-from-env', f"Expected 'test-key-from-env', got '{api_key}'"

print('✓ API key correctly loaded from environment variable')
print(f'✓ config.get_api_key("xai") = {api_key}')
EOF
```
**Expected:**
```
✓ API key correctly loaded from environment variable
✓ config.get_api_key("xai") = test-key-from-env
```

### Test 6: Run Unit Tests (If Available)
```bash
cd /home/stephen_bogner/slb/agentic_bookkeeper_module && python -m pytest tests/test_config.py -v
```
**Expected:** All config tests pass

### Test 7: Run GUI Tests (If Available)
```bash
cd /home/stephen_bogner/slb/agentic_bookkeeper_module && python -m pytest tests/gui/test_dashboard_widget.py -v -k "monitor" 2>/dev/null || echo "No dashboard widget tests found"
```
**Expected:** All dashboard tests pass (or message if no tests exist)

### Test 8: Full Integration Test
```bash
# Set all provider keys
export OPENAI_API_KEY="test-openai-key"
export ANTHROPIC_API_KEY="test-anthropic-key"
export XAI_API_KEY="test-xai-key"
export GOOGLE_API_KEY="test-google-key"

# Verify all providers can be validated
python << 'EOF'
from agentic_bookkeeper.utils.config import Config

config = Config()

providers = ['openai', 'anthropic', 'xai', 'google']
for provider in providers:
    api_key = config.get_api_key(provider)
    assert api_key, f"Failed to get API key for {provider}"
    assert api_key.startswith('test-'), f"Wrong API key for {provider}: {api_key}"
    print(f'✓ {provider}: API key detected successfully')

print('\n✓ All provider API keys validated successfully')
EOF
```
**Expected:**
```
✓ openai: API key detected successfully
✓ anthropic: API key detected successfully
✓ xai: API key detected successfully
✓ google: API key detected successfully

✓ All provider API keys validated successfully
```

## Notes

### Why This Bug Happened

This bug was introduced in the recent `GUI_DOCUMENT_MONITOR_FIX.md` implementation where on-demand DocumentMonitor initialization was added. The developer correctly used the Config class for other configuration values but incorrectly assumed API keys were stored as top-level keys like `"xai_api_key"` rather than in the nested `api_keys` dictionary.

### Related Code Patterns

Correct API key access pattern used elsewhere in the codebase:

**cli.py:103, 177:**
```python
api_key = config.get_api_key(args.provider)
```

The CLI correctly uses `get_api_key(provider)` method - the dashboard widget should follow the same pattern.

### Testing Recommendations

After applying this fix:

1. **Manual GUI Test:** Start application with environment variable set, configure provider, click "Start Monitoring" - should work
2. **Manual GUI Test:** Start application without environment variable, try to start monitoring - should show proper error dialog
3. **Regression Test:** Ensure existing monitoring functionality still works when API keys are configured through Settings dialog (not just environment variables)

### Security Note

This bug does not expose API keys or create security vulnerabilities. It only affects the validation logic that checks if API keys exist. The bug causes false negatives (claiming keys are missing when they exist) but never false positives (claiming keys exist when they don't).
