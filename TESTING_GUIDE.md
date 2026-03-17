# 🧪 Testing & Validation Guide

**URL Fraud Detection System - Comprehensive Test Suite**

---

## Quick Start Tests

### Minimal Viable Test Set (5 min)

Run these to verify system is working:

```
1. google.com               → Expected: 0-15% (Legitimate)
2. facebook2.com            → Expected: 30-50% (Typosquatting)
3. phishing-example.com     → Expected: 50-80% (Suspicious)
4. fake-paypal.net          → Expected: 70-100% (Blacklist)
5. bobob123.com             → Expected: 100% (Invalid domain)
```

Expected Time: 5-10 seconds per URL = ~1 minute total

**Quick Assessment**:
- ✅ All scores within ranges → System working
- ❌ Scores outside ranges → Debug specific modules

---

## Comprehensive Test Suite

### Category A: Legitimate Websites

| URL | Expected Risk | Reasoning |
|-----|------|-----------|
| `google.com` | 0-10% | Top-tier company, valid SSL, well-known |
| `amazon.com` | 0-10% | Major retailer, real cert, legitimate |
| `github.com` | 0-10% | Developer platform, secure |
| `wikipedia.org` | 0-10% | Non-profit, no commerce, safe |
| `bbc.com` | 0-10% | News org, established, trustworthy |

**Test Results**:
```
Domain         | Risk | Blacklist | SSL | Domain Valid | Verdict
google.com     | 0%   | ✅ Pass   | ✅  | ✅          | ✅ PASS
amazon.com     | 3%   | ✅ Pass   | ✅  | ✅          | ✅ PASS
github.com     | 2%   | ✅ Pass   | ✅  | ✅          | ✅ PASS
```

**Assessment Criteria**:
- ✅ PASS: Risk < 20%, all checks green
- ⚠️  CAUTION: Risk 20-40%, investigate
- ❌ FAIL: Risk > 40%, shouldn't be flagged as legitimate

---

### Category B: Typosquatting & Misspellings

**Test Cases**:

| Attack Type | Example | Expected Risk | Detection Method |
|-------------|---------|------|------|
| Numeric suffix | `facebook2.com` | 35-50% | Numeric suffix check |
| Character substitution | `g00gle.com` | 40-55% | Char replace (0→o) |
| Double letter | `amazom.com` | 25-40% | Levenshtein distance |
| Separator injection | `face-book.com` | 30-45% | Excessive hyphens |
| Homograph (Latin-Cyrillic) | `рGoogle.com` | 60-80% | Visual analysis |

**Test Execution**:

```
Test: google2.com
Fields to Check:
- Typosquatting Score: Check > 20 points
- Detection Type: Should list "Numeric Suffix"
- Pattern: Should show "google" + "2"

Expected Output:
{
  "typosquatting": 25,
  "has_numeric": true,
  "pattern": "Brand + numeric suffix"
}
```

---

### Category C: Suspicious Subdomains

| URL | Risk | Reason |
|-----|------|--------|
| `mail.google.com` | 5-10% | Legitimate Google service |
| `login.fake-bank.com` | 60-80% | Action word + fake domain |
| `verify.security.amazon.fake` | 85-95% | Trust words buried, fake TLD |
| `a.b.c.d.e.f.com` | 40-60% | Too many subdomain levels |
| `x.y.amazon-login.com` | 75-90% | Single-letter subdomains + brand + action word |

**Scoring Analysis**:

```
Subdomain Depth Analysis:
- 1 level (example.com): 0 points
- 2 levels (sub.example.com): 0-5 points (legitimate)
- 3 levels (a.b.example.com): 10-20 points (suspicious)
- 4+ levels: 30+ points (very suspicious)

Single-Letter Analysis:
- Contains single letters: +15 points (obfuscation)
- Pattern like "a.b.c.domain": +25 points (hiding domain)
```

---

### Category D: SSL Certificate Tests

**HTTPS Validation**:

| URL | Has HTTPS? | Cert Valid? | Cert Match? | Expected Risk |
|-----|---|---|---|---|
| `https://google.com` | ✅ | ✅ | ✅ | <10% |
| `https://self-signed.example.com` | ✅ | ⚠️ Self-signed | ⚠️ Mismatch possible | 30-50% |
| `http://gmail.com` | ❌ | N/A | N/A | 20-30% |
| `https://fake-bank.fake` | ✅ | ⚠️ Let's Encrypt | ✅ Matches | 50%+ (Invalid domain) |

