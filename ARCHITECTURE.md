# 🏗️ Technical Architecture & Design Document

**URL Fraud Detection System - System Design & Implementation**

---

## 1. System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           HTML/CSS/JavaScript Frontend               │   │
│  │  - Input field for URL                              │   │
│  │  - Real-time result display with animations         │   │
│  │  - Blacklist management interface                   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests (JSON)
                           ↓
┌──────────────────────────────────────────────────────────────┐
│              FLASK WEB SERVER (localhost:5000)               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  URL Fraud Detector Class                           │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 10 Independent Detection Methods:              │  │   │
│  │  │  1. Blacklist Check (local + URLhaus)          │  │   │
│  │  │  2. Typosquatting Detection (algorithms)        │  │   │
│  │  │  3. Suspicious Subdomains (structural)          │  │   │
│  │  │  4. SSL Certificate Validation                 │  │   │
│  │  │  5. Certificate Mismatch Check                 │  │   │
│  │  │  6. HTML Content Analysis (behavioral)          │  │   │
│  │  │  7. PhishTank Database Query                   │  │   │
│  │  │  8. Domain Reachability (DNS + TCP)            │  │   │
│  │  │  9. URL Pattern Analysis                       │  │   │
│  │  │  10. Suspicious Keyword Detection               │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Persistence Layer                                  │   │
│  │  - Blacklist file management                       │   │
│  │  - Error handling & logging                        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬─────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        ↓          ↓          ↓          ↓
   ┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
   │ blackl │ │ System │ │PhishTank│ │ External │
   │ ist.   │ │ Sockets│ │  API    │ │Websites  │
   │ txt    │ │ DNS/TCP│ │         │ │ (SSL)    │
   └────────┘ └────────┘ └─────────┘ └──────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Layer (index.html)

**Purpose**: User interface for URL threat analysis

**Key Components**:

```
┌─────────────────────────────┐
│     Input Container         │
│  ┌───────────────────────┐  │
│  │  URL Input Field      │  │
│  │  Check Button         │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
           ↓ (JavaScript)
┌─────────────────────────────┐
│  Fetch API → /check endpoint│
└─────────────────────────────┘
           ↓ (JSON Response)
┌─────────────────────────────┐
│   Result Display Container  │
│  ┌───────────────────────┐  │
│  │  Score Circle (0-100%)│  │
│  │  Risk Level (color)   │  │
│  │  Detail Items:        │  │
│  │    - Blacklist: Yes   │  │
│  │    - Typosquatting: No│  │
│  │    - SSL: Valid       │  │
│  │  Add to Blacklist btn │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

**Communication Protocol**:

```
Request:
POST /check HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "url": "facebook2.com"
}

Response:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "url": "facebook2.com",
  "risk_score": 42,
  "risk_level": "warning",
  "checks": {
    "blacklist": false,
    "typosquatting": true,
    "subdomains": false,
    "ssl": false,
    "phishtank": false,
    ...
  },
  "analysis": {
    "typosquatting": "Numeric suffix detected (facebook + 2)",
    ...
  }
}
```

---

### 2.2 Backend Layer (app.py)

**Purpose**: Core threat detection engine

**Architecture Pattern**: Class-Based Detector

```python
class URLFraudDetector:
    def __init__(self):
        self.blacklist = []
    
    def check_url(self, url):
        """Orchestrator - calls all detection methods"""
        # Parse URL
        # Run 10 independent checks
        # Aggregate scores
        # Return results
    
    def check_method_1(self, url):
        """Individual detection method"""
        score = 0
        # Specific logic
        return score

    # ... 9 more check methods
```

**Scoring System**:

```
Final Risk Score = Sum of all check scores (0-100%)

Risk Level:
  0-25%   = Safe (Green)
  26-50%  = Warning (Yellow)
  51-75%  = Suspicious (Orange)
  76-100% = Dangerous (Red)
```

---

## 3. Detection Methods Architecture

### Method 1: Blacklist Check

```
┌─────────────────────────────────┐
│  Input: URL                     │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Load blacklist.txt             │
│  Strip whitespace/comments      │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Check if URL in local list     │
│  If yes: +50 points             │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Query URLhaus API              │
│  (if network available)         │
│  If yes: +50 points             │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  Return score (0, 50, or 100)   │
└─────────────────────────────────┘
```

**Code Pattern**:
```python
def check_blacklist(self, url):
    score = 0
    domain = self.extract_domain(url)
    
    # Check local blacklist
    if domain in self.load_blacklist():
        score += 50
    
    # Check URLhaus API
    try:
        response = requests.get(
            f"https://urlhaus-api.abuse.ch/v1/url/",
            params={"url": url},
            timeout=5
        )
        if response.json().get("query_status") == "found":
            score += 50
    except:
        pass  # API unavailable
    
    return min(score, 100)
