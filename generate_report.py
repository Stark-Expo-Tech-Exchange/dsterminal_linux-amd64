#!/usr/bin/env python3
"""
DSTERMINAL Report Generator
Generates a well-formatted DOC file for the NCST Technical Progress Report
"""

import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def create_report():
    """Create the DSTERMINAL Technical Progress Report"""
    
    # Create document
    doc = Document()
    
    # Set margins
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
    
    # ============================================================
    # TITLE PAGE
    # ============================================================
    
    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("DSTERMINAL PROJECT")
    run.bold = True
    run.font.size = Pt(22)
    run.font.name = 'Arial'
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("Technical Progress and Grant Utilization Report")
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = 'Arial'
    
    doc.add_paragraph()
    
    # Project Info
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run("Project Title: DSTerminal (Defensive Security Terminal)").bold = True
    doc.add_paragraph()
    info2 = doc.add_paragraph()
    info2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info2.add_run("Report Period: June â€“ July 2026").bold = True
    doc.add_paragraph()
    info3 = doc.add_paragraph()
    info3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info3.add_run("Submitted To: The Director General, NCST").bold = True
    doc.add_paragraph()
    info4 = doc.add_paragraph()
    info4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info4.add_run("Submitted By: Spark Wilson Spink - Project Lead").bold = True
    doc.add_paragraph()
    info5 = doc.add_paragraph()
    info5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info5.add_run("Contact: (+265) 993 076 724 / 886 283 247").bold = True
    
    doc.add_page_break()
    
    # ============================================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ============================================================
    
    h1 = doc.add_heading("1. EXECUTIVE SUMMARY", level=1)
    
    p = doc.add_paragraph()
    p.add_run("This report provides an update on the DSTerminal Project's progress following grant support from NCST.")
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("DSTerminal v4.0.0.113 has been successfully developed, packaged, and branded. The software is now at Pre-Release stage with 85% core development completion. The project has utilized MWK 3,135,000 of the total MWK 5,000,000 grant, leaving a balance of MWK 1,865,000.")
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Current Status:").bold = True
    
    status_items = [
        "Software packaging and branding complete",
        "Production-ready installers available (Windows and Linux)",
        "All 9 core security modules operational",
        "Internal testing: 90% complete",
        "External pilot testing: Not yet started",
        "Commercialization: Not yet started"
    ]
    
    for item in status_items:
        p = doc.add_paragraph(item, style='List Bullet')
    
    # ============================================================
    # SECTION 2: PROJECT STATUS SUMMARY
    # ============================================================
    
    doc.add_page_break()
    h2 = doc.add_heading("2. PROJECT STATUS SUMMARY", level=1)
    
    table = doc.add_table(rows=8, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Indicator"
    headers[1].text = "Status"
    headers[2].text = "Progress"
    
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    data = [
        ("Grant Received", "Yes â€“ 100%", "âœ“"),
        ("Software Development", "85% Complete", "â†‘"),
        ("Internal Testing", "90% Complete", "â†‘"),
        ("Software Packaging", "Complete", "âœ“"),
        ("Equipment Procurement", "85% Complete", "â†‘"),
        ("External Pilot Testing", "0%", "âœ—"),
        ("Commercialization", "0%", "âœ—")
    ]
    
    for i, row_data in enumerate(data):
        row = table.rows[i + 1]
        row.cells[0].text = row_data[0]
        row.cells[1].text = row_data[1]
        row.cells[2].text = row_data[2]
    
    # ============================================================
    # SECTION 3: TECHNICAL ACHIEVEMENTS
    # ============================================================
    
    doc.add_page_break()
    h3 = doc.add_heading("3. TECHNICAL ACHIEVEMENTS", level=1)
    
    doc.add_heading("3.1 Software Modules Completed", level=2)
    
    table = doc.add_table(rows=10, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Module"
    headers[1].text = "Status"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    modules = [
        ("VirusTotal Scanner", "âœ“"),
        ("Network Reconnaissance", "âœ“"),
        ("Web Security Analyzer", "âœ“"),
        ("Encryption Engine", "âœ“"),
        ("SQLMap Integration", "âœ“"),
        ("Wi-Fi Auditor", "âœ“"),
        ("System Hardening", "âœ“"),
        ("Digital Forensics", "âœ“"),
        ("SSL/TLS Scanner", "âœ“")
    ]
    
    for i, module_data in enumerate(modules):
        row = table.rows[i + 1]
        row.cells[0].text = module_data[0]
        row.cells[1].text = module_data[1]
    
    doc.add_heading("3.2 Packaging and Branding Completed", level=2)
    
    packaging_items = [
        "Windows Installer (304 MB) with all dependencies",
        "Portable ZIP version (255 MB)",
        "Linux server compatibility",
        "User documentation and command reference",
        "Professional branding with NCST acknowledgment"
    ]
    
    for item in packaging_items:
        p = doc.add_paragraph(item, style='List Bullet')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Both Licensed and Non-Licensed DSTerminal installers have been packaged and branded, ready for pilot testing deployment.").bold = True
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("The DSTerminal installer is dependency-aware with all required libraries bundled. It does not require internet access during installation and does not need external dependencies to be installed or configured by users.").italic = True
    
    # ============================================================
    # SECTION 4: EQUIPMENT PROCUREMENT
    # ============================================================
    
    doc.add_page_break()
    h4 = doc.add_heading("4. EQUIPMENT PROCUREMENT", level=1)
    
    table = doc.add_table(rows=10, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Item"
    headers[1].text = "Cost (MWK)"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    equipment = [
        ("Desktop Workstation", "1,250,000"),
        ("HP Laptop (Testing)", "750,000"),
        ("Airtel ODU Router", "425,000"),
        ("External HDD (1TB)", "70,000"),
        ("Packaging and Branding", "320,000"),
        ("API Integration and Patching", "300,000"),
        ("Transportation", "20,000"),
        ("Total Spent", "3,135,000"),
        ("Remaining Balance", "1,865,000")
    ]
    
    for i, eq_data in enumerate(equipment):
        row = table.rows[i + 1]
        row.cells[0].text = eq_data[0]
        row.cells[1].text = eq_data[1]
        if "Total" in eq_data[0] or "Remaining" in eq_data[0]:
            for cell in row.cells:
                cell.paragraphs[0].runs[0].bold = True
    
    # ============================================================
    # SECTION 5: CHALLENGES AND FUNDING SHORTFALL
    # ============================================================
    
    doc.add_page_break()
    h5 = doc.add_heading("5. CHALLENGES AND FUNDING SHORTFALL", level=1)
    
    doc.add_heading("5.1 Key Challenges", level=2)
    
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Challenge"
    headers[1].text = "Impact"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    challenges = [
        ("Rising Equipment Costs", "Reduced purchasing power, delayed some planned procurements"),
        ("High External Testing Costs", "Pilot testing requires infrastructure, personnel, and logistics"),
        ("Continuous Development Needs", "Bug fixes, security updates, and feature enhancements require ongoing resources")
    ]
    
    for i, ch_data in enumerate(challenges):
        row = table.rows[i + 1]
        row.cells[0].text = ch_data[0]
        row.cells[1].text = ch_data[1]
    
    doc.add_heading("5.2 Critical Funding Shortfall", level=2)
    
    p = doc.add_paragraph()
    p.add_run("The remaining MWK 1,865,000 is insufficient to cover all planned activities and critical requirements needed to complete the project successfully:")
    
    table = doc.add_table(rows=13, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Activity"
    headers[1].text = "Estimated Cost (MWK)"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    funding_items = [
        ("External Beta Testing Program", "800,000"),
        ("Pilot Deployment at Institutions", "600,000"),
        ("Security Audits and Penetration Testing", "700,000"),
        ("Training Content and Workshops", "500,000"),
        ("Legal and IP Registration", "400,000"),
        ("Continuous Development Support", "500,000"),
        ("Marketing and Commercialization", "500,000"),
        ("Monitoring and Evaluation", "200,000"),
        ("Contingency", "300,000"),
        ("Total Required", "4,500,000"),
        ("Available Balance", "1,865,000"),
        ("Shortfall", "2,635,000")
    ]
    
    for i, fund_data in enumerate(funding_items):
        row = table.rows[i + 1]
        row.cells[0].text = fund_data[0]
        row.cells[1].text = fund_data[1]
        if "Total" in fund_data[0] or "Available" in fund_data[0] or "Shortfall" in fund_data[0]:
            for cell in row.cells:
                cell.paragraphs[0].runs[0].bold = True
    
    # ============================================================
    # SECTION 6: FUTURE ACTIVITIES
    # ============================================================
    
    doc.add_page_break()
    h6 = doc.add_heading("6. FUTURE ACTIVITIES", level=1)
    
    doc.add_heading("6.1 Activities Requiring Additional Funding", level=2)
    
    p = doc.add_paragraph()
    p.add_run("The following activities cannot be completed with the remaining funds and require additional financial support:")
    
    table = doc.add_table(rows=9, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Activity"
    headers[1].text = "Cost (MWK)"
    headers[2].text = "Justification"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    future_items = [
        ("External Beta Testing", "800,000", "Essential to validate software stability and gather user feedback before public release. Includes tester incentives, platform costs, and logistics."),
        ("Pilot Deployment", "600,000", "Deploy software at partner institutions to demonstrate real-world application and provide case studies necessary for commercialization."),
        ("Security Audits and Penetration Testing", "700,000", "Critical to validate the security claims of the software, identify vulnerabilities, and build trust with potential users."),
        ("Legal and IP Registration", "400,000", "Necessary to protect intellectual property rights, enabling future commercialization and sustainability."),
        ("Marketing and Commercialization", "500,000", "Essential for market entry, business model development, and achieving project sustainability beyond the grant period."),
        ("Training Content and Workshops", "500,000", "Enables end-user adoption, builds community of practice, and supports technology transfer."),
        ("Monitoring and Evaluation", "200,000", "Required to measure project impact, track outcomes, and provide accountability to NCST."),
        ("Total Additional Funding Requested", "4,500,000", "")
    ]
    
    for i, item_data in enumerate(future_items):
        row = table.rows[i + 1]
        row.cells[0].text = item_data[0]
        row.cells[1].text = item_data[1]
        row.cells[2].text = item_data[2]
        if "Total" in item_data[0]:
            for cell in row.cells:
                cell.paragraphs[0].runs[0].bold = True
    
    doc.add_heading("6.2 Planned Activities with Remaining Funds (MWK 1,865,000)", level=2)
    
    table = doc.add_table(rows=9, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Activity"
    headers[1].text = "Timeline"
    headers[2].text = "Cost (MWK)"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    planned_activities = [
        ("External Beta Testing (Partial)", "Augâ€“Sep 2026", "500,000"),
        ("Pilot Deployment (1 Institution)", "Sep 2026", "400,000"),
        ("Basic Training Content", "Aug 2026", "250,000"),
        ("Internal Security Reviews", "Ongoing", "200,000"),
        ("Bug Fixes and Maintenance", "Ongoing", "300,000"),
        ("Monitoring and Evaluation (Partial)", "Oct 2026", "100,000"),
        ("Contingency", "", "115,000"),
        ("Total", "", "1,865,000")
    ]
    
    for i, activity in enumerate(planned_activities):
        row = table.rows[i + 1]
        row.cells[0].text = activity[0]
        row.cells[1].text = activity[1]
        row.cells[2].text = activity[2]
        if "Total" in activity[0]:
            for cell in row.cells:
                cell.paragraphs[0].runs[0].bold = True
    
    doc.add_heading("6.3 Activities That Will Be Deferred Without Additional Funding", level=2)
    
    deferred_items = [
        "Comprehensive external security audit (MWK 700,000)",
        "Full-scale pilot deployment (MWK 600,000)",
        "IP registration (MWK 400,000)",
        "Marketing and commercialization activities (MWK 500,000)",
        "Expanded training and workshops (MWK 500,000)"
    ]
    
    for item in deferred_items:
        p = doc.add_paragraph(item, style='List Bullet')
    
    # ============================================================
    # SECTION 7: CONCLUSION AND RECOMMENDATIONS
    # ============================================================
    
    doc.add_page_break()
    h7 = doc.add_heading("7. CONCLUSION AND RECOMMENDATIONS", level=1)
    
    doc.add_heading("7.1 Conclusion", level=2)
    
    p = doc.add_paragraph()
    p.add_run("DSTerminal has achieved significant technical milestones with NCST support. The software is now ready for external validation, but MWK 4,500,000 is needed to complete all remaining activities successfully.")
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("The available balance of MWK 1,865,000 is insufficient to cover external testing, pilot deployment, security validation, legal protection, and commercializationâ€”all of which are essential for the project's success and sustainability.")
    
    doc.add_heading("7.2 Recommendations for NCST", level=2)
    
    p = doc.add_paragraph()
    p.add_run("1. Consider additional funding of MWK 4,500,000 to cover all critical remaining activities:").bold = True
    
    sub_items = [
        "External beta testing and pilot deployment",
        "Comprehensive security audits",
        "IP registration and legal protection",
        "Marketing, commercialization, and sustainability",
        "Training content and workshops",
        "Continuous development support",
        "Monitoring and evaluation"
    ]
    
    for item in sub_items:
        p = doc.add_paragraph(f"   - {item}", style='List Bullet')
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("2. Facilitate connections â€“ Introduce the project to potential institutional partners for pilot deployment.").bold = True
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("3. Provide commercialization guidance â€“ Support with market entry and business model development.").bold = True
    
    # ============================================================
    # SECTION 8: ACKNOWLEDGEMENT
    # ============================================================
    
    doc.add_page_break()
    h8 = doc.add_heading("8. ACKNOWLEDGEMENT", level=1)
    
    p = doc.add_paragraph()
    p.add_run("I sincerely thank NCST for the continued support. The grant has been instrumental in advancing DSTerminal from concept to a functional, packaged software product ready for external validation.")
    
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Prepared By:").bold = True
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("Spark Wilson Spink").bold = True
    p = doc.add_paragraph()
    p.add_run("Project Lead, DSTerminal")
    p = doc.add_paragraph()
    p.add_run("Date: July 24, 2026")
    
    # ============================================================
    # SECTION 9: SUMMARY OF FUNDING REQUIREMENTS
    # ============================================================
    
    doc.add_page_break()
    h9 = doc.add_heading("9. SUMMARY OF FUNDING REQUIREMENTS", level=1)
    
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    headers = table.rows[0].cells
    headers[0].text = "Item"
    headers[1].text = "Amount (MWK)"
    for cell in headers:
        cell.paragraphs[0].runs[0].bold = True
    
    summary_data = [
        ("Total Grant Received", "5,000,000"),
        ("Total Spent to Date", "3,135,000"),
        ("Remaining Balance", "1,865,000"),
        ("Total Required to Complete Project", "4,500,000"),
        ("Additional Funding Requested", "4,500,000")
    ]
    
    for i, data in enumerate(summary_data):
        row = table.rows[i + 1]
        row.cells[0].text = data[0]
        row.cells[1].text = data[1]
        if "Total" in data[0] or "Additional" in data[0]:
            for cell in row.cells:
                cell.paragraphs[0].runs[0].bold = True
    
    # Save the document
    filename = f"DSTERMINAL_Progress_Report_{datetime.now().strftime('%Y%m%d')}.docx"
    doc.save(filename)
    print(f"âœ… Report saved as: {filename}")
    return filename

if __name__ == "__main__":
    # First, install python-docx if not installed
    try:
        import docx
    except ImportError:
        print("Installing python-docx...")
        os.system("pip install python-docx")
        import docx
    
    create_report()
    print("\nðŸ“„ Report generation complete!")
    print("   Open the generated .docx file to view the formatted report.")