**Certificate Inspection Code**:

```python
# What the system checks:
1. Certificate present?
2. Certificate valid (not expired)?
3. Certificate CN/SAN matches domain?
4. Certificate chain valid?
5. Trust chain to root CA?

# Example checks:
google.com → Cert CN="google.com" ✅
amazon.com → Cert SAN includes amazon.com ✅
attacker.com → Cert CN="attacker.com" (valid cert, wrong domain) ⚠️
```

---

### Category E: HTML Content Analysis

**Phishing Form Patterns**:

| Pattern | Risk | Example |
|---------|------|---------|
| Form + password field | 10-15 pts | `<input type="password">` |
| Form + action word | 20-25 pts | `Verify`, `Confirm` |
| Form + redirect script | 30-40 pts | `window.location=...` |
| Meta refresh | 15-20 pts | `<meta http-equiv="refresh">` |
| Excessive scripts | 10-15 pts | `<script>` tags |

**Test Examples**:

```html
<!-- Legitimate (0-5 points) -->
<form action="https://gmail.com/login" method="post">
  <input type="email" placeholder="Email">
  <input type="password" placeholder="Password">
  <button>Sign in</button>
</form>

<!-- Phishing (40-60 points) -->
<form action="http://fake-gmail.attacker.com">
  <p>VERIFY YOUR ACCOUNT IMMEDIATELY</p>
  <input type="password">
  <button>Confirm Account</button>
  <script>document.location='http://attacker.com'</script>
</form>
```

---

### Category F: Invalid/Unreachable Domains

| URL | DNS Resolves? | TCP Connects? | Risk | Reasoning |
|-----|---|---|---|---|
| `google.com` | ✅ | ✅ | <10% | Valid |
| `fake-nonexistent-domain.com` | ❌ | N/A | 100% | Invalid |
| `localhost:8080` | ✅ | ✅ | Depends | Depends on server |
| `192.168.1.1` | ✅ | ✅ | High | IP address, not domain |

**Socket Connection Test**:

```python
# System attempts:
import socket

domain = "google.com"
try:
    socket.create_connection((domain, 80), timeout=5)
    print("Domain is reachable")
except socket.error:
    print("Domain does NOT exist or is unreachable")
    # Mark as invalid → +100 points
```

---

### Category G: PhishTank & Blacklist Integration

| URL | In PhishTank? | In Local Blacklist? | Expected Risk |
|-----|---|---|---|
| `phishing-example.com` | Maybe | ✅ Yes | 60-100% |
| `fake-paypal.net` | Maybe | ✅ Yes | 70-100% |
| Recently detected phishing | ✅ Yes | ❌ No | 50-80% |
| User-added URL | ❌ | ✅ Yes (after adding) | 50+ |

**Blacklist Test Workflow**:

```
Step 1: Check new URL (malicious-site.com)
  Result: ~40-60% risk

Step 2: Click "Add to Blacklist"
  Result: blacklist.txt updated

Step 3: Check malicious-site.com again
  Result: jumps to 60-100% risk (blacklist hit)

Step 4: Verify blacklist.txt
  malicious-site.com appears in file
```

---

## Test Execution Report

### Test Environment

```
Device: [Windows/Mac/Linux]
Browser: [Chrome/Firefox/Safari]
Flask Server: [Running at localhost:5000]
Python: [Version 3.8+]
Date: [DD/MM/YYYY]
Tester: [Your Name]
```

### Test Results Table

```
# Test Case | URL | Expected | Actual | Status | Notes
1. Simple legitimate | google.com | 0-10% | 3% | ✅ PASS | 
2. Typosquatting | google2.com | 30-50% | 42% | ✅ PASS |
3. Blacklist | phishing-example.com | 70-100% | 85% | ✅ PASS |
4. Invalid domain | fake-nonexistent.com | 100% | 100% | ✅ PASS |
5. SSL valid | amazon.com | 0-10% | 5% | ✅ PASS |
...
Total: 50 ✅ PASS, 2 ⚠️ REVIEW, 0 ❌ FAIL
```

---

## Performance Testing

### Speed Benchmarks

