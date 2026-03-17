from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import urlparse
import ssl
import socket
from datetime import datetime
import json
import os

app = Flask(__name__)

# Load blacklist from file
BLACKLIST_FILE = 'blacklist.txt'

def load_blacklist():
    """Load blacklist URLs from file"""
    blacklist = set()
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                for line in f:
                    url = line.strip()
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        blacklist.add(url.lower())
        except Exception as e:
            print(f"Error loading blacklist: {e}")
    return blacklist

def save_to_blacklist(url):
    """Add URL to blacklist file"""
    try:
        with open(BLACKLIST_FILE, 'a') as f:
            f.write(url.lower() + '\n')
        return True
    except Exception as e:
        print(f"Error saving to blacklist: {e}")
        return False

class URLFraudDetector:
    def __init__(self):
        self.fraud_score = 0
        self.details = []
        
    def check_url(self, url):
        """Main function to check URL safety"""
        self.fraud_score = 0
        self.details = []
        
        # Validate URL format
        if not self.is_valid_url(url):
            self.details.append(("Invalid URL Format", "90", "URL does not follow proper format"))
            self.fraud_score = 90
            return self.fraud_score, self.details
        
        # Check if domain/IP actually exists
        if not self.domain_exists(url):
            self.fraud_score = 100
            self.details.append(("Invalid URL", "100", "This is not a valid URL - domain/IP does not exist"))
            return self.fraud_score, self.details
        
        # Run all checks
        self.check_blacklist(url)
        self.check_typosquatting(url)
        self.check_suspicious_subdomains(url)
        self.check_phishtank(url)
        self.check_ssl_certificate(url)
        self.check_certificate_mismatch(url)
        self.check_html_content(url)
        self.check_domain_age(url)
        self.check_url_patterns(url)
        self.check_suspicious_keywords(url)
        
        return self.fraud_score, self.details
    
    def is_valid_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def domain_exists(self, url):
        """Check if domain/IP actually exists and is reachable"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").split(":")[0]  # Remove port
            
            # Try to resolve domain
            ip = socket.gethostbyname(domain)
            
            # Also try to connect to verify it's actually reachable
            try:
                # Try HTTP/HTTPS port
                port = 443 if parsed.scheme == 'https' else 80
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((domain, port))
                sock.close()
                
                # If connection succeeds (result == 0), domain is reachable
                return result == 0
            except:
                # If connection attempt fails, domain doesn't exist
                return False
        except (socket.gaierror, socket.error, ValueError):
            return False
    
    def check_blacklist(self, url):
        """Check against local blacklist and URLhaus"""
        # Check local blacklist first
        blacklist = load_blacklist()
        if url.lower() in blacklist:
            threat_score = 50
            self.fraud_score += threat_score
            self.details.append((
                "Blacklist Database",
                threat_score,
                "URL found in local blacklist"
            ))
            return
        
        try:
            # Check URLhaus API (free, no key required)
            response = requests.get(
                f"https://urlhaus-api.abuse.ch/v1/url/",
                params={"url": url},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("query_status") == "ok" and data.get("url_info"):
                    threat_score = 40
                    self.fraud_score += threat_score
                    self.details.append((
                        "Blacklist Database",
                        threat_score,
                        f"URL found in abuse database: {data['url_info'].get('threat_type', 'malware')}"
                    ))
        except Exception as e:
            self.details.append(("Blacklist Check", "0", "Could not verify - connection error"))
    
    def check_ssl_certificate(self, url):
        """Check SSL certificate validity"""
        try:
            parsed = urlparse(url)
            netloc = parsed.netloc.replace("www.", "")
            
            # Extract domain/IP and port
            if ":" in netloc:
                domain = netloc.split(":")[0]
                try:
                    port = int(netloc.split(":")[1])
                except (ValueError, IndexError):
                    port = 443
            else:
                domain = netloc
                port = 443
            
            # For HTTPS URLs, check appropriate port
            if parsed.scheme == 'https' and port == 443:
                ssl_port = 443
            else:
                ssl_port = port
            
            # Try to get SSL certificate
            context = ssl.create_default_context()
            
            try:
                with socket.create_connection((domain, ssl_port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        if cert:
                            # Certificate found and valid
                            try:
                                # Certificate date format: 'Mar 16 00:00:00 2027 GMT'
                                notAfter = cert.get('notAfter', '')
                                expiry = datetime.strptime(notAfter, "%b %d %H:%M:%S %Y %Z")
                                
                                if expiry < datetime.now():
                                    self.fraud_score += 35
                                    self.details.append(("SSL Certificate", "35", "Certificate expired"))
                                else:
                                    self.details.append(("SSL Certificate", "0", "Valid SSL certificate found"))
                            except ValueError:
                                # If date parsing fails, certificate exists at least
                                self.details.append(("SSL Certificate", "0", "Valid SSL certificate found"))
                        else:
                            self.fraud_score += 25
                            self.details.append(("SSL Certificate", "25", "No SSL certificate found"))
            except ssl.SSLCertVerificationError:
                # Self-signed certificate - still valid but not trusted
                self.fraud_score += 15
                self.details.append(("SSL Certificate", "15", "Self-signed certificate (not from trusted CA)"))
            except (socket.timeout):
                self.fraud_score += 10
                self.details.append(("SSL Certificate", "10", f"Connection timeout on port {ssl_port}"))
            except (socket.gaierror):
                self.fraud_score += 15
                self.details.append(("SSL Certificate", "15", "Domain/IP could not be reached"))
            except ssl.SSLError as e:
                self.fraud_score += 20
                self.details.append(("SSL Certificate", "20", f"SSL error - {str(e)[:50]}"))
            except Exception as e:
                self.fraud_score += 10
                self.details.append(("SSL Certificate", "10", f"Could not verify SSL"))
                
        except Exception as e:
            self.details.append(("SSL Check", "0", f"Could not verify SSL"))
    
    def check_domain_age(self, url):
        """Check domain age using WHOIS data"""
        try:
            # Domain already validated in check_url, so we can skip this
            self.details.append(("Domain Validation", "0", "Domain exists and is reachable"))
                
        except Exception as e:
            self.details.append(("Domain Check", "0", "Could not verify domain"))
    
    def check_url_patterns(self, url):
        """Check for suspicious URL patterns"""
        threat_indicators = 0
        reasons = []
        
        # Check for IP address instead of domain
        if urlparse(url).netloc.replace("www.", "").split(":")[0].count(".") >= 3:
            try:
                parts = urlparse(url).netloc.split(":")[0].split(".")
                if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                    threat_indicators += 20
                    reasons.append("Uses IP address instead of domain")
            except:
                pass
        
        # Check for suspicious port numbers
        if ":" in urlparse(url).netloc:
            port = urlparse(url).netloc.split(":")[1]
            if port in ["8080", "8888", "9999", "1234"]:
                threat_indicators += 15
                reasons.append(f"Suspicious port number: {port}")
        
        # Check for too many subdomains
        domain = urlparse(url).netloc.replace("www.", "")
        if domain.count(".") > 3:
            threat_indicators += 10
            reasons.append("Too many subdomains (suspicious)")
        
        if threat_indicators > 0:
            self.fraud_score += threat_indicators
            self.details.append(("URL Pattern Analysis", threat_indicators, "; ".join(reasons)))
        else:
            self.details.append(("URL Pattern Analysis", "0", "Normal URL structure"))
    
    def check_suspicious_keywords(self, url):
        """Check for suspicious patterns in URL"""
        suspicious_patterns = [
            "login", "verify", "confirm", "update", "validate", "alert",
            "secure", "admin", "bank", "crypto", "wallet", "claim", "reward", "urgent"
        ]
        
        url_lower = url.lower()
        found_keywords = [word for word in suspicious_patterns if word in url_lower]
        
        # Single keywords are not highly suspicious, but multiple are
        threat_score = len(found_keywords) * 5
        threat_score = min(threat_score, 20)  # Cap at 20
        
        if threat_score > 0:
            self.fraud_score += threat_score
            self.details.append((
                "Suspicious Keywords",
                threat_score,
                f"Found patterns: {', '.join(found_keywords[:3])}"
            ))
    
    def check_typosquatting(self, url):
        """Detect typosquatting based on suspicious patterns"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").lower()
        main_domain = domain.split(".")[0]  # Get just the domain name without TLD
        
        threat_score = 0
        
        # Pattern 1: Domain name + only numbers (e.g., facebook2, google123)
        # Any word followed by digits is suspicious
        if main_domain and len(main_domain) > 2:
            # Find where numbers start
            alpha_part = ""
            num_part = ""
            for char in main_domain:
                if char.isalpha() or char in "-_":
                    alpha_part += char
                elif char.isdigit():
                    num_part += char
                else:
                    break
            
            # If we have word part + number part, it's suspicious
            if alpha_part and num_part and len(num_part) >= 1:
                threat_score += 30
                self.details.append((
                    "Typosquatting Detection",
                    30,
                    f"Domain name with numeric suffix '{num_part}' - common phishing technique"
                ))
                return
        
        # Pattern 2: Common character substitutions (0->o, 1->i/l, 3->e, etc.)
        # Check if domain looks like it has character substitutions
        suspicious_chars = {'0', '1', '3', '4', '5', '7', '8', '9'}
        char_count = sum(1 for c in main_domain if c in suspicious_chars)
        
        # If domain has multiple numeric characters mixed with letters, suspicious
        if char_count >= 1 and len(main_domain) > 3:
            # Normalize and check if it becomes a real word-like pattern
            normalized = main_domain
            substitutions = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '9': 'g'}
            for num, letter in substitutions.items():
                normalized = normalized.replace(num, letter)
            
            # If normalized version has way fewer abnormal characters
            norm_suspicious = sum(1 for c in normalized if c in suspicious_chars)
            if norm_suspicious < char_count:
                threat_score += 25
                self.details.append((
                    "Typosquatting Detection",
                    25,
                    f"Domain '{domain}' contains suspicious character substitutions"
                ))
                return
        
        # Pattern 3: Excessive hyphens or underscores (used to bypass filters)
        separator_count = main_domain.count('-') + main_domain.count('_')
        if separator_count >= 2:
            threat_score += 20
            self.details.append((
                "Typosquatting Detection",
                20,
                f"Domain has excessive separators (hyphens/underscores) - potential phishing"
            ))
            return
        
        if threat_score == 0:
            self.details.append(("Typosquatting Detection", "0", "No typosquatting patterns detected"))
    
    def check_suspicious_subdomains(self, url):
        """Check for suspicious subdomain patterns"""
        parsed = urlparse(url)
        netloc = parsed.netloc.replace("www.", "").lower()
        parts = netloc.split(".")
        
        # Pattern 1: High number of subdomains (more than 3 dots = 4+ parts)
        subdomain_parts = parts[:-1]  # All except TLD
        if len(subdomain_parts) > 2:
            threat_score = 15
            self.details.append((
                "Suspicious Subdomains",
                threat_score,
                f"Excessive subdomains ({len(subdomain_parts)}) - unusual structure"
            ))
            self.fraud_score += threat_score
            return
        
        # Pattern 2: Very short subdomain (single letter) before main domain
        for part in subdomain_parts:
            if len(part) == 1 and part.isalpha():
                threat_score = 10
                self.details.append((
                    "Suspicious Subdomains",
                    threat_score,
                    f"Single-letter subdomain '{part}' - possibly masking real domain"
                ))
                self.fraud_score += threat_score
                return
        
        self.details.append(("Suspicious Subdomains", "0", "Subdomain structure appears normal"))
    
    def check_phishtank(self, url):
        """Check against PhishTank database for known phishing URLs"""
        try:
            response = requests.post(
                "https://checkurl.phishtank.com/checkurl/",
                data={"url": url, "format": "json"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("meta", {}).get("status") == "ok":
                    result = data.get("results", {})
                    if result.get("in_database"):
                        self.fraud_score += 50
                        self.details.append((
                            "PhishTank Database",
                            50,
                            f"URL found in PhishTank phishing database"
                        ))
                    else:
                        self.details.append(("PhishTank Database", "0", "Not in PhishTank database"))
                else:
                    self.details.append(("PhishTank Check", "0", "Could not verify - service unavailable"))
        except Exception as e:
            self.details.append(("PhishTank Check", "0", "Could not verify - connection error"))
    
    def check_certificate_mismatch(self, url):
        """Check if SSL certificate domain matches the requested domain"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "").split(":")[0].lower()
            
            # Only check for HTTPS
            if parsed.scheme != 'https':
                self.details.append(("Certificate Mismatch", "0", "Not HTTPS - skipped"))
                return
            
            context = ssl.create_default_context()
            try:
                with socket.create_connection((domain, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        if cert:
                            # Get Subject Alternative Names (SANs)
                            sans = []
                            for san in cert.get('subjectAltName', []):
                                if san[0] == 'DNS':
                                    sans.append(san[1].lower())
                            
                            # Also get the common name
                            cn = None
                            for rdn in cert.get('subject', ()):
                                for name_type, name_value in rdn:
                                    if name_type == 'commonName':
                                        cn = name_value.lower()
                            
                            all_names = sans + ([cn] if cn else [])
                            
                            # Check if domain matches
                            cert_matches = False
                            for name in all_names:
                                # Handle wildcard certificates
                                if name.startswith('*.'):
                                    wildcard_domain = name[2:]
                                    if domain.endswith(wildcard_domain):
                                        cert_matches = True
                                        break
                                elif name == domain or domain.endswith('.' + name):
                                    cert_matches = True
                                    break
                            
                            if not cert_matches:
                                self.fraud_score += 40
                                self.details.append((
                                    "Certificate Mismatch",
                                    40,
                                    f"SSL cert doesn't match domain - potential MITM attack"
                                ))
                            else:
                                self.details.append(("Certificate Mismatch", "0", "Certificate matches domain"))
            except Exception as e:
                self.details.append(("Certificate Mismatch", "0", "Could not validate certificate"))
        except Exception as e:
            self.details.append(("Certificate Check", "0", "Could not verify certificate mismatch"))
    
    def check_html_content(self, url):
        """Scan HTML content for phishing indicators"""
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            
            if response.status_code == 200:
                html = response.text.lower()
                threat_score = 0
                indicators = []
                
                # Pattern 1: Suspicious action words combined with forms
                action_words = ["confirm", "verify", "validate", "update", "urgent", "click", "immediate"]
                has_action_word = any(word in html for word in action_words)
                
                if has_action_word and '<form' in html and ('password' in html or 'login' in html):
                    threat_score += 25
                    indicators.append("Form with suspicious action language")
                
                # Pattern 2: JavaScript redirects
                if 'window.location' in html or 'location.href' in html or '.redirect' in html:
                    threat_score += 20
                    indicators.append("JavaScript redirect/location change detected")
                
                # Pattern 3: Meta refresh (auto-redirect)
                if '<meta' in html and 'refresh' in html:
                    threat_score += 15
                    indicators.append("Automatic page refresh/redirect detected")
                
                # Pattern 4: Excessive scripts (relative to content)
                script_count = html.count('<script')
                form_count = html.count('<form')
                # If way more scripts than forms, suspicious
                if script_count > 15 and form_count == 0:
                    threat_score += 10
                    indicators.append(f"Excessive scripts without forms ({script_count})")
                
                if threat_score > 0:
                    self.fraud_score += min(threat_score, 35)
                    self.details.append((
                        "HTML Content Analysis",
                        min(threat_score, 35),
                        "; ".join(indicators[:2])  # Show first 2 indicators
                    ))
                else:
                    self.details.append(("HTML Content Analysis", "0", "No phishing indicators detected"))
        except requests.exceptions.RequestException:
            self.details.append(("HTML Content", "0", "Could not scan HTML content"))
        except Exception as e:
            self.details.append(("HTML Content", "0", "Error scanning content"))
    
    def get_final_score(self):
        """Return capped final score"""
        return min(self.fraud_score, 100)


detector = URLFraudDetector()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_url():
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please enter a URL'}), 400
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    fraud_score, details = detector.check_url(url)
    final_score = detector.get_final_score()
    
    # Determine risk level
    if final_score >= 70:
        risk_level = "🔴 HIGHLY SUSPICIOUS"
    elif final_score >= 50:
        risk_level = "🟠 SUSPICIOUS"
    elif final_score >= 30:
        risk_level = "🟡 MODERATE RISK"
    else:
        risk_level = "🟢 LEGITIMATE"
    
    return jsonify({
        'url': url,
        'fraud_percentage': final_score,
        'risk_level': risk_level,
        'details': [
            {
                'check': detail[0],
                'score': detail[1],
                'message': detail[2]
            }
            for detail in details
        ]
    })


@app.route('/add-to-blacklist', methods=['POST'])
def add_to_blacklist():
    """Add a URL to the blacklist"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Check if already in blacklist
    blacklist = load_blacklist()
    if url.lower() in blacklist:
        return jsonify({'error': 'URL already in blacklist'}), 400
    
    # Add to blacklist
    if save_to_blacklist(url):
        return jsonify({'success': True, 'message': f'URL added to blacklist'}), 200
    else:
        return jsonify({'error': 'Failed to add URL to blacklist'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
