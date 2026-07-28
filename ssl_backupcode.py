#     def check_ssl(self, domain=None):
#         """Comprehensive SSL certificate analyzer with export options"""
#         try:
           
#             if not domain:
#                 domain = input("Enter domain to check (e.g., starkexpo.com): ").strip()
#                 if not domain:
#                     print("[!] No domain provided")
#                     return
        
#             print(f"\n[+] Analyzing SSL certificate for {domain}...")
        
#         # Configure enhanced SSL context
#             context = ssl.create_default_context()
#             context.check_hostname = True
#             context.verify_mode = ssl.CERT_REQUIRED
#             context.load_default_certs()
        
#         # Set timeout and create connection
#             socket.setdefaulttimeout(10)
        
#             with socket.create_connection((domain, 443)) as sock:
#                 with context.wrap_socket(sock, server_hostname=domain) as ssock:
#                     cert = ssock.getpeercert(binary_form=True)
#                     x509 = ssl.DER_cert_to_PEM_cert(cert)
#                     cert_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, x509)
                
#                 # Get certificate details
#                     peer_cert = ssock.getpeercert()
#                     issuer = dict(x[0] for x in peer_cert['issuer'])
#                     subject = dict(x[0] for x in peer_cert['subject'])
#                     expires = datetime.strptime(peer_cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
#                     valid_days = (expires - datetime.now()).days
                
#                 # Get certificate chain using OpenSSL
#                     chain = []
#                     store = OpenSSL.crypto.X509Store()
#                     store_ctx = OpenSSL.crypto.X509StoreContext(store, cert_obj)
                
#                     try:
#                         chain_result = store_ctx.get_verified_chain()
#                         for i, chain_cert in enumerate(chain_result):
#                             chain.append({
#                                 'subject': dict(chain_cert.get_subject().get_components()),
#                                 'issuer': dict(chain_cert.get_issuer().get_components()),
#                                 'expires': chain_cert.get_notAfter().decode('utf-8'),
#                                 'serial': chain_cert.get_serial_number(),
#                                 'version': chain_cert.get_version() + 1
#                             })
#                     except OpenSSL.crypto.X509StoreContextError:
#                         chain.append({
#                             'subject': dict(cert_obj.get_subject().get_components()),
#                             'issuer': dict(cert_obj.get_issuer().get_components()),
#                             'expires': cert_obj.get_notAfter().decode('utf-8'),
#                             'serial': cert_obj.get_serial_number(),
#                             'version': cert_obj.get_version() + 1
#                         })
                
#                 # Check OCSP revocation status
#                     ocsp_status = "Unknown"
#                     if len(chain) > 1:
#                         ocsp_status = self._check_ocsp(cert_obj, chain[1])
                
#                 # Print comprehensive report
#                     self._print_ssl_report(domain, ssock, cert_obj, chain, ocsp_status, valid_days)
    
#         except ssl.SSLError as e:
#             print(f"[!] SSL Error: {e}")
#         except socket.timeout:
#             print("[!] Connection timed out")
#         except ImportError as e:
#             print(f"[!] Required module missing: {str(e)}")
#             print("[!] Please install pyOpenSSL: pip install pyopenssl")
#         except Exception as e:
#             print(f"[!] Analysis failed: {str(e)}")
 
#     def _cinematic_box(self, title, seconds=3):
#         """Display a centered colored box with progress and flickering messages"""
#         terminal_width = shutil.get_terminal_size((80, 20)).columns
#         box_width = min(60, terminal_width - 10)  # keep margins

#     # Random colors
#         colors = [Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW]
#         color = random.choice(colors)

#     # Top border
#         print("\n" + color + "+" + "═" * box_width + "+" + Style.RESET_ALL)
#         print(color + "│" + title.center(box_width) + "│" + Style.RESET_ALL)
#         print(color + "+" + "─" * box_width + "+" + Style.RESET_ALL)