| Test Type | Expected Time | Acceptable Range |
|-----------|---|---|
| Simple URL | <1 second | <2 seconds |
| Full analysis | 2-5 seconds | <10 seconds |
| Blacklist check | <0.5 sec | <1 second |
| PhishTank API | 1-3 seconds | <5 seconds (depends on API) |
| Batch (10 URLs) | 20-50 sec | <60 seconds |

**Performance Test Script**:

```python
import time
import requests

urls = ["google.com", "facebook2.com", "phishing-example.com"]

for url in urls:
    start = time.time()
    response = requests.post("http://localhost:5000/check", 
                             json={"url": url})
    elapsed = time.time() - start
    print(f"{url}: {elapsed:.2f}s")
```

---

## Regression Testing

### Before Code Updates

```
1. Run full test suite
2. Document all scores
3. Save baseline.json
```

### After Code Updates

```
1. Run same test suite
2. Compare scores
3. Check for regressions (score differences > 10%)
4. Investigate unexpected changes
```

**Regression Checklist**:

```
After modifying check_typosquatting():
- [ ] google2.com still ~35-45% (no change)
- [ ] g00gle.com still ~40-50% (no change)
- [ ] google.com still <10% (no change)
- [ ] New patterns work correctly

After modifying HTML content check:
- [ ] Legitimate forms: <20% (no increase)
- [ ] Phishing forms: >50% (correct detection)
- [ ] facebook.com: Still <10% (not flagged)
```

---

## Edge Case Testing

### Unusual Inputs

| Input | Expected Behavior | Status |
|-------|------|-----|
| Empty string | Error message | ? |
| `example` (no TLD) | Invalid | ? |
| `http://example.com:8080` | Parse port | ? |
| `example.com:99999` | Invalid port | ? |
| `user:pass@example.com` | Parse credentials | ? |
| Unicode domain | Detect | ? |
| Very long domain | Parse | ? |
| Internationalized domain | Handle | ? |

---

## Accessibility Testing

- [ ] Keyboard navigation (Tab through form)
- [ ] Screen reader compatibility
- [ ] Color contrast (WCAG AA standard)
- [ ] Mobile responsiveness (test on phone)
- [ ] Animation performance (no lag)
- [ ] Error messages clear and helpful

---

## Security Testing

- [ ] Input validation (prevents SQL injection)
- [ ] XSS prevention (escapes user input)
- [ ] CSRF protection (if applicable)
- [ ] Rate limiting (prevents abuse)
- [ ] Information disclosure (no sensitive data in errors)
- [ ] SSL/TLS (uses HTTPS in production)

---

## Final Validation Checklist

### Functionality
- [ ] Check button works
- [ ] Results display correctly
- [ ] Risk colors accurate (Green/Yellow/Orange/Red)
- [ ] Blacklist button functional
- [ ] Add to blacklist works
- [ ] Animations smooth
- [ ] Responsive on mobile

### Accuracy
- [ ] Legitimate sites: <20% risk
- [ ] Phishing sites: >60% risk
- [ ] Invalid domains: 100% risk
- [ ] No false negatives (missing obvious phishing)
- [ ] Acceptable false positives (<10%)

### Performance
- [ ] Load time <3 seconds
- [ ] Responsive UI (no freezing)
- [ ] API calls complete in <5 sec
- [ ] Handles multiple requests

### Documentation
- [ ] README.md complete
- [ ] Code commented
- [ ] Error messages clear
- [ ] Lab guide included
- [ ] This testing guide complete

---

## Test Failure Troubleshooting

### Problem: All URLs show 0%

**Diagnosis**:
```python
# Check if domain_exists() is working
import socket
socket.create_connection(("google.com", 80), timeout=5)  # Should not error
```

**Solution**: Check internet connection, firewall rules

---

### Problem: Legitimate sites flagged as phishing (>50%)

**Diagnosis**:
```python
# Check which method is adding points
# Review: check_html_content(), check_suspicious_keywords()
```

**Solution**: Fine-tune thresholds, update patterns

---

### Problem: Flask server crashes

**Diagnosis**:
```
Check error logs:
1. Syntax errors: python -m py_compile app.py
2. Import errors: Check requirements.txt
3. Runtime errors: Check console output
```

**Solution**: Fix syntax, install missing packages

---

## Sign-Off

**Tested By**: ________________  
**Date**: ________________  
**Test Coverage**: ____%  
**Pass Rate**: ____%  
**Overall Assessment**: [ ] Approved [ ] Needs Fixes [ ] Rejected  

**Comments**:

