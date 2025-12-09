# 🚀 STREAMLIT DEPLOYMENT GUIDE

**EDMGP Data Refinery - Complete Installation & Deployment**

Version: 2.0 (Full Stack)  
Date: December 10, 2025

---

## 📦 WHAT'S INCLUDED

### Complete Application Stack

**Backend (Phase 1 - Complete):**
- ✅ 6 Python modules (~2,500 lines)
- ✅ Automated test suite (27 tests)
- ✅ CLI tool (`run_app.py`)
- ✅ Demo scripts

**Frontend (Phase 2 - Complete):**
- ✅ Streamlit UI (`streamlit_app.py`)
- ✅ Interactive waveform visualizer
- ✅ Stem labeling interface
- ✅ Manual pairing override
- ✅ Real-time validation

**Documentation:**
- ✅ 10+ comprehensive guides
- ✅ User manual
- ✅ API examples
- ✅ Test reports

---

## 🖥️ SYSTEM REQUIREMENTS

### Minimum Specifications

**Hardware:**
- **RAM:** 8GB (16GB recommended for large tracks)
- **Storage:** 10GB free space
- **CPU:** Multi-core processor (Apple Silicon M4 tested)

**Operating System:**
- ✅ macOS 11+ (Apple Silicon M4 tested)
- ✅ Windows 10/11 (tested on Windows 11)
- ✅ Linux (Ubuntu 20.04+)

**Python:**
- **Version:** 3.9+ (tested on 3.12.10)
- **Package Manager:** pip

---

## 📥 INSTALLATION

### Option 1: Fresh Install (Recommended)

#### Step 1: Clone Repository

```bash
# Using Git
git clone https://github.com/ZaryabShah/EDMGP-Data-Refinery-MVP.git
cd EDMGP-Data-Refinery-MVP

# Or download ZIP and extract
```

#### Step 2: Install Python Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, librosa, pretty_midi; print('✅ All dependencies installed')"
```

**Expected Dependencies:**
```
streamlit>=1.52.1
librosa==0.11.0
pretty-midi==0.2.10
soundfile==0.13.1
rapidfuzz==3.14.3
numpy<2.0
pandas>=2.3.3
matplotlib>=3.7.0
```

#### Step 3: Run Tests

```bash
# Verify backend functionality
python test_suite.py
```

**Expected Output:**
```
============================================================
OVERALL TEST RESULTS
============================================================
✅ ALL TEST MODULES PASSED
```

#### Step 4: Launch Streamlit

```bash
# Launch the UI
python -m streamlit run streamlit_app.py

# Or use shorter command (if streamlit is in PATH)
streamlit run streamlit_app.py
```

**App opens at:** `http://localhost:8501`

---

### Option 2: Using Virtual Environment (Isolated)

```bash
# Create virtual environment
python3 -m venv edmgp_env

# Activate
# macOS/Linux:
source edmgp_env/bin/activate
# Windows:
edmgp_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch app
streamlit run streamlit_app.py
```

---

### Option 3: Docker Deployment (Advanced)

```bash
# Create Dockerfile (see section below)
docker build -t edmgp-refinery .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data edmgp-refinery
```

---

## 🐳 DOCKER SETUP

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  edmgp-refinery:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./Clean_Dataset_Staging:/app/Clean_Dataset_Staging
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

**Usage:**
```bash
docker-compose up -d
```

---

## 🍎 macOS (M4 Apple Silicon) SPECIFIC

### ARM64 Compatibility

All dependencies are ARM64-compatible. Tested on:
- **Device:** MacBook Pro M4
- **OS:** macOS Sequoia+
- **Python:** 3.12.10 (ARM64)

### Installation Notes

```bash
# Ensure Homebrew is updated
brew update

# Install Python (if not installed)
brew install python@3.12

# Install dependencies (some may compile from source)
pip3 install -r requirements.txt

# This may take 5-10 minutes on first install
```