#         spinner = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
#         flickers = ["[Scanning...]", "[TLS Check]", "[OCSP Query]", "[Certificate Verify]", "[Risk Assessment]"]
#         end_time = time.time() + seconds
#         i = 0

#         while time.time() < end_time:
#             progress = int(((time.time() % seconds) / seconds) * box_width)
#             bar = "█" * progress + "-" * (box_width - progress)
#             flicker_text = random.choice(flickers).ljust(box_width)
#             sys.stdout.write(f"\r{color}│{spinner[i%len(spinner)]} {bar[:box_width-2]} {Style.BRIGHT}{flicker_text[:box_width-4]}{Style.RESET_ALL}{color}│{Style.RESET_ALL}")
#             sys.stdout.flush()
#             time.sleep(0.1)
#             i += 1

#     # Bottom border
#         sys.stdout.write(f"\r{color}│{' ' * box_width}│{Style.RESET_ALL}\n")
#         print(color + "+" + "═" * box_width + "+" + Style.RESET_ALL)
#         sys.stdout.flush()
# # ---------- Example usage in your certcheck sequence ----------
#     def _animated_ssl_scan(self):
#         stages = [
#             "Initializing SSL Inspection Engine",
#             "Analyzing TLS Handshake",
#             "Validating Certificate Chain",
#             "Mapping Trust Relationships",
#             "Running Risk Assessment Engine",
#             "Generating Defense Recommendations"
#         ]

#         for stage in stages:
#             self._cinematic_box(stage, seconds=4)  # adjust duration per stage
#             time.sleep(0.5)  # slight pause before next stage

#     # After stages, print certificate info table
#         self._animated_ssl_table() 
#         # new method for blinking colored table
# # =============table============
#     def _animated_ssl_table(self):
#         """Display certificate info in colored, blinking table"""
#         terminal_width = shutil.get_terminal_size((80, 20)).columns
#         table_width = min(70, terminal_width - 10)
#         cert_data = [
#             ["Domain", "unima.ac.mw"],
#             ["Issuer", "R13"],
#             ["Expires", "20260404 (27 days)"],
#             ["Protocol", "TLSv1.2"],
#             ["Cipher", "ECDHE-RSA-AES256-GCM-SHA384"],
#             ["Signature", "sha256WithRSAEncryption"],
#             ["OCSP Status", "Unknown"],
#             ["Risk Level", "HIGH"]
#         ]

#         colors = [Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW]

#         print("\n" + Fore.BLUE + "╔" + "═"*table_width + "╗" + Style.RESET_ALL)
#         print(Fore.BLUE + f"║ {'DSTerminal SSL/TLS Security Audit'.center(table_width)} ║" + Style.RESET_ALL)
#         print(Fore.BLUE + "╠" + "═"*table_width + "╣" + Style.RESET_ALL)

#         for row in cert_data:
#             k, v = row
#             color = random.choice(colors)
#             blink = "\033[5m"  # ANSI blink
#             print(Fore.BLUE + "║ " + Style.RESET_ALL + f"{color}{blink}{k:<15}{Style.RESET_ALL}: {v:<{table_width-20}}" + Fore.BLUE + " ║" + Style.RESET_ALL)
#             time.sleep(0.05)

#         print(Fore.BLUE + "╚" + "═"*table_width + "╝" + Style.RESET_ALL)

#     def _print_ssl_report(self, domain, ssock, cert_obj, chain, ocsp_status, valid_days):

#     # Stage 1: Initialization
#         self._loading_animation("Initializing SSL Inspection Engine", 10)

#     # Stage 2: Handshake Analysis
#         self._loading_animation("Analyzing TLS Handshake", 10)

#     # Stage 3: Certificate Validation
#         self._loading_animation("Validating Certificate Chain", 10)

#         protocol = ssock.version()
#         cipher = ssock.cipher()[0]
#         sig_algo = cert_obj.get_signature_algorithm().decode()

#         tls13_supported = protocol == "TLSv1.3"
#         renewal_warning = valid_days < 60

#     # Basic Info
#         print("\n╔" + "═"*70 + "╗")
#         print(f"║ {'DSTerminal SSL/TLS Security Audit':^68} ║")
#         print("╠" + "═"*70 + "╣")

#         print(f"║ {'Domain:':<20} {domain:<46} ║")
#         print(f"║ {'Issuer:':<20} {cert_obj.get_issuer().CN:<46} ║")
#         print(f"║ {'Subject:':<20} {cert_obj.get_subject().CN:<46} ║")
#         print(f"║ {'Expires:':<20} {cert_obj.get_notAfter().decode()} ({valid_days} days) ║")
#         print(f"║ {'Protocol:':<20} {protocol:<46} ║")
#         print(f"║ {'Cipher:':<20} {cipher:<46} ║")
#         print(f"║ {'Signature:':<20} {sig_algo:<46} ║")
#         print(f"║ {'OCSP Status:':<20} {ocsp_status:<46} ║")

#         print("╚" + "═"*70 + "╝")

#     # Stage 4: Chain Mapping
#         self._loading_animation("Mapping Trust Relationships", 10)

#         print("\n[ Certificate Chain ]")

#         for i, cert in enumerate(chain):
#             print(f"{'  '*i}└─ {cert['subject'].get(b'CN', b'Unknown').decode()}")
#             if i == 0:
#                 print(f"    Issuer: {cert['issuer'].get(b'CN', b'Unknown').decode()}")
#                 print(f"    Valid Until: {cert['expires']}")

#     # Stage 5: Risk Engine
#         self._loading_animation("Running Risk Assessment Engine", 10)

#         print("\n[ Security Assessment ]")

#         risk = 0

#         if renewal_warning:
#             print("[!] Certificate renewal required soon")
#             risk += 2

#         if "SHA1" in sig_algo:
#             print("[!] Weak signature algorithm (SHA-1)")
#             risk += 3

#         if protocol in ["TLSv1", "TLSv1.1"]:
#             print("[!] Deprecated TLS protocol")
#             risk += 4

#         if not tls13_supported:
#             print("[!] TLS 1.3 not enabled")
#             risk += 1

#         if ocsp_status != "VALID":
#             print("[!] OCSP revocation not verified")
#             risk += 2

#         if risk == 0:
#             level = "LOW"
#         elif risk <= 3:
#             level = "MEDIUM"
#         elif risk <= 6:
#             level = "HIGH"
#         else:
#             level = "CRITICAL"

#         print(f"\n[✓] Overall Risk Level: {level}")

#         # Build report data
#         data = {
#             "subject": cert_obj.get_subject().CN,
#             "valid_days": valid_days,
#             "protocol": ssock.version(),
#             "cipher": ssock.cipher()[0],
#             "ocsp": ocsp_status,
#             "risk_level": level,
#             "renewal_warning": renewal_warning,
#             "tls13": ssock.version() == "TLSv1.3",
#             "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

#         # Certificate info
#         "certificate": {
#             "subject": {"CN": cert_obj.get_subject().CN},
#             "issuer": {"CN": cert_obj.get_issuer().CN},
#             "expires": cert_obj.get_notAfter().decode(),
#             "serial": str(cert_obj.get_serial_number()),
#             "signature": cert_obj.get_signature_algorithm().decode()
#         },

#         "security_profile": {
#             "tls13": ssock.version() == "TLSv1.3",
#             "ocsp": ocsp_status,
#             "forward_secrecy": "ECDHE" in ssock.cipher()[0]
#         }
#     }


#     # Stage 6: Defensive Recommendations
#         self._loading_animation("Generating Defense Recommendations", 10)

#         print("\n[ Recommendations ]")

#         if renewal_warning:
#             print("→ Renew SSL certificate immediately")

#         if not tls13_supported:
#             print("→ Upgrade server to support TLS 1.3")

#         if ocsp_status != "VALID":
#             print("→ Enable OCSP stapling")

#         if risk == 0:
#             print("→ No action required. System secure.")

#     # Stage 7: Export Prompt
#         choice = input("\nExport security report to file? (y/N): ").lower()

#         if choice == "y":
#             self._export_ssl_results(domain, ssock, cert_obj, chain)
            
#         pdf_choice = input("Generate PDF compliance report? (y/N): ").lower()

#         if pdf_choice == "y":
#             self._generate_pdf_report(data)

#     def _check_ocsp(self, cert, issuer_cert):
#         """Check OCSP revocation status"""
#         try:
#             from cryptography.x509.oid import ExtensionOID
#             from cryptography.hazmat.backends import default_backend
#             from cryptography.x509 import load_pem_x509_certificate
            
#             cert = load_pem_x509_certificate(
#                 OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
#             )
        
#             if issuer_cert:
#                 issuer = load_pem_x509_certificate(
#                     OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, issuer_cert)
#                 )
#                 builder = OCSPRequestBuilder()
#                 builder = builder.add_certificate(cert, issuer)
#                 req = builder.build()
            
#                 ocsp_url = cert.extensions.get_extension_for_class(
#                     cryptography.x509.AuthorityInformationAccess
#                 ).value.get_ocsp_urls()[0]
            
#                 response = requests.post(
#                     ocsp_url,
#                     data=req.public_bytes(serialization.Encoding.DER),
#                     headers={'Content-Type': 'application/ocsp-request'}
#                 )
            
#                 return "REVOKED" if response.status == 1 else "VALID"
#         except:
#             return "Unknown"

#     def _export_ssl_results(self, domain, ssock, cert_obj, chain):

#         subject = self._bytes_to_str_dict(
#             dict(cert_obj.get_subject().get_components())
#         )

#         issuer = self._bytes_to_str_dict(
#             dict(cert_obj.get_issuer().get_components())
#         )

#         data = {
#             "domain": domain,
#             "scan_time": datetime.now().isoformat(),

#             "protocol": ssock.version(),
#             "cipher": ssock.cipher()[0],

#             "certificate": {
#                 "subject": subject,
#                 "issuer": issuer,
#                 "expires": cert_obj.get_notAfter().decode(),
#                 "serial": str(cert_obj.get_serial_number()),
#                 "signature": cert_obj.get_signature_algorithm().decode()
#             },

#             "chain": self._clean_chain(chain),

#             "security_profile": {
#                 "tls13": ssock.version() == "TLSv1.3",
#                 "ocsp": "checked",
#                 "forward_secrecy": "ECDHE" in ssock.cipher()[0]
#             }
#         }

#         filename = f"dsterminal_ssl_{domain}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

#         with open(filename, "w") as f:
#             json.dump(data, f, indent=2)

#         print(f"\n[✓] Encrypted audit report saved: {filename}")

#     def _bytes_to_str_dict(self, data):
#         """Convert bytes dictionary to string dictionary"""

#         clean = {}

#         for k, v in data.items():

#             if isinstance(k, bytes):
#                 k = k.decode()

#             if isinstance(v, bytes):
#                 v = v.decode()

#             clean[k] = v

#         return clean

#     # string bytes conversions===============
#     def _clean_chain(self, chain):
#         """Convert certificate chain bytes to strings"""

#         cleaned = []

#         for cert in chain:

#             new_cert = {}

#             for k, v in cert.items():

#             # Decode key
#                 if isinstance(k, bytes):
#                     k = k.decode()

#             # Decode value
#                 if isinstance(v, bytes):
#                     v = v.decode()

#             # If value is dict (nested)
#                 if isinstance(v, dict):

#                     temp = {}

#                     for kk, vv in v.items():

#                         if isinstance(kk, bytes):
#                             kk = kk.decode()

#                         if isinstance(vv, bytes):
#                             vv = vv.decode()

#                         temp[kk] = vv

#                     v = temp

#                 new_cert[k] = v

#             cleaned.append(new_cert)

#         return cleaned

#     def _generate_pdf_report(self, data, logo_path="icon.jpg", footer_logo_path="icon.jpg"):
#     # Safely get all keys with defaults
#         domain = data.get("domain", "unknown_domain")
#         certificate = data.get("certificate", {})
#         security_profile = data.get("security_profile", {})
#         scan_time = data.get("scan_time", datetime.now().strftime('%Y-%m-%d %H:%M'))
#         protocol = data.get("protocol", "N/A")
#         cipher = data.get("cipher", "N/A")

#         subject = certificate.get("subject", {}).get("CN", "N/A")
#         issuer = certificate.get("issuer", {}).get("CN", "N/A")
#         expires = certificate.get("expires", "N/A")
#         serial = certificate.get("serial", "N/A")
#         signature = certificate.get("signature", "N/A")

#         tls13 = security_profile.get("tls13", False)
#         ocsp = security_profile.get("ocsp", "N/A")
#         forward_secrecy = security_profile.get("forward_secrecy", False)

#         filename = f"dsterminal_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

#         doc = SimpleDocTemplate(
#             filename,
#             pagesize=A4,
#             rightMargin=40,
#             leftMargin=40,
#             topMargin=40,
#             bottomMargin=40
#         )

#         page_width, page_height = A4
#         styles = getSampleStyleSheet()
#         elements = []

#             # -------- Top Logo (auto-scaled, centered) --------
#         if os.path.exists(logo_path):
#             logo = Image(logo_path)
#             max_width = page_width - doc.leftMargin - doc.rightMargin
#             if logo.imageWidth > max_width:
#                 scale_ratio = max_width / logo.imageWidth
#                 logo.drawWidth = logo.imageWidth * scale_ratio
#                 logo.drawHeight = logo.imageHeight * scale_ratio
#             logo.hAlign = 'CENTER'
#             elements.append(logo)
#             elements.append(Spacer(1, 20))

#     # Title
#         title_style = ParagraphStyle("TitleStyle", fontSize=22, alignment=1, spaceAfter=20, bold=True)
#         section_style = ParagraphStyle("SectionStyle", fontSize=14, spaceBefore=20, spaceAfter=10, bold=True)
#         normal = styles["Normal"]

#         elements.append(Paragraph("DSTerminal Security Compliance Report", title_style))
#         elements.append(Paragraph(f"Generated: {scan_time}", normal))
#         elements.append(Spacer(1, 20))

#     # System Info
#         elements.append(Paragraph("System Information", section_style))
#         sys_table = [
#             ["Domain", domain],
#             ["Protocol", protocol],
#             ["Cipher", cipher],
#             ["Scan Time", scan_time]
#         ]
#         elements.append(self._styled_table(sys_table))

#     # Certificate Info
#         elements.append(Paragraph("Certificate Details", section_style))
#         cert_table = [
#             ["Subject", subject],
#             ["Issuer", issuer],
#             ["Expiry", expires],
#             ["Serial", serial],
#             ["Signature", signature]
#         ]
#         elements.append(self._styled_table(cert_table))

#     # Security Profile
#         elements.append(Paragraph("Security Profile", section_style))
#         sec_table = [
#             ["TLS 1.3 Enabled", str(tls13)],
#             ["OCSP Checked", ocsp],
#             ["Forward Secrecy", str(forward_secrecy)]
#         ]
#         elements.append(self._styled_table(sec_table))

#     # Recommendations
#         elements.append(Paragraph("Recommendations", section_style))
#         recs = self._build_recommendations(data)
#         for rec in recs:
#             elements.append(Paragraph(f"• {rec}", normal))
#             elements.append(Spacer(1, 5))

#     # Footer
#         elements.append(Spacer(1, 40))
#         footer_data = []

#             # Footer logo
#         if os.path.exists(footer_logo_path):
#             footer_logo = Image(footer_logo_path)
#             max_footer_width = 50  # small logo width
#             scale_ratio = max_footer_width / footer_logo.imageWidth
#             footer_logo.drawWidth = footer_logo.imageWidth * scale_ratio
#             footer_logo.drawHeight = footer_logo.imageHeight * scale_ratio
#             footer_data.append([footer_logo, Paragraph("AUTOGENERATED CERTIFICATE REPORT | DSTerminal Platform\n© Stark Expo Tech Exchange", normal)])
#             footer_table = Table(footer_data, colWidths=[60, page_width - 60 - doc.leftMargin - doc.rightMargin])
#             footer_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
#             elements.append(footer_table)
#         else:
#         # fallback if logo missing
#             elements.append(Paragraph("AUTOGENERATED REPORT | DSTerminal Platform", normal))
#             elements.append(Paragraph("© Stark Expo Tech Exchange LTD", normal))

   
#         doc.build(elements)
#         print(f"\n[✓] PDF Compliance Report Created: {filename}")

#     def _styled_table(self, data):

#         table = Table(data, colWidths=[180, 320])

#         style = TableStyle([
#             ("BACKGROUND", (0, 0), (-1, 0), lightgrey),
#             ("GRID", (0, 0), (-1, -1), 0.5, black),
#             ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("ALIGN", (0, 0), (0, -1), "LEFT"),
#             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#             ("PADDING", (0, 0), (-1, -1), 6),
#         ])

#         table.setStyle(style)

#         return table

#     def _build_recommendations(self, data):

#         recs = []

#         cert = data["certificate"]
#         sec = data["security_profile"]

#     # Expiry check
#         expires = datetime.strptime(cert["expires"][:8], "%Y%m%d")
#         days_left = (expires - datetime.utcnow()).days

#         if days_left < 60:
#             recs.append("Renew SSL certificate within 30 days")

#         if not sec["tls13"]:
#             recs.append("Upgrade server configuration to support TLS 1.3")

#         if sec["ocsp"] != "VALID":
#             recs.append("Enable OCSP stapling for revocation validation")

#         if sec["forward_secrecy"] is False:
#             recs.append("Enable Perfect Forward Secrecy (ECDHE)")

#         if not recs:
#             recs.append("No critical risks detected. Maintain current security posture.")

#         return recs
# # added animated effects for the ssl certificate checks================
#     def _type_print(self, text, delay=0.02):
#         """Cinematic typing effect"""
#         for char in text:
#             sys.stdout.write(char)
#             sys.stdout.flush()
#             time.sleep(delay)
#         print()

#     def _loading_animation(self, text, seconds=5):
#         """Cinematic hacking-style animated loader with glitch and progress effects"""
#     # Print main stage text centered
#         terminal_width = 80
#         print("\n" + text.center(terminal_width))
    
#         spinner = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
#         end_time = time.time() + seconds
#         i = 0

#     # Build cinematic random messages
#         flickers = [
#             "[ACCESSING CERT DATA]", "[TLS HANDSHAKE INIT]", "[VALIDATING CHAIN]",
#             "[OCSP CHECK]", "[ASSESSING RISK]", "[GENERATING RECOMMENDATIONS]",
#             "[ANALYZING PROTOCOL]", "[CIPHER SCAN]", "[SIGNATURE VERIFY]"
#         ]

#         while time.time() < end_time:
#         # Glitchy flicker text
#             flicker_text = random.choice(flickers)
        
#         # Animated spinner + sliding progress
#             bar_length = 30
#             progress = int(((time.time() % seconds) / seconds) * bar_length)
#             bar = "█" * progress + "-" * (bar_length - progress)

#         # Random colors
#             color = random.choice([Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW])
#             sys.stdout.write(f"\r{color}{spinner[i % len(spinner)]} {bar} {flicker_text.center(40)}{Style.RESET_ALL}")
#             sys.stdout.flush()
#             time.sleep(0.1)
#             i += 1

#     # Finish with a completed checkmark
#         sys.stdout.write(f"\r{Fore.GREEN}[✓] {text} Completed{' ' * 40}{Style.RESET_ALL}\n")
#         sys.stdout.flush()
