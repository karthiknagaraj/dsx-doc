# Installation & Setup Guide

## System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM
- 500MB disk space for dependencies and data
- Internet connection (for LLM API calls)

**Recommended:**
- Python 3.11 (tested version)
- 8GB+ RAM
- 2GB disk space
- High-speed internet connection

## Prerequisites

### 1. Get an LLM API Key

The documentation generation requires an LLM API. We use **OpenRouter** by default (supports 200+ models).

#### Option A: OpenRouter (Recommended)
1. Go to https://openrouter.ai/
2. Sign up for a free account
3. Copy your API key from https://openrouter.ai/keys
4. Cost: Pay-as-you-go ($0.50-$10 per 1M tokens depending on model)

#### Option B: Alternative Providers
- **OpenAI**: https://openai.com/api/ (requires paid account)
- **Anthropic**: https://www.anthropic.com/claude (API access)
- **Local Models**: Use locally-run LLMs via OpenAI-compatible endpoints

### 2. Get Your DataStage DSX Files
- Export jobs from DataStage Manager or Director
- Files typically end with `.dsx` extension
- One file per job recommended

---

## Installation Methods

### Method 1: Local Development (Recommended for Beginners)

#### Step 1: Clone or Download the Repository
```powershell
# Using Git (if installed)
git clone https://github.com/YOUR-USERNAME/dsx-doc-assistant.git
cd dsx-doc-assistant

# Or download as ZIP and extract
```

#### Step 2: Create Python Virtual Environment
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Or if you prefer conda
conda create -n dsx-assistant python=3.11
conda activate dsx-assistant
```

#### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt

# For testing (optional)
pip install pytest pytest-mock
```

#### Step 4: Set Up Environment Variables
```powershell
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# Open .env in your editor: notepad .env
```

Edit `.env`:
```env
DSX_API_KEY=your_openrouter_api_key_here
DSX_CHAT_MODEL=openai/gpt-oss-120b
DSX_CHAT_BASE_URL=https://openrouter.ai/api/v1
DSX_CHAT_PROVIDER=openrouter
```

#### Step 5: Place DSX Files
```powershell
# Create input directory if needed
mkdir dsx_files_input -Force

# Copy your .dsx files to this directory
Copy-Item "C:\path\to\your\files\*.dsx" dsx_files_input\
```

#### Step 6: Run the Application
```powershell
# Launch the Streamlit app
streamlit run frontend.py

# The app will open in your browser at http://localhost:8501
```

---

### Method 2: Docker (Recommended for Deployment)

#### Option A: Using Docker Desktop

**Install Docker Desktop** (if not already installed):
1. Download from https://www.docker.com/products/docker-desktop
2. Install following the installer prompts
3. Launch Docker Desktop

**Build and Run:**
```powershell
# Build the Docker image
docker build -t dsx-doc-assistant:latest .

# Run the container
docker run -p 8501:8501 `
  -e DSX_API_KEY="your_api_key" `
  -e DSX_CHAT_MODEL="openai/gpt-oss-120b" `
  -v ${PWD}/dsx_files_input:/app/dsx_files_input `
  -v ${PWD}/data:/app/data `
  dsx-doc-assistant:latest

# App will be available at http://localhost:8501
```

#### Option B: Using Docker Compose

**Install Docker Compose** (included with Docker Desktop on Windows)

**Create `.env` file for Docker:**
```powershell
cat > .env << 'EOF'
DSX_API_KEY=your_openrouter_api_key_here
DSX_CHAT_MODEL=openai/gpt-oss-120b
DSX_CHAT_BASE_URL=https://openrouter.ai/api/v1
DSX_CHAT_PROVIDER=openrouter
EOF
```

**Start the application:**
```powershell
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Method 3: Conda (Alternative Environment Manager)