**Common Issue:** librosa compilation
```bash
# If librosa fails, install LLVM first
brew install llvm
export LDFLAGS="-L/opt/homebrew/opt/llvm/lib"
export CPPFLAGS="-I/opt/homebrew/opt/llvm/include"
pip3 install librosa
```

---

## 🪟 WINDOWS 11 SPECIFIC

### PowerShell Setup

```powershell
# Navigate to project
cd "C:\Users\YourName\Desktop\EDMGP-Data-Refinery-MVP"

# Install dependencies
python -m pip install -r requirements.txt

# Launch app
python -m streamlit run streamlit_app.py
```

### Windows PATH Issues

If `streamlit` command not found:

```powershell
# Add Python Scripts to PATH
$env:Path += ";C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts"

# Verify
streamlit --version
```

### Windows Defender Firewall

First run may prompt for network access:
- ✅ Allow access to private networks
- ✅ Allow access to public networks (optional)

---

## 🐧 LINUX (Ubuntu/Debian)

### System Dependencies

```bash
# Update package list
sudo apt update

# Install required libraries
sudo apt install -y \
    python3-pip \
    python3-venv \
    libsndfile1 \
    ffmpeg \
    portaudio19-dev

# Install Python dependencies
pip3 install -r requirements.txt

# Launch app
python3 -m streamlit run streamlit_app.py
```

---

## 🌐 NETWORK DEPLOYMENT

### Local Network Access

**By default, Streamlit runs on localhost only.**

To make accessible on local network:

```bash
streamlit run streamlit_app.py \
    --server.address 0.0.0.0 \
    --server.port 8501
```

**Access from other devices:**
```
http://YOUR_LOCAL_IP:8501
```

### Public Deployment (Streamlit Cloud)

#### Option 1: Streamlit Community Cloud (Free)