```

---

### Method 2: Typosquatting Detection

**Algorithm**: Pattern-Based Detection (No Hardcoding)

```
┌─────────────────────────────────┐
│  Input: domain = "g00gle.com"   │
└─────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│  Check 1: Numeric Suffix             │
│  Pattern: domain + only digits       │
│  Example: "facebook2", "amazon99"    │
│  If detected: +25 points             │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│  Check 2: Character Substitution     │
│  Common patterns:                    │
│  0→o, 1→i, 3→e, 5→s, 7→l, 8→b       │
│  Example: "g00gle" (0→o), "am4z0n"   │
│  If detected: +20 points             │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│  Check 3: Excessive Separators       │
│  Count hyphens/underscores           │
│  Legitimate: 0-1 separators          │
│  Suspicious: 2+ separators           │
│  Example: "face-book-login"          │
│  If detected: +15 points             │
└──────────────────────────────────────┘
           ↓
┌──────────────────────────────────────┐
│  Return combined score (capped 100)  │
└──────────────────────────────────────┘
```

**Code Implementation**:
```python
def check_typosquatting(self, domain):
    score = 0
    
    # Check numeric suffix
    if any(char.isdigit() for char in domain):
        # Extract last part after dot
        parts = domain.split('.')
        if parts[-2].isdigit():  # Domain before TLD is only digits
            score += 25
    
    # Check character substitutions
    suspicious_pairs = {
        '0': 'o', '1': 'i', '3': 'e',
        '5': 's', '7': 'l', '8': 'b'
    }
    for placeholder, real in suspicious_pairs.items():
        if placeholder in domain and real in domain:
            score += min(20, len([c for c in domain if c == placeholder]) * 5)
    
    # Check excessive separators
    separator_count = domain.count('-') + domain.count('_')
    if separator_count > 1:
        score += 15 * min(separator_count - 1, 2)
    
    return min(score, 100)
```

---

### Method 3: Suspicious Subdomains

**Algorithm**: Structural Analysis

```
┌──────────────────────────────────┐
│  Input: url = "a.b.google.com"   │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Extract subdomains              │
│  a.b vs google.com               │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Count subdomain levels          │
│  a.b.google.com = 3 levels       │
│  google.com = 1 level            │
│  Threshold: >2 suspicious        │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Check for single-letter parts   │
│  "a" and "b" are suspicious      │
│  Legitimate: mail, api, cdn      │
│  Suspicious: x, y, z, a.b, q.r   │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│  Score: 10 pts/level + 5 pts/part│
└──────────────────────────────────┘
```

---

### Method 4-5: SSL Certificate Checks

**Method 4: SSL Validation**
```
URL → Extract domain → Connect with SSL context
→ Get certificate object → Check:
  1. Certificate exists? (10 pts if no)
  2. Not expired? (15 pts if yes)
  3. Valid chain? (10 pts if invalid)
```

**Method 5: Certificate Mismatch**
```
Certificate CN/SAN → Extract domains
→ Compare with requested domain
→ If mismatch: +30 points