```powershell
# Create environment
conda create -n dsx-assistant python=3.11
conda activate dsx-assistant

# Install dependencies
pip install -r requirements.txt

# Set up environment (same as Method 1)
cp .env.example .env
# Edit .env with your API key

# Run the app
streamlit run frontend.py
```

---

## Verification Steps

### 1. Verify Python Installation
```powershell
python --version
# Should show Python 3.9 or higher
```

### 2. Verify Package Installation
```powershell
pip list
# Should show streamlit, python-dotenv, requests, urllib3, jsonschema
```

### 3. Verify API Key
```powershell
$env:DSX_API_KEY = "your_api_key"
echo $env:DSX_API_KEY
```

### 4. Test API Connectivity
```powershell
python -c "
import os
from doc_generator import load_chat_config
cfg = load_chat_config()
print(f'✓ Config loaded: {cfg.provider} with {cfg.model}')
"
```

### 5. Verify Database Setup
```powershell
python -c "
import sqlite3
conn = sqlite3.connect('dsx_graph_all.sqlite')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print(f'✓ Database tables: {[row[0] for row in cursor.fetchall()]}')
conn.close()
"
```

---

## First Run Checklist

- [ ] Python 3.9+ installed and verified
- [ ] Virtual environment created and activated
- [ ] Dependencies installed via `pip install -r requirements.txt`
- [ ] `.env` file created with `DSX_API_KEY` set
- [ ] API key is valid and has available credits
- [ ] DSX files placed in `dsx_files_input/` directory
- [ ] Application starts without errors: `streamlit run frontend.py`
- [ ] Browser shows the Streamlit interface at `http://localhost:8501`

---

## Troubleshooting Installation

### Issue: Python not found
```
'python' is not recognized as an internal or external command
```
**Solution**: 
1. Add Python to PATH: `python -m pip --version` to verify
2. Use `python3` instead of `python`
3. Reinstall Python and check "Add Python to PATH" during installation

### Issue: Virtual environment not activating
```
.\venv\Scripts\Activate.ps1 : File cannot be loaded
```
**Solution**:
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1
```

### Issue: Module not found
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**:
```powershell
# Verify virtual environment is active
# Then reinstall:
pip install -r requirements.txt

# Or install specific package
pip install streamlit
```

### Issue: API key error
```
ValueError: Missing API key. Set DSX_API_KEY in your .env file
```
**Solution**:
1. Check `.env` file exists
2. Verify `DSX_API_KEY=your_actual_key_here` (not template text)
3. No spaces around `=` sign
4. Restart the application

### Issue: Connection refused
```
ConnectionRefusedError: Failed to establish LLM API connection
```
**Solution**:
1. Check internet connection: `ping 8.8.8.8`
2. Verify API key is valid: Test at https://openrouter.ai/keys
3. Check API status: https://status.openrouter.ai/
4. Increase timeout: Set `DSX_CHAT_TIMEOUT_SEC=300` in `.env`

### Issue: Streamlit port already in use
```
Error: Port 8501 is already in use.
```
**Solution**:
```powershell
# Kill process using port 8501
Get-Process | Where-Object {$_.Name -eq "pythonw"} | Stop-Process

# Or use different port
streamlit run frontend.py --server.port 8502
```

---

## Next Steps

After successful installation:

1. **Try the Documentation Tab**:
   - Upload a `.dsx` file
   - Click "Ingest to Database"
   - Generate documentation

2. **Try Semantic Search Tab**:
   - Select a job
   - Build chunks
   - Generate embeddings
   - Ask questions

3. **For CI/CD Integration**:
   - See [DEPLOYMENT.md](DEPLOYMENT.md)
   - Check [CI_CD_SETUP.md](CI_CD_SETUP.md)

4. **Command-Line Usage**:
   - See [USAGE.md](../README.md#usage) for CLI examples

---

## Getting Help

- **Documentation**: Check [README.md](../README.md) and [USAGE.md](USAGE.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: Create a GitHub Issue with error details