1. Push code to GitHub (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select repository: `EDMGP-Data-Refinery-MVP`
6. Main file: `streamlit_app.py`
7. Click "Deploy"

**Limitations:**
- Limited to 1GB RAM
- File uploads limited to 200MB
- Public URL (e.g., `yourapp.streamlit.app`)

#### Option 2: Custom Server (VPS/Cloud)

**Requirements:**
- Ubuntu/Debian server
- 4GB+ RAM
- Public IP
- Domain name (optional)

**Setup:**
```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone https://github.com/ZaryabShah/EDMGP-Data-Refinery-MVP.git
cd EDMGP-Data-Refinery-MVP

# Install dependencies
pip3 install -r requirements.txt

# Run with systemd (persistent)
sudo nano /etc/systemd/system/edmgp-refinery.service
```

**systemd Service:**
```ini
[Unit]
Description=EDMGP Data Refinery Streamlit App
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/EDMGP-Data-Refinery-MVP
ExecStart=/usr/bin/python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable edmgp-refinery
sudo systemctl start edmgp-refinery
sudo systemctl status edmgp-refinery
```

---

## 🔒 SECURITY & PERMISSIONS

### File System Permissions

```bash
# Ensure read/write access to output directory
chmod -R 755 Clean_Dataset_Staging

# Ensure read access to source files
chmod -R 644 Raw_input_sample/
```

### Environment Variables

Create `.env` file for sensitive config:

```bash
# .env
OUTPUT_ROOT=Clean_Dataset_Staging
FUZZY_MATCH_THRESHOLD=70
DEFAULT_SAMPLE_RATE=44100
```

Load in `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

OUTPUT_ROOT = os.getenv('OUTPUT_ROOT', 'Clean_Dataset_Staging')
```

---

## 🧪 POST-INSTALLATION VERIFICATION

### 1. Run Automated Tests

```bash
python test_suite.py
```

**Expected:** All 27 tests passing

### 2. Run CLI Demo

```bash
python demo_with_labels.py
```

**Expected:** Processes "Fall Down" track successfully

### 3. Launch Streamlit UI

```bash
streamlit run streamlit_app.py
```

**Expected:** Browser opens to app interface

### 4. Process Sample Track

1. Load "Fall Down" sample in UI
2. Label a few stems
3. Export
4. Verify output in `Clean_Dataset_Staging/`

---

## 📊 PERFORMANCE TUNING

### Memory Optimization

For large tracks (100+ stems):

```python
# In streamlit_app.py, add:
import streamlit as st

st.set_page_config(
    # ... existing config ...
    max_upload_size=1024,  # 1GB
)

# Clear cache periodically
@st.cache_data.clear()
def clear_cache():
    pass
```

### Parallel Processing

For batch processing, use multiprocessing:

```python
# batch_processor.py
from multiprocessing import Pool

def process_track(track_path):
    # Your processing logic
    pass

if __name__ == "__main__":
    tracks = ["track1", "track2", "track3"]
    with Pool(4) as pool:
        pool.map(process_track, tracks)
```

### Disk Space Management

```bash
# Auto-cleanup old batches
find Clean_Dataset_Staging/ -type d -name "Batch_*" -mtime +30 -exec rm -rf {} +
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Module not found" errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt --force-reinstall
```

### Issue: Streamlit won't start

```bash
# Check if port 8501 is in use
# macOS/Linux:
lsof -i :8501

# Windows:
netstat -ano | findstr :8501

# Kill process or use different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: librosa import error on M4 Mac

```bash
# Install via conda instead
conda install -c conda-forge librosa
```

### Issue: MIDI files not loading

```bash
# Install fluidsynth (optional, for MIDI playback)
brew install fluidsynth  # macOS
sudo apt install fluidsynth  # Linux
```

### Issue: Waveform visualization slow

```python
# Reduce waveform resolution in streamlit_app.py
fig, ax = plt.subplots(figsize=(10, 3))  # Smaller figure
librosa.display.waveshow(audio_mono[::10], ...)  # Downsample
```

---

## 📈 MONITORING & LOGGING

### Enable Streamlit Logs

```bash
# Run with debug logging
streamlit run streamlit_app.py --logger.level=debug
```

### Custom Application Logs

Add to `streamlit_app.py`:

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

---

## 🔄 UPDATES & MAINTENANCE

### Update Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart Streamlit
# (It auto-reloads on code changes)
```

### Database Migrations (Future)

If you add database support:

```bash
# Example with SQLite
python manage.py migrate
```

---

## 📞 SUPPORT MATRIX

| Platform | Status | Notes |
|----------|--------|-------|
| **macOS M4** | ✅ Fully Tested | Primary development platform |
| **Windows 11** | ✅ Fully Tested | PowerShell commands |
| **Linux Ubuntu** | ✅ Compatible | May need system deps |
| **Docker** | ✅ Supported | See Dockerfile |
| **Streamlit Cloud** | ⚠️ Limited | RAM/storage constraints |

---

## 🎯 PRODUCTION CHECKLIST

Before deploying to production:

- [ ] All tests passing (`python test_suite.py`)
- [ ] Sample data processed successfully
- [ ] Output files validated in DAW
- [ ] Documentation reviewed
- [ ] Backup strategy in place
- [ ] Monitoring/logging configured
- [ ] Security permissions set
- [ ] Network access configured
- [ ] User training completed

---

## 📚 ADDITIONAL RESOURCES

**Documentation:**
- `README.md` - Project overview
- `STREAMLIT_USER_GUIDE.md` - UI usage guide
- `CLIENT_HANDOFF.md` - Client onboarding
- `FINAL_TEST_REPORT.md` - Test results

**Support:**
- GitHub Issues: [github.com/ZaryabShah/EDMGP-Data-Refinery-MVP/issues](https://github.com/ZaryabShah/EDMGP-Data-Refinery-MVP/issues)
- Email: [Your support email]

---

**Created:** December 10, 2025  
**Version:** 2.0 (Full Stack Deployment)  
**Status:** ✅ Production Ready
