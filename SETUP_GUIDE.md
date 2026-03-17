# 🚀 Complete Setup & Installation Guide

**URL Fraud Detection System - Step-by-Step Installation**

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 7+, macOS 10.12+, Linux (any modern distro)
- **Python**: 3.8 or higher
- **RAM**: 512 MB minimum
- **Disk Space**: ~50 MB
- **Internet**: Required for PhishTank API & domain validation

### Recommended Setup

- **Python**: 3.10 or 3.11
- **RAM**: 2 GB+
- **SSD**: For faster startup
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+

---

## Installation Steps

### Step 1: Verify Python Installation

**Windows**:
```powershell
python --version
```

**macOS/Linux**:
```bash
python3 --version
```

Expected output: `Python 3.8.0` or higher

**If Python not found**:
- Download from [python.org](https://www.python.org/downloads/)
- Windows: Use installer with "Add Python to PATH" ✅
- macOS: Use installer or Homebrew: `brew install python3`
- Linux: `sudo apt install python3` (Ubuntu/Debian)

---

### Step 2: Create Project Directory

**Windows**:
```powershell
mkdir C:\detection-project
cd C:\detection-project
```

**macOS/Linux**:
```bash
mkdir ~/detection-project
cd ~/detection-project
```

---

### Step 3: Set Up Virtual Environment

Virtual environments isolate project dependencies from system Python.

**Windows**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an error about execution policies:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verification**:
```
You should see (venv) at the start of your terminal line
(venv) C:\detection-project>
```

---

### Step 4: Install Dependencies

**Copy requirements.txt** to your project directory, then:

```powershell
# Windows
pip install -r requirements.txt

# macOS/Linux
pip3 install -r requirements.txt
```

**Expected Output**:
```
Collecting Flask==2.3.3
Downloading flask-2.3.3-py3-none-any.whl (101 kB)
Installing collected packages: Werkzeug, Jinja2, click, itsdangerous, Flask, requests
Successfully installed Flask-2.3.3 Werkzeug-2.3.7 requests-2.31.0
```

**Verify Installation**:
```python
pip list
```

Should show:
- Flask 2.3.3
- Werkzeug 2.3.7
- requests 2.31.0

---

### Step 5: Create Project Structure

Ensure files are in correct locations:

```
detection-project/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── blacklist.txt            # Blocked URLs (auto-created)
├── templates/
│   └── index.html           # Web interface
├── README.md                # Project documentation
├── LAB_GUIDE.md            # Lab exercises
├── TESTING_GUIDE.md        # Test cases
└── SETUP_GUIDE.md          # This file
```

---

### Step 6: Create Necessary Files

**blacklist.txt** (if not present):
```
# Phishing URLs to block
phishing-example.com
fake-paypal.net
scam-amazon.co.uk
```

---

### Step 7: Run the Application

**Windows**:
```powershell
(venv) C:\detection-project> python app.py
```

**macOS/Linux**:
```bash
(venv) ~/detection-project$ python3 app.py
```

**Expected Output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

---

### Step 8: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see:
- Black gradient background
- White input field with "Check" button
- Ready to analyze URLs

---

## Detailed Component Explanation

### Flask Application (app.py)

**What it does**:
- Creates web server on localhost:5000
- Processes URL requests
- Implements threat detection algorithms
- Manages blacklist file
- Returns JSON results

**Key Functions**:

```python
check_url(url)              # Main detection orchestrator
domain_exists(domain)        # Verify domain is reachable
check_blacklist(url)        # Check against known phishing
check_typosquatting(url)    # Detect brand misuse
check_suspicious_subdomains(url)  # Analyze subdomain structure
check_ssl_certificate(url)  # Validate HTTPS certificate
check_html_content(url)     # Analyze form/redirect behavior
check_phishtank(url)        # Query PhishTank API
```

**Dependencies**:
- `flask`: Web framework
- `requests`: HTTP library for external APIs
- `ssl`: Certificate validation
- `socket`: Network connectivity
- `urllib.parse`: URL parsing

---

### Web Interface (templates/index.html)

**What it does**:
- Provides modern, animated user interface
- Sends URLs to Flask backend
- Displays threat analysis results
- Manages blacklist additions

**Key Sections**:

```html
<!-- Input Form -->
<input type="text" id="urlInput" placeholder="Enter URL...">
<button onclick="checkURL()">Check</button>

<!-- Results Display -->
<div id="result" class="result">
  <div class="score-circle">85%</div>
  <div class="details">
    <div class="detail-item">Typosquatting: Detected</div>
    <div class="detail-item">SSL: Invalid</div>
  </div>
  <button onclick="addToBlacklist()">Add to Blacklist</button>
</div>
```

---

### Blacklist File (blacklist.txt)

**What it does**:
- Stores user-identified phishing URLs
- Pre-populated with example URLs
- Automatically checked for quick blocking

**Format**:
```
one-url-per-line.com
another-phishing.net
malicious-domain.xyz
# Comments start with #
```

---

## Configuration & Customization

### Adjust Detection Thresholds

In `app.py`, modify the scoring thresholds:

```python
# Current thresholds
BLACKLIST_PENALTY = 50          # Points for blacklist match
SSL_ISSUE_PENALTY = 25          # Points for SSL problems
SUBDOMAIN_PENALTY = 15          # Points per suspicious subdomain
TYPO_PENALTY = 25               # Points for typosquatting
```

**To make detection stricter**: Increase penalties
**To reduce false positives**: Decrease penalties

---

### Adjust PhishTank API

The system queries PhishTank for known phishing URLs:

```python
PHISHTANK_API_URL = "http://checkurl.phishtank.com/checkurl/"
PHISHTANK_TIMEOUT = 5  # seconds
```

To disable PhishTank (for offline testing):
```python
def check_phishtank(self, url):
    return 0  # Skip API call
```

---

### Enable/Disable Features

To disable specific checks:

```python
def check_url(self, domain):
    score = 0
    # score += self.check_typosquatting(domain)  # Disable
    score += self.check_suspicious_subdomains(domain)
    score += self.check_ssl_certificate(url)
    # score += self.check_phishtank(url)  # Disable PhishTank
    return score
```

---

## Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'flask'"

**Cause**: Flask not installed or virtual environment not activated

**Solution**:
```powershell
# Verify venv is activated (should see (venv) in prompt)
# If not:
.\venv\Scripts\Activate.ps1

# Install Flask:
pip install Flask==2.3.3
```

---

### Issue 2: "Address already in use"

**Cause**: Port 5000 already in use by another application

**Solution 1** - Kill existing process:

**Windows**:
```powershell
netstat -ano | findstr :5000
taskkill /PID [PID_NUMBER] /F
```

**macOS/Linux**:
```bash
lsof -i :5000
kill -9 [PID]
```

**Solution 2** - Use different port:

Edit `app.py`:
```python
if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Use 5001 instead
```

---

### Issue 3: "ConnectionError: Failed to establish connection"

**Cause**: Domain checking is timing out or network is unavailable

**Solution**:
```python
# Check internet connection
ping google.com

# Increase timeout in app.py:
socket.create_connection((domain, 80), timeout=10)  # Was 5
```

---

### Issue 4: URLs show "Invalid URL" incorrectly

**Cause**: Domain_exists() is too strict or network issues

**Solution**:
```python
# Add debug output
print(f"Checking {domain}...")
try:
    socket.create_connection((domain, 80), timeout=10)
    print("Connected successfully")
except socket.error as e:
    print(f"Connection failed: {e}")
```

---

### Issue 5: PhishTank API returning errors

**Cause**: API timeout, rate limiting, or service unavailable

**Solution**:
```python
try:
    response = requests.get(url, timeout=5)
except requests.Timeout:
    print("PhishTank API timeout - skipping")
    return 0  # Skip check
except Exception as e:
    print(f"PhishTank error: {e}")
    return 0
```

---

### Issue 6: Animations not smooth

**Cause**: Browser performance or CSS issues

**Solution**:
- Update browser to latest version
- Disable browser extensions
- Check browser console for errors (F12)
- Test in different browser

---

### Issue 7: Blacklist not persisting

**Cause**: File permissions or incorrect path

**Solution**:
```python
# Verify file is created
import os
print(os.path.exists('blacklist.txt'))  # Should be True

# Verify write permissions
with open('blacklist.txt', 'a') as f:
    f.write('\ntest-url.com\n')
```

---

## Running on Different Ports

If port 5000 is unavailable, modify `app.py`:

```python
if __name__ == "__main__":
    app.run(
        debug=True,
        host='127.0.0.1',  # Localhost only
        port=8000          # Change to 8000
    )
```

Access at: `http://localhost:8000`

---

## Running on Network

To allow other computers to access the application:

**Edit app.py**:
```python
if __name__ == "__main__":
    app.run(
        debug=True,
        host='0.0.0.0',   # All interfaces
        port=5000
    )
```

Then access from other computers:
```
http://[YOUR_IP_ADDRESS]:5000
```

Find your IP:
- Windows: `ipconfig` → IPv4 Address
- macOS/Linux: `ifconfig` → inet

---

## Deployment Checklist

### Development Environment ✅
- [ ] Python 3.8+ installed
- [ ] Virtual environment set up
- [ ] Dependencies installed
- [ ] app.py runs without errors
- [ ] Web interface accessible
- [ ] Blacklist functionality works

### Testing Environment ✅
- [ ] All 10 detection methods working
- [ ] Legitimate sites score <20%
- [ ] Phishing sites score >60%
- [ ] Invalid domains score 100%
- [ ] Animations smooth
- [ ] No console errors

### College Submission ✅
- [ ] README.md complete
- [ ] LAB_GUIDE.md created
- [ ] TESTING_GUIDE.md created
- [ ] All code commented
- [ ] No hardcoded lists
- [ ] Dynamic algorithms working
- [ ] Performance acceptable

### Production Considerations ⚠️
- [ ] Debug mode OFF (`debug=False`)
- [ ] Production server (Gunicorn/uWSGI)
- [ ] HTTPS enabled
- [ ] Rate limiting implemented
- [ ] Error logging configured
- [ ] Database for persistence (SQLite)
- [ ] Security headers configured

---

## Deactivating Virtual Environment

When done working:

**Windows**:
```powershell
deactivate
```

**macOS/Linux**:
```bash
deactivate
```

---

## Next Steps After Installation

1. **Read README.md** - Understand the project
2. **Run test cases** - Verify with TESTING_GUIDE.md
3. **Complete lab exercises** - Use LAB_GUIDE.md
4. **Customize thresholds** - Fine-tune detection
5. **Test extensively** - Find edge cases
6. **Document findings** - Create lab report
7. **Submit to college** - Package and deliver

---

## Getting Help

### Debug Mode
Enable detailed logging in app.py:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs
```python
# Add debug prints
print(f"URL: {url}")
print(f"Score: {score}")
print(f"Checks passed: {passed}")
```

### Browser Console
Press `F12` while using web interface to see:
- Network requests
- JavaScript errors
- Console messages
- Performance metrics

---

## Quick Reference Commands

```powershell
# Windows
python --version                    # Check Python version
cd C:\detection-project            # Navigate to project
.\venv\Scripts\Activate.ps1         # Activate venv
pip list                            # List installed packages
pip install -r requirements.txt     # Install dependencies
python app.py                       # Run application
deactivate                          # Deactivate venv

# macOS/Linux
python3 --version
cd ~/detection-project
source venv/bin/activate
pip list
pip install -r requirements.txt
python3 app.py
deactivate
```

---

## Installation Complete ✅

Your URL Fraud Detection System is ready!

```
Next: Open http://localhost:5000 in your browser
Test: Try checking google.com and facebook2.com
Learn: Read LAB_GUIDE.md for exercises
```

---

**Questions?** Check the troubleshooting section above or review code comments in app.py.

**Ready for college submission!** Package all files and documentation together.

