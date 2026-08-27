#!python
"""
DSTERMINAL License Agreement PDF Generator
Clean, professional legal document with no background colors
"""

import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

# Version constant
VERSION = "4.0.0.113"

class DSTERMINALEULAGenerator:
    """Generate professional EULA PDF with clean formatting"""
    
    def __init__(self):
        self.output_dir = "licenses"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_pdf(self):
        """Generate the professional EULA PDF with clean formatting"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"DSTERMINAL_EULA_v{VERSION}_{timestamp}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title="DSTERMINAL End User License Agreement",
            author="Stark Expo Tech Exchange"
        )
        
        # Styles - No background colors, clean black/white/gray
        styles = getSampleStyleSheet()
        
        # Main Title Style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle Style
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=25,
            fontName='Helvetica'
        )
        
        # Section Heading Style
        section_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#003366'),
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        # Subsection Heading Style
        subsection_style = ParagraphStyle(
            'SubsectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#004488'),
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        # Body Text Style
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            fontName='Helvetica',
            leading=14
        )
        
        # Important/Warning Text Style
        warning_style = ParagraphStyle(
            'WarningText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#cc0000'),
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Highlighted text style
        highlight_style = ParagraphStyle(
            'HighlightText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#006600'),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            fontName='Helvetica',
            leading=14,
            leftIndent=20
        )
        
        # Footer Style
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        # Load logo
        logo_img = None
        logo_paths = [
            "installer_assets/3486-removebg-preview.ico",
            "../installer_assets/3486-removebg-preview.ico",
            "icon-removebg-preview.ico"
        ]
        
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    pil_img = PILImage.open(logo_path)
                    pil_img = pil_img.resize((70, 70), PILImage.Resampling.LANCZOS)
                    if pil_img.mode in ('RGBA', 'LA', 'P'):
                        background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                        if pil_img.mode == 'RGBA':
                            background.paste(pil_img, mask=pil_img.split()[-1])
                        else:
                            background.paste(pil_img)
                        pil_img = background
                    
                    temp_logo = os.path.join(self.output_dir, "temp_logo.png")
                    pil_img.save(temp_logo, "PNG")
                    logo_img = Image(temp_logo, width=60, height=60)
                    break
                except Exception as e:
                    print(f"âš ï¸ Logo load warning: {e}")
                    continue
        
        # Build story
        story = []
        
        # Add logo
        if logo_img:
            logo_table = Table([[logo_img]], colWidths=[450], rowHeights=[80])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(logo_table)
            story.append(Spacer(1, 5))
        
        # Title
        story.append(Paragraph("DSTERMINAL - Defensive Security Terminal", title_style))
        story.append(Paragraph("Cyber-Ops Platform", title_style))
        story.append(Paragraph("End User License Agreement (EULA)", subtitle_style))
        story.append(Paragraph(f"Version v{VERSION} | Last Updated: {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
        story.append(Spacer(1, 15))
        
        # Divider
        story.append(Paragraph("-" * 80, styles['Normal']))
        story.append(Spacer(1, 15))
        
        # IMPORTANT NOTICE
        notice_text = """
        <b>IMPORTANT NOTICE</b><br/>
        <br/>
        PLEASE READ THIS END USER LICENSE AGREEMENT CAREFULLY BEFORE 
        INSTALLING OR USING DSTERMINAL SOFTWARE.<br/>
        <br/>
        THIS IS A LEGAL AGREEMENT BETWEEN YOU (EITHER AN INDIVIDUAL OR A SINGLE 
        ENTITY) AND STARK EXPO TECH EXCHANGE ("LICENSOR") FOR THE DSTERMINAL 
        SOFTWARE PRODUCT ("SOFTWARE").<br/>
        <br/>
        <b>BY INSTALLING, COPYING, OR OTHERWISE USING THE SOFTWARE, YOU AGREE TO BE 
        BOUND BY THE TERMS OF THIS AGREEMENT. IF YOU DO NOT AGREE TO THE TERMS OF 
        THIS AGREEMENT, DO NOT INSTALL OR USE THE SOFTWARE.</b>
        """
        story.append(Paragraph(notice_text, warning_style))
        story.append(Spacer(1, 15))
        
        # ============================================================
        # SECTIONS 1-13
        # ============================================================
        
        sections = [
            ("1. GRANT OF LICENSE", [
                "1.1 Commercial License. Licensor grants you a non-exclusive, non-transferable, non-sublicensable license to install and use the Software for internal business purposes only, subject to the payment of applicable subscription fees.",
                "1.2 Evaluation License. A limited evaluation license may be available for a specified trial period. During this period, the Software may have limited functionality or contain a time restriction.",
                "1.3 Authorized Users. Only licensed users within your organization may access and use the Software. Each user must have their own license credential."
            ]),
            ("2. RESTRICTIONS", [
                "2.1 You may NOT:",
                "   a) Reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code of the Software;",
                "   b) Modify, adapt, translate, or create derivative works based on the Software;",
                "   c) Rent, lease, lend, sell, sublicense, assign, distribute, or otherwise transfer the Software or any rights therein;",
                "   d) Remove, alter, or obscure any proprietary notices, labels, or marks from the Software;",
                "   e) Use the Software for competitive analysis or to develop competing products;",
                "   f) Use the Software in any manner that violates applicable laws or regulations, including unauthorized security testing;",
                "   g) Share license credentials or allow unauthorized access to the Software.",
                "2.2 The Software is licensed as a single product. Its component parts may not be separated for use on more than one device or by more than one user."
            ]),
            ("3. INTELLECTUAL PROPERTY RIGHTS", [
                "3.1 Ownership. The Software is licensed, not sold. Licensor retains all right, title, and interest in and to the Software, including all intellectual property rights therein.",
                "3.2 Confidentiality. The Software constitutes trade secrets and confidential information of Licensor.",
                "3.3 Audit Rights. Licensor reserves the right to audit your use of the Software to ensure compliance with this Agreement, upon reasonable notice."
            ]),
            ("4. SUBSCRIPTION AND FEES", [
                "4.1 Subscription Required. Access to and use of the Software requires an active subscription agreement.",
                "4.2 Fee Changes. Licensor reserves the right to change subscription fees upon 30 days' written notice.",
                "4.3 Non-Payment. Licensor may suspend or terminate access to the Software immediately if subscription fees are not paid when due."
            ]),
            ("5. NO WARRANTY", [
                "5.1 THE SOFTWARE IS PROVIDED \"AS IS\" AND \"AS AVAILABLE\" WITHOUT WARRANTY OF ANY KIND.",
                "5.2 LICENSOR DOES NOT WARRANT THAT THE SOFTWARE WILL BE ERROR-FREE OR FREE OF VULNERABILITIES.",
                "5.3 YOU ASSUME ALL RISKS ASSOCIATED WITH THE USE OF THE SOFTWARE."
            ]),
            ("6. LIMITATION OF LIABILITY", [
                "TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY SPECIAL, INCIDENTAL, INDIRECT, OR CONSEQUENTIAL DAMAGES WHATSOEVER. IN ANY CASE, LICENSOR'S ENTIRE LIABILITY SHALL BE LIMITED TO THE AMOUNT ACTUALLY PAID BY YOU FOR THE SOFTWARE DURING THE TWELVE (12) MONTHS PRECEDING THE CLAIM."
            ]),
            ("7. TERM AND TERMINATION", [
                "7.1 Term. This Agreement is effective upon your acceptance and continues until terminated.",
                "7.2 Termination for Breach. Licensor may terminate this Agreement immediately if you fail to comply.",
                "7.3 Termination without Cause. Either party may terminate this Agreement for any reason upon 30 days' written notice.",
                "7.4 Effect of Termination. Upon termination, you must immediately cease all use of the Software and destroy all copies."
            ]),
            ("8. COMPLIANCE WITH LAWS", [
                "You agree to use the Software only for lawful purposes and in compliance with all applicable laws and regulations, including but not limited to:",
                "   a) Computer Fraud and Abuse Act (CFAA) and similar state laws;",
                "   b) Data protection and privacy laws (including GDPR, CCPA, etc.);",
                "   c) Export control laws and regulations."
            ]),
            ("9. AUTHORIZED USE ONLY", [
                "The Software is designed for:",
                "   a) Authorized security assessments and penetration testing;",
                "   b) Internal network monitoring and security auditing;",
                "   c) Compliance and regulatory testing.",
                "",
                "You represent and warrant that you have proper authorization to test any systems or networks you scan using the Software."
            ]),
            ("10. GOVERNING LAW", [
                "This Agreement shall be governed by and construed in accordance with the laws of the Republic of Malawi. Any legal action or proceeding arising under this Agreement shall be brought exclusively in the courts located in Lilongwe, Malawi."
            ]),
            ("11. ENTIRE AGREEMENT", [
                "This Agreement constitutes the entire agreement between the parties concerning the subject matter hereof."
            ]),
            ("12. SEVERABILITY", [
                "If any provision of this Agreement is held to be unenforceable or invalid, the remaining provisions shall continue in full force and effect."
            ]),
            ("13. CONTACT INFORMATION", [
                "For license inquiries, support, or to report violations of this Agreement:",
                "",
                "Stark Expo Tech Exchange",
                "Contact (s): [+265] 993 076 724 / 886 283 247",
                "Email: licensing@starkexpotechexchange-mw.com",
                "Website: https://www.starkexpotechexchange-mw.com"
            ])
        ]
        
        for section_title, content_list in sections:
            story.append(Paragraph(section_title, section_style))
            for content in content_list:
                if content.strip():
                    story.append(Paragraph(content, body_style))
            story.append(Spacer(1, 8))
        
        # Page break before signature page
        story.append(PageBreak())
        
        # ============================================================
        # SIGNATURE PAGE
        # ============================================================
        
        story.append(Paragraph("ACKNOWLEDGMENT AND AGREEMENT", section_style))
        story.append(Spacer(1, 10))
        
        ack_text = """
        This Agreement is entered into by and between the following parties:<br/>
        <br/>
        <b>LICENSOR (Grantor of License):</b> Stark Expo Tech Exchange<br/>
        <b>LICENSEE (Recipient of License):</b> The undersigned organization/individual<br/>
        <br/>
        BY SIGNING BELOW, BOTH PARTIES ACKNOWLEDGE THAT THEY HAVE READ THIS AGREEMENT, 
        UNDERSTAND IT, AND AGREE TO BE BOUND BY ITS TERMS AND CONDITIONS.
        """
        story.append(Paragraph(ack_text, body_style))
        story.append(Spacer(1, 30))
        
        # LICENSOR SECTION
        story.append(Paragraph("PART A: LICENSOR (Stark Expo Tech Exchange)", subsection_style))
        story.append(Spacer(1, 10))
        
        licensor_sig_data = [
            ["Licensor:", "Stark Expo Tech Exchange", ""],
            ["Authorized Representative:", "_________________________", ""],
            ["Title:", "_________________________", ""],
            ["Date:", "_________________________", ""],
            ["Signature:", "_________________________", ""],
        ]
        
        licensor_table = Table(licensor_sig_data, colWidths=[150, 200, 100])
        licensor_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(licensor_table)
        story.append(Spacer(1, 30))
        
        # LICENSEE SECTION
        story.append(Paragraph("PART B: LICENSEE (Customer/Organization)", subsection_style))
        story.append(Spacer(1, 10))
        
        licensee_sig_data = [
            ["Organization Name:", "_________________________", ""],
            ["Organization Type:", "â–¡ Enterprise  â–¡ Education  â–¡ Government  â–¡ Individual", ""],
            ["License ID:", "_________________________", ""],
            ["Number of Users:", "_________", ""],
            ["Authorized Representative:", "_________________________", ""],
            ["Title/Position:", "_________________________", ""],
            ["Date:", "_________________________", ""],
            ["Signature:", "_________________________", ""],
        ]
        
        licensee_table = Table(licensee_sig_data, colWidths=[150, 200, 100])
        licensee_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(licensee_table)
        story.append(Spacer(1, 30))
        
        # WITNESS SECTION
        story.append(Paragraph("WITNESS (Optional)", subsection_style))
        story.append(Spacer(1, 10))
        
        witness_data = [
            ["Witness Name:", "_________________________", ""],
            ["Witness Signature:", "_________________________", ""],
            ["Date:", "_________________________", ""],
        ]
        
        witness_table = Table(witness_data, colWidths=[150, 200, 100])
        witness_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        story.append(witness_table)
        story.append(Spacer(1, 30))
        
        # Copyright notice
        copyright_text = f"""
        Â© {datetime.now().year} Stark Expo Tech Exchange. All Rights Reserved.<br/>
        DSTERMINAL is a trademark of Stark Expo Tech Exchange.<br/>
        Unauthorized reproduction or distribution of this document is prohibited.<br/>
        <br/>
        Document ID: DSTERMINAL-EULA-{datetime.now().strftime('%Y%m%d')}-001<br/>
        Printed On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        Version: {VERSION}
        """
        story.append(Paragraph(copyright_text, footer_style))
        
        # Watermark function (light, not intrusive)
        def add_watermark(canvas_obj, doc):
            canvas_obj.saveState()
            page_width, page_height = A4
            center_x = page_width / 2
            center_y = page_height / 2
            
            canvas_obj.setFont('Helvetica', 40)
            canvas_obj.setFillColor(colors.lightgrey)
            canvas_obj.setFillAlpha(0.15)
            canvas_obj.saveState()
            canvas_obj.translate(center_x, center_y)
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, "CONFIDENTIAL")
            canvas_obj.restoreState()
            
            canvas_obj.setFont('Helvetica', 8)
            canvas_obj.setFillAlpha(0.5)
            canvas_obj.setFillColor(colors.gray)
            canvas_obj.drawCentredString(center_x, 20, f"Page {doc.page} | DSTERMINAL EULA v{VERSION}")
            canvas_obj.restoreState()
        
        # Build PDF
        doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
        
        # Clean up
        temp_logo = os.path.join(self.output_dir, "temp_logo.png")
        if os.path.exists(temp_logo):
            try:
                os.remove(temp_logo)
            except:
                pass
        
        print(f"\nâœ… License Agreement Generated Successfully!")
        print(f"ðŸ“„ File: {pdf_path}")
        print(f"ðŸ“… Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return pdf_path


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("   DSTERMINAL License Agreement PDF Generator")
    print("   Clean Professional Legal Document")
    print("="*60 + "\n")
    
    generator = DSTERMINALEULAGenerator()
    pdf_path = generator.create_pdf()
    
    print("\n" + "="*60)
    print("   Generation Complete!")
    print("="*60)
    
    try:
        import webbrowser
        open_pdf = input("\nðŸ“„ Open PDF file? (y/n): ").strip().lower()
        if open_pdf == 'y':
            webbrowser.open(f"file://{pdf_path}")
            print("âœ… PDF opened")
    except KeyboardInterrupt:
        print("\n\nâœ… PDF generated successfully!")
    except Exception as e:
        print(f"\nâš ï¸ Could not open PDF: {e}")
        print(f"ðŸ“„ File location: {pdf_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nâš ï¸ Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nâŒ Error: {e}")
        sys.exit(1)