Example:
URL: https://amazon.attacker.com
Cert: amazon.attacker.com (matches URL) ✓
Cert: amazon.com (doesn't match URL) ✗ MISMATCH!
```

---

### Method 6: HTML Content Analysis

**Algorithm**: Behavioral Pattern Detection

```
┌─────────────────────────────────────┐
│  Fetch webpage HTML                 │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Pattern 1: Login Forms             │
│  Check for <form> + <input type="password">
│  Baseline: +10 points               │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Pattern 2: Action Words            │
│  Keywords: verify, confirm, update, │
│            secure, validate, click   │
│  If form + word: +25 points         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Pattern 3: Redirects               │
│  window.location = ...              │
│  <meta http-equiv="refresh">        │
│  If detected: +30 points            │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Pattern 4: JavaScript Execution    │
│  Count <script> tags                │
│  If >3 scripts: +10 points          │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Return weighted score              │
└─────────────────────────────────────┘
```

---

### Methods 7-10: Other Checks

**Method 7: PhishTank Database**
```
URL → Query PhishTank API → Returns in_database flag
If found: +50 points
Requires: Internet, API timeout handling
```

**Method 8: Domain Reachability**
```
Domain → DNS Resolution → TCP Connect (port 80/443)
Invalid: +100 points (invalid domain error)
Valid: 0 points
Pattern: socket.create_connection() with timeout
```

**Method 9: URL Pattern Analysis**
```
Check:
1. IP address instead of domain: +25 points
2. Non-standard port (99999): +15 points
3. Unusual TLDs or format: +10 points
```

**Method 10: Suspicious Keywords**
```
Common phishing action words:
verify, confirm, update, secure, validate, account,
password, login, urgent, immediately, click, payment

Pattern: Presence without legitimate context
Score: +5 points each (max 50)
```

---

## 4. Data Flow Diagrams

### Complete Request Flow

```
1. User Input
   ↓
2. JavaScript checkURL()
   ↓
3. fetch() to /check endpoint
   ↓
4. Flask receives request
   ↓
5. URL validation
   ├─ Domain exists? (DNS + TCP)
   └─ Invalid? → Return 100% risk
   ↓
6. Parallel checks (independent)
   ├─ check_blacklist()
   ├─ check_typosquatting()
   ├─ check_suspicious_subdomains()
   ├─ check_ssl_certificate()
   ├─ check_certificate_mismatch()
   ├─ check_html_content()
   ├─ check_phishtank()
   ├─ check_url_patterns()
   └─ check_suspicious_keywords()
   ↓
7. Score aggregation
   Final_Score = Sum of all checks / 10 (cap 100)
   ↓
8. Risk level determination
   ├─ 0-25%: Safe (Green)
   ├─ 26-50%: Warning (Yellow)
   ├─ 51-75%: Suspicious (Orange)
   └─ 76-100%: Dangerous (Red)
   ↓
9. JSON response
   ↓
10. JavaScript displayResult()
   ↓
11. CSS animations trigger
   ↓
12. User sees results
```

---

## 5. Algorithm Complexity Analysis

### Time Complexity

| Check Method | Time | Notes |
|---|---|---|
| Blacklist | O(n) | Linear in blacklist size |
| Typosquatting | O(m) | Linear in domain length |
| Subdomains | O(m) | Linear in domain length |
| SSL Cert | O(1) | Fixed time (timeout) |
| HTML Analysis | O(p) | Linear in page size |
| PhishTank | O(1) | API timeout fixed |
| Domain Check | O(1) | Socket timeout fixed |
| Patterns | O(m) | Linear in domain length |

**Overall**: O(p) where p = page size (for HTML fetching)
Dominated by HTML content analysis (slowest)

### Space Complexity

| Component | Space |
|---|---|
| Blacklist (memory) | O(n) - size of list |
| URL parsing | O(m) - domain length |
| HTML parsing | O(p) - page size |
| Results object | O(1) - fixed size |

---

## 6. Error Handling Architecture

```
Try-Catch Pattern:

try:
    # Specific operation
    response = requests.get(url, timeout=5)
except requests.Timeout:
    # Network timeout
    score += 0  # Skip check
except requests.ConnectionError:
    # Connection failed
    score += 0
except socket.error:
    # Socket operation failed
    invalid = True
except Exception:
    # Unexpected error
    log_error()
    score += 0
finally:
    # Cleanup
    close_sockets()
```

**Design Principle**: Fail gracefully
- Never crash if check fails
- Skip individual checks, continue others
- Always return valid response
- Log errors for debugging

---

## 7. Security Considerations

### Input Validation

```
URL Input:
1. Length check (max 2048 chars)
2. Character validation (alphanumeric + special)
3. Format check (looks like URL?)
4. Escape special characters (XSS prevention)
```

### API Safety

```
External API Calls:
1. Timeout protection (5-10 seconds)
2. Error handling (catch all exceptions)
3. Rate limiting (1 request per user)
4. Response validation (check format)
5. No credential storage
```

### File Access

```
blacklist.txt:
1. Read-only initially
2. Append-only writes
3. No arbitrary file access
4. Path validation (prevent directory traversal)
```

---

## 8. Performance Optimization

### Current Bottlenecks

1. **HTML Content Analysis**: ~1-3 seconds (page fetch + parsing)
2. **PhishTank API**: ~1-2 seconds (network latency)
3. **SSL Certificate**: ~0.5-1 second (handshake)

### Optimization Strategies

```python
# 1. Caching
url_cache = {}  # Cache results for 1 hour
if url in url_cache:
    return url_cache[url]

# 2. Timeouts
socket.settimeout(5)    # Fail fast
requests.timeout = 3    # Don't wait forever

# 3. Parallel Processing (Future)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(check_method, urls)

# 4. Lightweight Checks First
# Run fast checks (domain, blacklist) before slow ones
# Skip HTML analysis if already 100% flagged
```

---

## 9. Extensibility Design

### Adding New Detection Methods

```python
# Step 1: Add method to class
def check_new_detection(self, url):
    score = 0
    # Implementation
    return score

# Step 2: Update check_url orchestrator
def check_url(self, url):
    # ... existing checks
    score += self.check_new_detection(url)
    # ... rest of checks

# Step 3: Update frontend
// Added to detail items display
"new_detection": result.checks.new_detection
```

### Adding New External APIs

```python
def check_new_api(self, url):
    try:
        response = requests.get(
            "https://api.example.com/check",
            params={"url": url},
            timeout=5
        )
        if response.json()["is_phishing"]:
            return 50
    except:
        pass  # API unavailable
    return 0
```

---

## 10. Testing Architecture

### Unit Test Pattern

```python
def test_typosquatting():
    detector = URLFraudDetector()
    
    # Test case 1: Numeric suffix
    assert detector.check_typosquatting("facebook2.com") > 20
    
    # Test case 2: No typosquatting
    assert detector.check_typosquatting("facebook.com") < 10
    
    # Test case 3: Char substitution
    assert detector.check_typosquatting("g00gle.com") > 20
```

### Integration Test Pattern

```python
def test_full_analysis():
    detector = URLFraudDetector()
    
    result = detector.check_url("google.com")
    assert result["risk_score"] < 20  # Legitimate
    assert result["risk_level"] == "safe"
    
    result = detector.check_url("facebook2.com")
    assert result["risk_score"] > 30  # Suspicious
```

---

## 11. Deployment Architecture

### Development
```
localhost:5000
├─ Debug mode: ON
├─ Error verbose: ON
├─ No SSL required (HTTP)
└─ Local files only
```

### Production (Future)
```
Production Server
├─ WSGI Server (Gunicorn/uWSGI)
├─ Reverse Proxy (Nginx)
├─ HTTPS/SSL required
├─ Debug mode: OFF
├─ Database (SQLite/PostgreSQL)
├─ Logging system
└─ Rate limiting
```

---

## 12. Code Organization

```
app.py (600 lines)
├─ Imports (40 lines)
├─ Configuration (20 lines)
├─ URLFraudDetector class (520 lines)
│  ├─ __init__ (10 lines)
│  ├─ check_url (50 lines) - Orchestrator
│  ├─ Supporting methods (30 lines)
│  ├─ 10x Detection methods (400 lines)
│  └─ Blacklist methods (30 lines)
└─ Flask routes (60 lines)
   ├─ @app.route('/') - Home
   ├─ @app.route('/check') - API
   └─ @app.route('/add-to-blacklist') - Persist

templates/index.html (600 lines)
├─ HTML structure (200 lines)
├─ CSS styling (300 lines)
└─ JavaScript (100 lines)

Static files
├─ blacklist.txt - Persistent data
└─ requirements.txt - Dependencies
```

---

## 13. Design Decisions & Rationale

### Why Class-Based?
```
✅ Encapsulation: State (blacklist) isolated
✅ Reusability: Can instantiate multiple detectors
✅ Maintenance: Organized, expandable
✅ Testing: Easy to mock and test
```

### Why No Hardcoding?
```
✅ Flexibility: Works on ANY domain
✅ Scalability: No manual maintenance
✅ Accuracy: Pattern-based, not keyword-based
✅ Academic Value: Shows algorithm design
```

### Why Scoring System (0-100)?
```
✅ Intuitive: Users understand percentages
✅ Granular: Multiple risk levels (30%, 60%, 90%)
✅ Flexible: Can adjust thresholds easily
✅ Visual: Maps to colors (Red orange, Yellow, Green)
```

---

## Summary

This architecture provides:
- **Modularity**: Independent detection methods
- **Extensibility**: Easy to add new checks
- **Robustness**: Error handling throughout
- **Transparency**: Clear logic flow
- **Performance**: Optimized for interactive use
- **Security**: Input validation and safe APIs
- **Maintainability**: Clean code organization

The system is designed for educational purposes while maintaining production-quality code practices.

