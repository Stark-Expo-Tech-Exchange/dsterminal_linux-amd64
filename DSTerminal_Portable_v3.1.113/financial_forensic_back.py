#!/usr/bin/env python3
"""
DSTerminal Financial Forensics Module
Enhanced Global Banking Fraud Investigation with User Input Integration
Supports: Malawi, Africa, Global Banking Networks
"""

import os
import sys
import time
import random
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Rich console imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.live import Live
    from rich.table import Table
    from rich.align import Align
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    from rich.columns import Columns
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich not installed. Install with: pip install rich")

# PDF Generation imports
try:
    from reportlab.lib.pagesizes import A4, letter, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white, grey, red, green, blue, yellow, purple, orange
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table as PDFTable, TableStyle, PageBreak, KeepTogether
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics import renderPDF
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF reports will not be available.")
    print("Install with: pip install reportlab")

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'; RESET_ALL = '\033[0m'

if RICH_AVAILABLE:
    console = Console()
else:
    console = None

# ============================================================================
# DATA CLASSES FOR INVESTIGATION DETAILS
# ============================================================================

class InvestigationType(Enum):
    """Types of financial investigations"""
    MONEY_LAUNDERING = "Money Laundering"
    WIRE_FRAUD = "Wire Fraud"
    CRYPTO_SCAM = "Cryptocurrency Scam"
    IDENTITY_THEFT = "Identity Theft"
    INSIDER_TRADING = "Insider Trading"
    SHELL_COMPANY = "Shell Company"
    ACCOUNT_FRAUD = "Account Fraud"
    LOAN_FRAUD = "Loan Fraud"
    CHEQUE_FRAUD = "Cheque Fraud"
    CYBER_FRAUD = "Cyber Fraud"

class RiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class InvestigationStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLETED = "COMPLETED"
    REFERRED = "REFERRED"

@dataclass
class InstitutionDetails:
    """Details about the institution conducting the investigation"""
    institution_name: str
    institution_type: str  # Bank, Regulatory Body, Law Enforcement, etc.
    country: str
    city: str
    department: str
    investigator_name: str
    investigator_id: str
    contact_email: str
    contact_phone: str
    regulatory_license: str = ""
    swift_bic_code: str = ""
    bank_code: str = ""  # Local bank code (e.g., Malawi Bank Code)
    
@dataclass
class CaseDetails:
    """Core case investigation details"""
    case_number: str
    investigation_type: str
    case_title: str
    reporting_date: str
    status: str
    priority: str
    jurisdiction: str
    amount_involved: float
    currency: str
    
@dataclass
class SubjectDetails:
    """Details about the subject under investigation"""
    subject_name: str
    subject_type: str  # Individual, Company, Organization
    national_id: str
    account_numbers: List[str]
    known_addresses: List[str]
    phone_numbers: List[str]
    email_addresses: List[str]
    registration_number: str = ""  # For companies
    
@dataclass
class TransactionDetails:
    """Suspicious transaction details"""
    transaction_ids: List[str]
    date_range_start: str
    date_range_end: str
    source_accounts: List[str]
    destination_accounts: List[str]
    intermediary_banks: List[str]
    transaction_pattern: str
    total_amount: float
    
@dataclass
class EvidenceCollected:
    """Evidence gathered during investigation"""
    evidence_items: List[Dict[str, str]]
    document_references: List[str]
    witness_statements: List[str]
    forensic_findings: List[str]
    chain_of_custody: List[Dict[str, str]]

# ============================================================================
# GLOBAL BANKING DATABASE
# ============================================================================

# African Banks Database (including Malawi)
AFRICAN_BANKS = {
    "Malawi": [
        {"name": "National Bank of Malawi", "swift": "NBMAMWMW", "code": "101001"},
        {"name": "Reserve Bank of Malawi", "swift": "RBMAMWMW", "code": "100001"},
        {"name": "Standard Bank Malawi", "swift": "SBICMWMW", "code": "102001"},
        {"name": "FDH Bank Malawi", "swift": "FDHBMWMW", "code": "103001"},
        {"name": "NBS Bank Malawi", "swift": "NBSMMWMW", "code": "104001"},
        {"name": "MyBucks Banking Corporation", "swift": "MYBUMWMW", "code": "105001"},
        {"name": "Opportunity Bank Malawi", "swift": "OPBKMWMW", "code": "106001"},
        {"name": "First Capital Bank Malawi", "swift": "FCMBMWMW", "code": "107001"},
        {"name": "EcoBank Malawi", "swift": "ECOCMWMW", "code": "108001"}
    ],
    "South Africa": [
        {"name": "Standard Bank South Africa", "swift": "SBZAZAJJ", "code": "051001"},
        {"name": "First National Bank", "swift": "FIRNZAJJ", "code": "052001"},
        {"name": "ABSA Bank", "swift": "ABS AZAJJ", "code": "053001"},
        {"name": "Nedbank", "swift": "NEDSZAJJ", "code": "054001"},
        {"name": "Capitec Bank", "swift": "CABLZAJJ", "code": "055001"}
    ],
    "Nigeria": [
        {"name": "First Bank of Nigeria", "swift": "FBNINGLA", "code": "011001"},
        {"name": "Zenith Bank", "swift": "ZEIBINGL", "code": "012001"},
        {"name": "GTBank", "swift": "GTBINGLA", "code": "013001"},
        {"name": "UBA Bank", "swift": "UNAFNGLA", "code": "014001"}
    ],
    "Kenya": [
        {"name": "Equity Bank Kenya", "swift": "EQBLKENA", "code": "061001"},
        {"name": "KCB Bank", "swift": "KCBLKENX", "code": "062001"},
        {"name": "Co-operative Bank", "swift": "KCOOKENA", "code": "063001"}
    ],
    "Ghana": [
        {"name": "Ghana Commercial Bank", "swift": "GHCBGHAC", "code": "071001"},
        {"name": "Ecobank Ghana", "swift": "ECO CGHAC", "code": "072001"}
    ],
    "Zambia": [
        {"name": "Zanaco Bank", "swift": "ZANAZMLU", "code": "081001"},
        {"name": "Standard Chartered Zambia", "swift": "SCBLZMLU", "code": "082001"}
    ]
}

# Global Banking Networks
GLOBAL_BANKS = {
    "SWIFT_Members": [
        "JPMorgan Chase (USA)", "HSBC (UK)", "Deutsche Bank (Germany)",
        "Barclays (UK)", "BNP Paribas (France)", "Mizuho Bank (Japan)",
        "Bank of China (China)", "ICBC (China)", "Santander (Spain)"
    ],
    "Correspondent_Banks": [
        "Citibank N.A.", "Wells Fargo", "Bank of America",
        "Standard Chartered", "UBS AG", "Credit Suisse"
    ],
    "African_Correspondents": [
        "Standard Bank Group", "Ecobank Transnational", "United Bank for Africa",
        "African Development Bank", "Trade and Development Bank"
    ]
}

# High-risk jurisdictions
HIGH_RISK_JURISDICTIONS = {
    "North Korea": {"code": "DPRK", "risk": "CRITICAL"},
    "Iran": {"code": "IRN", "risk": "CRITICAL"},
    "Syria": {"code": "SYR", "risk": "CRITICAL"},
    "Russia": {"code": "RUS", "risk": "HIGH"},
    "Myanmar": {"code": "MMR", "risk": "HIGH"},
    "Venezuela": {"code": "VEN", "risk": "HIGH"},
    "Belarus": {"code": "BLR", "risk": "HIGH"},
    "Afghanistan": {"code": "AFG", "risk": "HIGH"}
}

# ============================================================================
# INVESTIGATION INPUT COLLECTOR
# ============================================================================

class InvestigationInputCollector:
    """Collects investigation details from the user/investigator"""
    
    def __init__(self):
        self.collected_data = {}
        
    def _safe_input(self, prompt: str, default: str = "") -> str:
        """Safely get input from user"""
        if console:
            result = Prompt.ask(prompt, default=default)
        else:
            result = input(f"{prompt} {default}: ").strip()
            if not result and default:
                result = default
        return result
    
    def _safe_confirm(self, prompt: str, default: bool = True) -> bool:
        """Safely get confirmation from user"""
        if console:
            return Confirm.ask(prompt, default=default)
        else:
            response = input(f"{prompt} (y/n): ").lower()
            return response == 'y' or (default and response == '')
    
    def collect_institution_details(self) -> InstitutionDetails:
        """Collect details about the investigating institution"""
        print("\n" + "="*60)
        print("🏛️  INSTITUTION DETAILS (REQUIRED FOR REPORT)")
        print("="*60)
        print("The following information will appear in every generated report.\n")
        
        # Bank selection for African banks
        if self._safe_confirm("\nIs this investigation being conducted by an African bank?", default=True):
            print("\n🌍 Select Country:")
            countries = list(AFRICAN_BANKS.keys())
            for i, country in enumerate(countries, 1):
                print(f"  {i}. {country}")
            
            country_choice = self._safe_input(f"\nSelect country (1-{len(countries)})", "1")
            try:
                country = countries[int(country_choice) - 1]
            except:
                country = "Malawi"
            
            print(f"\n🏦 Banks in {country}:")
            banks = AFRICAN_BANKS.get(country, AFRICAN_BANKS["Malawi"])
            for i, bank in enumerate(banks, 1):
                print(f"  {i}. {bank['name']} (SWIFT: {bank['swift']})")
            
            bank_choice = self._safe_input(f"\nSelect bank (1-{len(banks)})", "1")
            try:
                selected_bank = banks[int(bank_choice) - 1]
                institution_name = selected_bank['name']
                swift_code = selected_bank['swift']
                bank_code = selected_bank['code']
            except:
                selected_bank = banks[0]
                institution_name = selected_bank['name']
                swift_code = selected_bank['swift']
                bank_code = selected_bank['code']
        else:
            institution_name = self._safe_input("\nInstitution Name", "Financial Intelligence Unit")
            swift_code = self._safe_input("SWIFT/BIC Code", "N/A")
            bank_code = self._safe_input("Local Bank Code", "N/A")
            country = self._safe_input("Country", "Global")
        
        institution_type = self._safe_input(
            "Institution Type",
            "Bank / Regulatory Body / Law Enforcement"
        )
        
        city = self._safe_input("City", "Lilongwe" if country == "Malawi" else "N/A")
        department = self._safe_input("Department", "Financial Intelligence Unit")
        investigator_name = self._safe_input("Investigator Name", "FIU Analyst")
        investigator_id = self._safe_input("Investigator ID/Badge Number", "FIU-" + datetime.now().strftime("%Y%m%d"))
        contact_email = self._safe_input("Contact Email", "fiu@institution.com")
        contact_phone = self._safe_input("Contact Phone", "+265-XXX-XXX")
        regulatory_license = self._safe_input("Regulatory License Number", "N/A")
        
        return InstitutionDetails(
            institution_name=institution_name,
            institution_type=institution_type,
            country=country,
            city=city,
            department=department,
            investigator_name=investigator_name,
            investigator_id=investigator_id,
            contact_email=contact_email,
            contact_phone=contact_phone,
            regulatory_license=regulatory_license,
            swift_bic_code=swift_code,
            bank_code=bank_code
        )
    
    def collect_case_details(self) -> CaseDetails:
        """Collect core case details"""
        print("\n" + "="*60)
        print("📋 CASE DETAILS")
        print("="*60)
        
        # Generate default case number
        default_case = f"FIU-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
        case_number = self._safe_input("Case Number", default_case)
        
        print("\n📊 Investigation Type:")
        investigation_types = [t.value for t in InvestigationType]
        for i, itype in enumerate(investigation_types, 1):
            print(f"  {i}. {itype}")
        
        type_choice = self._safe_input(f"\nSelect type (1-{len(investigation_types)})", "1")
        try:
            investigation_type = investigation_types[int(type_choice) - 1]
        except:
            investigation_type = "Money Laundering"
        
        case_title = self._safe_input("Case Title", f"{investigation_type} Investigation")
        reporting_date = self._safe_input("Reporting Date", datetime.now().strftime("%Y-%m-%d"))
        
        print("\n📌 Status:")
        statuses = [s.value for s in InvestigationStatus]
        for i, status in enumerate(statuses, 1):
            print(f"  {i}. {status}")
        
        status_choice = self._safe_input(f"\nSelect status (1-{len(statuses)})", "2")
        try:
            status = statuses[int(status_choice) - 1]
        except:
            status = "IN_PROGRESS"
        
        print("\n⚠️ Priority:")
        priorities = ["URGENT", "HIGH", "MEDIUM", "LOW"]
        for i, priority in enumerate(priorities, 1):
            print(f"  {i}. {priority}")
        
        priority_choice = self._safe_input(f"\nSelect priority (1-{len(priorities)})", "1")
        try:
            priority = priorities[int(priority_choice) - 1]
        except:
            priority = "HIGH"
        
        jurisdiction = self._safe_input("Jurisdiction (Country/Region)", "Malawi / Global")
        
        print("\n💰 Amount Involved:")
        amount_str = self._safe_input("Amount", "0")
        try:
            amount = float(amount_str.replace(',', '').replace('$', ''))
        except:
            amount = 0.0
        
        currency = self._safe_input("Currency", "MWK" if jurisdiction == "Malawi" else "USD")
        
        return CaseDetails(
            case_number=case_number,
            investigation_type=investigation_type,
            case_title=case_title,
            reporting_date=reporting_date,
            status=status,
            priority=priority,
            jurisdiction=jurisdiction,
            amount_involved=amount,
            currency=currency
        )
    
    def collect_subject_details(self) -> SubjectDetails:
        """Collect details about the investigation subject"""
        print("\n" + "="*60)
        print("👤 SUBJECT DETAILS (SUSPECT/ENTITY)")
        print("="*60)
        
        has_subject = self._safe_confirm("Do you have subject information to enter?", default=False)
        
        if not has_subject:
            return SubjectDetails(
                subject_name="UNKNOWN - Under Investigation",
                subject_type="Unknown",
                national_id="N/A",
                account_numbers=[],
                known_addresses=[],
                phone_numbers=[],
                email_addresses=[],
                registration_number=""
            )
        
        subject_name = self._safe_input("Subject Name", "UNKNOWN")
        
        print("\nSubject Type:")
        subject_types = ["Individual", "Company", "Organization", "Trust", "Partnership"]
        for i, stype in enumerate(subject_types, 1):
            print(f"  {i}. {stype}")
        
        type_choice = self._safe_input(f"\nSelect type (1-{len(subject_types)})", "1")
        try:
            subject_type = subject_types[int(type_choice) - 1]
        except:
            subject_type = "Individual"
        
        national_id = self._safe_input("National ID/Registration Number", "N/A")
        
        # Account numbers
        account_numbers = []
        while True:
            acc = self._safe_input("Account Number (leave empty to stop)", "")
            if not acc:
                break
            account_numbers.append(acc)
            print(f"  ✓ Added: {acc}")
        
        # Addresses
        known_addresses = []
        while True:
            addr = self._safe_input("Address (leave empty to stop)", "")
            if not addr:
                break
            known_addresses.append(addr)
            print(f"  ✓ Added address")
        
        # Phone numbers
        phone_numbers = []
        while True:
            phone = self._safe_input("Phone Number (leave empty to stop)", "")
            if not phone:
                break
            phone_numbers.append(phone)
            print(f"  ✓ Added: {phone}")
        
        # Emails
        email_addresses = []
        while True:
            email = self._safe_input("Email Address (leave empty to stop)", "")
            if not email:
                break
            email_addresses.append(email)
            print(f"  ✓ Added: {email}")
        
        registration_number = self._safe_input("Company Registration Number (if applicable)", "")
        
        return SubjectDetails(
            subject_name=subject_name,
            subject_type=subject_type,
            national_id=national_id,
            account_numbers=account_numbers,
            known_addresses=known_addresses,
            phone_numbers=phone_numbers,
            email_addresses=email_addresses,
            registration_number=registration_number
        )
    
    def collect_transaction_details(self) -> Optional[TransactionDetails]:
        """Collect transaction details"""
        print("\n" + "="*60)
        print("💸 TRANSACTION DETAILS")
        print("="*60)
        
        has_transactions = self._safe_confirm("Do you have transaction details to enter?", default=False)
        
        if not has_transactions:
            return None
        
        transaction_ids = []
        while True:
            txn_id = self._safe_input("Transaction ID (leave empty to stop)", "")
            if not txn_id:
                break
            transaction_ids.append(txn_id)
            print(f"  ✓ Added: {txn_id}")
        
        date_range_start = self._safe_input("Date Range Start (YYYY-MM-DD)", (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"))
        date_range_end = self._safe_input("Date Range End (YYYY-MM-DD)", datetime.now().strftime("%Y-%m-%d"))
        
        source_accounts = []
        while True:
            acc = self._safe_input("Source Account (leave empty to stop)", "")
            if not acc:
                break
            source_accounts.append(acc)
        
        destination_accounts = []
        while True:
            acc = self._safe_input("Destination Account (leave empty to stop)", "")
            if not acc:
                break
            destination_accounts.append(acc)
        
        intermediary_banks = []
        while True:
            bank = self._safe_input("Intermediary Bank (leave empty to stop)", "")
            if not bank:
                break
            intermediary_banks.append(bank)
        
        transaction_pattern = self._safe_input("Transaction Pattern Description", "Suspicious pattern detected")
        
        total_amount_str = self._safe_input("Total Amount Involved", "0")
        try:
            total_amount = float(total_amount_str.replace(',', '').replace('$', ''))
        except:
            total_amount = 0.0
        
        return TransactionDetails(
            transaction_ids=transaction_ids,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            source_accounts=source_accounts,
            destination_accounts=destination_accounts,
            intermediary_banks=intermediary_banks,
            transaction_pattern=transaction_pattern,
            total_amount=total_amount
        )
    
    def collect_evidence_details(self) -> EvidenceCollected:
        """Collect evidence details"""
        print("\n" + "="*60)
        print("📎 EVIDENCE COLLECTED")
        print("="*60)
        
        evidence_items = []
        while True:
            evidence_type = self._safe_input("Evidence Type (e.g., Bank Statement, Email, etc.)", "")
            if not evidence_type:
                break
            evidence_desc = self._safe_input("Description", "")
            evidence_ref = self._safe_input("Reference Number", "")
            evidence_items.append({
                "type": evidence_type,
                "description": evidence_desc,
                "reference": evidence_ref
            })
            print(f"  ✓ Added evidence: {evidence_type}")
        
        document_references = []
        while True:
            doc_ref = self._safe_input("Document Reference (leave empty to stop)", "")
            if not doc_ref:
                break
            document_references.append(doc_ref)
        
        witness_statements = []
        while True:
            witness = self._safe_input("Witness Name (leave empty to stop)", "")
            if not witness:
                break
            statement_date = self._safe_input("Statement Date", datetime.now().strftime("%Y-%m-%d"))
            witness_statements.append(f"{witness} - {statement_date}")
        
        forensic_findings = []
        while True:
            finding = self._safe_input("Forensic Finding (leave empty to stop)", "")
            if not finding:
                break
            forensic_findings.append(finding)
        
        chain_of_custody = [{
            "timestamp": datetime.now().isoformat(),
            "custodian": self._safe_input("Current Evidence Custodian", "FIU Department"),
            "location": self._safe_input("Storage Location", "Secure Evidence Room")
        }]
        
        return EvidenceCollected(
            evidence_items=evidence_items,
            document_references=document_references,
            witness_statements=witness_statements,
            forensic_findings=forensic_findings,
            chain_of_custody=chain_of_custody
        )
    
    def collect_additional_notes(self) -> str:
        """Collect additional investigation notes"""
        print("\n" + "="*60)
        print("📝 ADDITIONAL INVESTIGATION NOTES")
        print("="*60)
        print("Enter any additional notes (type 'END' on a new line to finish):\n")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
        
        return "\n".join(lines)

# ============================================================================
# COMPREHENSIVE INVESTIGATION REPORT
# ============================================================================

class InvestigationReport:
    """Complete investigation report with all collected data"""
    
    def __init__(self):
        self.institution: Optional[InstitutionDetails] = None
        self.case: Optional[CaseDetails] = None
        self.subject: Optional[SubjectDetails] = None
        self.transactions: Optional[TransactionDetails] = None
        self.evidence: Optional[EvidenceCollected] = None
        self.additional_notes: str = ""
        self.findings: List[Tuple[str, str, str]] = []
        self.recommendations: List[str] = []
        self.report_id: str = ""
        self.generated_at: str = ""
        
    def to_dict(self) -> Dict:
        """Convert report to dictionary"""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "institution": asdict(self.institution) if self.institution else None,
            "case": asdict(self.case) if self.case else None,
            "subject": asdict(self.subject) if self.subject else None,
            "transactions": asdict(self.transactions) if self.transactions else None,
            "evidence": asdict(self.evidence) if self.evidence else None,
            "additional_notes": self.additional_notes,
            "findings": [{"finding": f, "details": d, "confidence": c} for f, d, c in self.findings],
            "recommendations": self.recommendations
        }
    
    def generate_pdf_report(self, output_dir: str) -> Optional[str]:
        """Generate PDF report with all collected data"""
        if not REPORTLAB_AVAILABLE:
            return None
        
        pdf_filename = os.path.join(output_dir, f"{self.report_id}_FULL_REPORT.pdf")
        
        try:
            doc = SimpleDocTemplate(
                pdf_filename,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=f"Financial Investigation Report - {self.report_id}",
                author=f"{self.institution.institution_name} - {self.institution.department}",
                subject=f"Case: {self.case.case_number} - {self.case.investigation_type}"
            )
            
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=HexColor('#8B0000'),
                alignment=1,
                spaceAfter=30,
                fontName='Helvetica-Bold'
            )
            
            section_style = ParagraphStyle(
                'SectionStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=HexColor('#2E4053'),
                spaceBefore=20,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            subsection_style = ParagraphStyle(
                'SubsectionStyle',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=HexColor('#5D6D7E'),
                spaceBefore=15,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                fontName='Helvetica'
            )
            
            story = []
            
            # Header
            header_text = f"""
            <para alignment="center">
            <font size="16" color="#8B0000"><b>{self.institution.institution_name}</b></font><br/>
            <font size="11" color="#2C3E50">{self.institution.department}</font><br/>
            <font size="9" color="#7F8C8D">Financial Investigation Report</font>
            </para>
            """
            story.append(Paragraph(header_text, normal_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Title
            story.append(Paragraph(f"INVESTIGATION REPORT: {self.case.case_number}", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Institution Information
            story.append(Paragraph("1. INVESTIGATING INSTITUTION", section_style))
            inst_data = [
                ["Institution Name", self.institution.institution_name],
                ["Institution Type", self.institution.institution_type],
                ["Country", self.institution.country],
                ["City", self.institution.city],
                ["Department", self.institution.department],
                ["SWIFT/BIC Code", self.institution.swift_bic_code],
                ["Bank Code", self.institution.bank_code],
                ["Investigator Name", self.institution.investigator_name],
                ["Investigator ID", self.institution.investigator_id],
                ["Contact Email", self.institution.contact_email],
                ["Contact Phone", self.institution.contact_phone],
                ["Regulatory License", self.institution.regulatory_license]
            ]
            
            inst_table = PDFTable(inst_data, colWidths=[2.2*inch, 3.5*inch])
            inst_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (0, -1), white),
                ('BACKGROUND', (1, 0), (1, -1), HexColor('#ECF0F1')),
                ('TEXTCOLOR', (1, 0), (1, -1), black),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(inst_table)
            story.append(Spacer(1, 0.2 * inch))
            
            # Case Information
            story.append(Paragraph("2. CASE INFORMATION", section_style))
            case_data = [
                ["Case Number", self.case.case_number],
                ["Investigation Type", self.case.investigation_type],
                ["Case Title", self.case.case_title],
                ["Reporting Date", self.case.reporting_date],
                ["Status", self.case.status],
                ["Priority", self.case.priority],
                ["Jurisdiction", self.case.jurisdiction],
                ["Amount Involved", f"{self.case.currency} {self.case.amount_involved:,.2f}"]
            ]
            
            case_table = PDFTable(case_data, colWidths=[2.2*inch, 3.5*inch])
            case_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#943126')),
                ('TEXTCOLOR', (0, 0), (0, -1), white),
                ('BACKGROUND', (1, 0), (1, -1), HexColor('#FADBD8')),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
            ]))
            story.append(case_table)
            story.append(Spacer(1, 0.2 * inch))
            
            # Subject Information
            if self.subject and self.subject.subject_name != "UNKNOWN - Under Investigation":
                story.append(Paragraph("3. SUBJECT INFORMATION", section_style))
                subject_data = [
                    ["Subject Name", self.subject.subject_name],
                    ["Subject Type", self.subject.subject_type],
                    ["National ID/Reg Number", self.subject.national_id],
                    ["Company Registration", self.subject.registration_number],
                    ["Account Numbers", ", ".join(self.subject.account_numbers) if self.subject.account_numbers else "N/A"],
                    ["Known Addresses", ", ".join(self.subject.known_addresses[:2]) if self.subject.known_addresses else "N/A"],
                    ["Phone Numbers", ", ".join(self.subject.phone_numbers[:3]) if self.subject.phone_numbers else "N/A"],
                    ["Email Addresses", ", ".join(self.subject.email_addresses[:3]) if self.subject.email_addresses else "N/A"]
                ]
                
                subject_table = PDFTable(subject_data, colWidths=[2.2*inch, 3.5*inch])
                subject_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), HexColor('#1A5276')),
                    ('TEXTCOLOR', (0, 0), (0, -1), white),
                    ('BACKGROUND', (1, 0), (1, -1), HexColor('#D4E6F1')),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
                ]))
                story.append(subject_table)
                story.append(Spacer(1, 0.2 * inch))
            
            # Transaction Details
            if self.transactions and self.transactions.transaction_ids:
                story.append(Paragraph("4. TRANSACTION DETAILS", section_style))
                txn_data = [
                    ["Transaction IDs", ", ".join(self.transactions.transaction_ids[:5])],
                    ["Date Range", f"{self.transactions.date_range_start} to {self.transactions.date_range_end}"],
                    ["Source Accounts", ", ".join(self.transactions.source_accounts[:3])],
                    ["Destination Accounts", ", ".join(self.transactions.destination_accounts[:3])],
                    ["Intermediary Banks", ", ".join(self.transactions.intermediary_banks[:3])],
                    ["Transaction Pattern", self.transactions.transaction_pattern],
                    ["Total Amount", f"{self.case.currency} {self.transactions.total_amount:,.2f}"]
                ]
                
                txn_table = PDFTable(txn_data, colWidths=[2.2*inch, 3.5*inch])
                txn_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), HexColor('#7D3C98')),
                    ('TEXTCOLOR', (0, 0), (0, -1), white),
                    ('BACKGROUND', (1, 0), (1, -1), HexColor('#E8DAEF')),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
                ]))
                story.append(txn_table)
                story.append(Spacer(1, 0.2 * inch))
            
            # Findings
            if self.findings:
                story.append(Paragraph("5. INVESTIGATION FINDINGS", section_style))
                findings_data = [["#", "Finding", "Details", "Confidence"]]
                for i, (finding, details, confidence) in enumerate(self.findings, 1):
                    confidence_color = "#27AE60" if confidence == "High" else "#F39C12" if confidence == "Medium" else "#E74C3C"
                    findings_data.append([
                        str(i),
                        Paragraph(finding, normal_style),
                        Paragraph(details[:200], normal_style),
                        Paragraph(f'<font color="{confidence_color}"><b>{confidence}</b></font>', normal_style)
                    ])
                
                findings_table = PDFTable(findings_data, colWidths=[0.5*inch, 2*inch, 3.2*inch, 0.8*inch])
                findings_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#34495E')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#BDC3C7')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9F9')),
                ]))
                story.append(findings_table)
                story.append(Spacer(1, 0.2 * inch))
            
            # Recommendations
            if self.recommendations:
                story.append(Paragraph("6. RECOMMENDATIONS", section_style))
                for rec in self.recommendations:
                    story.append(Paragraph(f"✓ {rec}", normal_style))
                story.append(Spacer(1, 0.2 * inch))
            
            # Evidence Summary
            if self.evidence and self.evidence.evidence_items:
                story.append(Paragraph("7. EVIDENCE SUMMARY", section_style))
                for item in self.evidence.evidence_items:
                    story.append(Paragraph(f"• {item['type']}: {item['description']} (Ref: {item['reference']})", normal_style))
                story.append(Spacer(1, 0.2 * inch))
            
            # Additional Notes
            if self.additional_notes:
                story.append(Paragraph("8. ADDITIONAL NOTES", section_style))
                story.append(Paragraph(self.additional_notes.replace('\n', '<br/>'), normal_style))
            
            # Footer
            story.append(Spacer(1, 0.5 * inch))
            footer_text = f"""
            <para alignment="center">
            <font size="8" color="#7F8C8D">
            Report Generated: {self.generated_at}<br/>
            Report ID: {self.report_id}<br/>
            This report is confidential and for authorized use only.
            </font>
            </para>
            """
            story.append(Paragraph(footer_text, normal_style))
            
            doc.build(story)
            return pdf_filename
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            return None
    
    def generate_json_report(self, output_dir: str) -> str:
        """Generate JSON report"""
        json_filename = os.path.join(output_dir, f"{self.report_id}.json")
        with open(json_filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return json_filename

# ============================================================================
# ENHANCED FINANCIAL FORENSICS CLASS
# ============================================================================

class EnhancedFinancialForensics:
    """Enhanced financial forensics with complete user input integration"""
    
    def __init__(self, workspace_dir=None):
        self.workspace_dir = workspace_dir or str(Path.home() / "dsterminal_workspace" / "financial_reports")
        os.makedirs(self.workspace_dir, exist_ok=True)
        self.reports_dir = os.path.join(self.workspace_dir, "pdf_reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        self.input_collector = InvestigationInputCollector()
        self.current_investigation: Optional[InvestigationReport] = None
        self.institution_details: Optional[InstitutionDetails] = None
        self.case_files = []
        
    def display_institution_header(self):
        """Display institution header in reports"""
        if self.institution_details and console:
            header = Panel(
                f"""
[bold cyan]🏛️ {self.institution_details.institution_name}[/bold cyan]
[dim]{self.institution_details.department}[/dim]
[dim]Country: {self.institution_details.country} | City: {self.institution_details.city}[/dim]
[dim]SWIFT: {self.institution_details.swift_bic_code} | Bank Code: {self.institution_details.bank_code}[/dim]
[dim]Investigator: {self.institution_details.investigator_name} (ID: {self.institution_details.investigator_id})[/dim]
[dim]Contact: {self.institution_details.contact_email} | {self.institution_details.contact_phone}[/dim]
                """,
                title="[bold red]INVESTIGATING INSTITUTION[/bold red]",
                border_style="red"
            )
            console.print(header)
    
    def start_new_investigation(self):
        """Start a new investigation with full user input"""
        console.clear() if console else os.system('clear')
        
        self._display_investigation_title()
        
        # Collect institution details first (these will appear in every report)
        if not self.institution_details:
            self.institution_details = self.input_collector.collect_institution_details()
        
        # Display institution header
        self.display_institution_header()
        
        # Create new investigation report
        self.current_investigation = InvestigationReport()
        self.current_investigation.institution = self.institution_details
        
        # Collect case details
        self.current_investigation.case = self.input_collector.collect_case_details()
        
        # Collect subject details
        self.current_investigation.subject = self.input_collector.collect_subject_details()
        
        # Collect transaction details
        self.current_investigation.transactions = self.input_collector.collect_transaction_details()
        
        # Collect evidence
        self.current_investigation.evidence = self.input_collector.collect_evidence_details()
        
        # Collect additional notes
        self.current_investigation.additional_notes = self.input_collector.collect_additional_notes()
        
        # Generate report ID
        self.current_investigation.report_id = f"FINREP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.current_investigation.generated_at = datetime.now().isoformat()
        
        # Generate findings based on case type and collected data
        self._generate_findings_from_data()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Save reports
        self._save_complete_report()
        
        return self.current_investigation
    
    def _generate_findings_from_data(self):
        """Generate findings based on collected investigation data"""
        findings = []
        
        case_type = self.current_investigation.case.investigation_type.lower()
        amount = self.current_investigation.case.amount_involved
        
        # Base findings from collected data
        if self.current_investigation.transactions:
            findings.append((
                "Transaction Pattern Analysis",
                f"Suspicious pattern detected: {self.current_investigation.transactions.transaction_pattern}",
                "High"
            ))
            
            if len(self.current_investigation.transactions.intermediary_banks) > 2:
                findings.append((
                    "Multiple Intermediaries",
                    f"Transactions routed through {len(self.current_investigation.transactions.intermediary_banks)} intermediary banks",
                    "Medium"
                ))
        
        if self.current_investigation.subject and self.current_investigation.subject.account_numbers:
            findings.append((
                "Subject Account Identification",
                f"{len(self.current_investigation.subject.account_numbers)} accounts linked to subject",
                "High"
            ))
        
        # Type-specific findings
        if "money laundering" in case_type:
            findings.extend([
                ("Structuring Detected", f"Multiple transactions in amounts below reporting threshold", "High"),
                ("Layering Pattern", "Complex transaction chain through multiple jurisdictions", "Medium"),
                ("Integration Point", f"Funds entering legitimate economy through various channels", "Medium")
            ])
        elif "wire fraud" in case_type:
            findings.extend([
                ("Unauthorized Transfer", f"Wire transfer without proper authorization", "High"),
                ("Beneficiary Mismatch", "Discrepancy between stated and actual beneficiary", "High"),
                ("BEC Indicators", "Business Email Compromise pattern detected", "Medium")
            ])
        elif "crypto" in case_type:
            findings.extend([
                ("Blockchain Analysis", "On-chain pattern matching with known scam wallets", "High"),
                ("Exchange Exposure", f"Funds traced to cryptocurrency exchanges", "Medium"),
                ("Mixer Usage", "Transaction obfuscation through mixing services", "Medium")
            ])
        elif "identity" in case_type:
            findings.extend([
                ("Synthetic Identity", f"Indicators of synthetic identity creation", "High"),
                ("Unauthorized Access", "Account takeover pattern detected", "High"),
                ("Credential Compromise", "Stolen credentials found in dark web monitoring", "Medium")
            ])
        
        # Amount-based finding
        if amount > 1000000:
            findings.append((
                "Significant Financial Impact",
                f"Total amount involved: ${amount:,.2f}",
                "High"
            ))
        
        self.current_investigation.findings = findings[:10]  # Limit to 10 findings
    
    def _generate_recommendations(self):
        """Generate recommendations based on investigation"""
        recommendations = [
            "Immediately freeze all identified suspicious accounts",
            f"File Suspicious Activity Report (SAR) with {self.institution_details.country} FIU",
            "Notify relevant law enforcement agencies",
            "Conduct enhanced due diligence on all counterparties",
            "Preserve all electronic evidence for legal proceedings",
            "Implement enhanced transaction monitoring for similar patterns",
            "Review and strengthen internal controls",
            "Consider asset freezing and forfeiture proceedings"
        ]
        
        # Add jurisdiction-specific recommendation
        if self.institution_details.country == "Malawi":
            recommendations.insert(1, "Notify Reserve Bank of Malawi and Malawi Financial Intelligence Authority")
            recommendations.append("Coordinate with Malawi Police Service - Financial Crimes Division")
        
        self.current_investigation.recommendations = recommendations
    
    def _save_complete_report(self):
        """Save both JSON and PDF reports"""
        # Save JSON
        json_file = self.current_investigation.generate_json_report(self.workspace_dir)
        self.case_files.append(json_file)
        
        # Generate PDF
        pdf_file = self.current_investigation.generate_pdf_report(self.reports_dir)
        
        if console:
            console.print(f"\n[bold green]✓ Investigation Complete![/bold green]")
            console.print(f"[cyan]JSON Report:[/cyan] {json_file}")
            if pdf_file:
                console.print(f"[cyan]PDF Report:[/cyan] {pdf_file}")
        else:
            print(f"\n✓ Investigation Complete!")
            print(f"JSON Report: {json_file}")
            if pdf_file:
                print(f"PDF Report: {pdf_file}")
    
    def display_full_report(self):
        """Display the complete investigation report in console"""
        if not self.current_investigation:
            if console:
                console.print("[red]No active investigation to display[/red]")
            return
        
        console.clear() if console else None
        
        # Institution Header
        self.display_institution_header()
        
        # Case Information
        case_panel = Panel(
            f"""
[bold yellow]Case Number:[/bold yellow] {self.current_investigation.case.case_number}
[bold yellow]Investigation Type:[/bold yellow] {self.current_investigation.case.investigation_type}
[bold yellow]Case Title:[/bold yellow] {self.current_investigation.case.case_title}
[bold yellow]Status:[/bold yellow] {self.current_investigation.case.status}
[bold yellow]Priority:[/bold yellow] [red]{self.current_investigation.case.priority}[/red]
[bold yellow]Jurisdiction:[/bold yellow] {self.current_investigation.case.jurisdiction}
[bold yellow]Amount:[/bold yellow] [green]{self.current_investigation.case.currency} {self.current_investigation.case.amount_involved:,.2f}[/green]
            """,
            title="[bold red]📋 CASE DETAILS[/bold red]",
            border_style="red"
        )
        
        if console:
            console.print(case_panel)
        
        # Subject Information
        if self.current_investigation.subject and self.current_investigation.subject.subject_name != "UNKNOWN - Under Investigation":
            subject_lines = [
                f"[bold cyan]Subject Name:[/bold cyan] {self.current_investigation.subject.subject_name}",
                f"[bold cyan]Subject Type:[/bold cyan] {self.current_investigation.subject.subject_type}",
                f"[bold cyan]National ID:[/bold cyan] {self.current_investigation.subject.national_id}"
            ]
            if self.current_investigation.subject.account_numbers:
                subject_lines.append(f"[bold cyan]Accounts:[/bold cyan] {', '.join(self.current_investigation.subject.account_numbers[:3])}")
            
            subject_panel = Panel(
                "\n".join(subject_lines),
                title="[bold yellow]👤 SUBJECT DETAILS[/bold yellow]",
                border_style="yellow"
            )
            if console:
                console.print(subject_panel)
        
        # Findings Table
        if self.current_investigation.findings:
            findings_table = Table(title="🔍 INVESTIGATION FINDINGS", box=box.DOUBLE_EDGE)
            findings_table.add_column("#", style="dim", width=4)
            findings_table.add_column("Finding", style="cyan", width=25)
            findings_table.add_column("Details", style="white", width=45)
            findings_table.add_column("Confidence", style="yellow", width=12)
            
            for i, (finding, details, confidence) in enumerate(self.current_investigation.findings, 1):
                conf_color = "green" if confidence == "High" else "yellow" if confidence == "Medium" else "red"
                findings_table.add_row(str(i), finding, details, f"[{conf_color}]{confidence}[/{conf_color}]")
            
            if console:
                console.print(findings_table)
        
        # Recommendations
        if self.current_investigation.recommendations:
            rec_text = "\n".join([f"✓ {rec}" for rec in self.current_investigation.recommendations[:8]])
            rec_panel = Panel(
                rec_text,
                title="[bold green]📋 RECOMMENDATIONS[/bold green]",
                border_style="green"
            )
            if console:
                console.print(rec_panel)
        
        # Additional Notes
        if self.current_investigation.additional_notes:
            notes_panel = Panel(
                self.current_investigation.additional_notes[:500],
                title="[bold cyan]📝 ADDITIONAL NOTES[/bold cyan]",
                border_style="cyan"
            )
            if console:
                console.print(notes_panel)
    
    def _display_investigation_title(self):
        """Display animated investigation title"""
        title_art = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗██╗ █████╗ ██╗              ║
║    ██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██║██╔══██╗██║              ║
║    █████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║     ██║███████║██║              ║
║    ██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██║██╔══██║██║              ║
║    ██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗██║██║  ██║███████╗         ║
║    ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝╚═╝  ╚═╝╚══════╝         ║
║                                                                               ║
║                  🔍 ENHANCED FINANCIAL INVESTIGATION SUITE 🔍                 ║
║                      🌍 GLOBAL BANKING SUPPORT 🌍                              ║
║                    🇲🇼 Malawi | Africa | Worldwide 🇲🇼                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """
        if console:
            for line in title_art.split('\n'):
                console.print(f"[bold red]{line}[/bold red]")
                time.sleep(0.01)
            console.print(Panel(
                "[bold yellow]Financial Intelligence Unit[/bold yellow]\n"
                "[cyan]Complete investigation documentation with institutional details[/cyan]\n"
                f"[dim]Reports Directory: {self.reports_dir}[/dim]",
                border_style="red"
            ))
            time.sleep(1.5)
    
    def main_menu(self):
        """Main investigation menu"""
        while True:
            console.clear() if console else os.system('clear')
            
            if console:
                self._display_investigation_title()
                
                menu_items = [
                    "[cyan]1.[/cyan] 🔍 Start New Investigation (Full Input)",
                    "[cyan]2.[/cyan] 📋 View Current Investigation Report",
                    "[cyan]3.[/cyan] 📁 View Saved Investigation Reports",
                    "[cyan]4.[/cyan] 🏛️ Update Institution Details",
                    "[cyan]5.[/cyan] 📊 Quick Investigation (Auto-Generated)",
                    "[cyan]6.[/cyan] 🌐 Live Financial Crime Monitor",
                    "[cyan]0.[/cyan] Exit"
                ]
                
                menu_panel = Panel(
                    "\n".join(menu_items),
                    title="[bold white]📊 FINANCIAL INVESTIGATION MENU[/bold white]",
                    border_style="bright_blue"
                )
                console.print(Align.center(menu_panel))
                
                choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]", choices=["0","1","2","3","4","5","6"])
            else:
                print("\n" + "="*50)
                print("FINANCIAL INVESTIGATION MENU")
                print("="*50)
                print("1. Start New Investigation (Full Input)")
                print("2. View Current Investigation Report")
                print("3. View Saved Investigation Reports")
                print("4. Update Institution Details")
                print("5. Quick Investigation (Auto-Generated)")
                print("6. Live Financial Crime Monitor")
                print("0. Exit")
                choice = input("\nSelect option: ").strip()
            
            if choice == "0":
                if console:
                    console.print("\n[bold red]Exiting Financial Forensics Suite...[/bold red]")
                else:
                    print("\nExiting Financial Forensics Suite...")
                break
            elif choice == "1":
                self.start_new_investigation()
                if console:
                    console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
                    input()
            elif choice == "2":
                self.display_full_report()
                if console:
                    console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
                    input()
            elif choice == "3":
                self.view_saved_reports()
            elif choice == "4":
                self.update_institution_details()
            elif choice == "5":
                self.quick_investigation()
            elif choice == "6":
                self.live_financial_crime_monitor()
    
    def update_institution_details(self):
        """Update institution details"""
        if console:
            console.clear()
            console.print("[bold yellow]Updating Institution Details...[/bold yellow]\n")
        self.institution_details = self.input_collector.collect_institution_details()
        if console:
            console.print("[bold green]✓ Institution details updated![/bold green]")
            console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
            input()
    
    def view_saved_reports(self):
        """View saved investigation reports"""
        reports = list(Path(self.workspace_dir).glob("FINREP-*.json"))
        
        if not reports:
            if console:
                console.print("[yellow]No saved reports found.[/yellow]")
                console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
                input()
            return
        
        if console:
            console.clear()
            console.print("[bold cyan]📁 SAVED INVESTIGATION REPORTS[/bold cyan]\n")
            
            for i, report in enumerate(reports, 1):
                with open(report, 'r') as f:
                    data = json.load(f)
                console.print(f"[green]{i}.[/green] [yellow]{data.get('report_id', 'Unknown')}[/yellow]")
                if data.get('case'):
                    console.print(f"     Case: {data['case'].get('case_number', 'N/A')} - {data['case'].get('investigation_type', 'N/A')}")
                console.print(f"     Generated: {data.get('generated_at', 'N/A')[:19]}")
                console.print()
            
            choice = Prompt.ask("Enter report number to view (0 to exit)", default="0")
            if choice.isdigit() and 1 <= int(choice) <= len(reports):
                with open(reports[int(choice)-1], 'r') as f:
                    data = json.load(f)
                self._display_saved_report(data)
        else:
            for i, report in enumerate(reports, 1):
                print(f"{i}. {report.name}")
            choice = input("\nEnter report number to view (0 to exit): ")
            if choice.isdigit() and 1 <= int(choice) <= len(reports):
                with open(reports[int(choice)-1], 'r') as f:
                    data = json.load(f)
                self._display_saved_report(data)
        
        if console:
            console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
            input()
    
    def _display_saved_report(self, data):
        """Display a saved report"""
        if console:
            console.clear()
            
            if data.get('institution'):
                inst = data['institution']
                header = Panel(
                    f"[bold cyan]🏛️ {inst.get('institution_name', 'Unknown')}[/bold cyan]\n"
                    f"[dim]{inst.get('department', 'N/A')}[/dim]\n"
                    f"[dim]Country: {inst.get('country', 'N/A')} | Investigator: {inst.get('investigator_name', 'N/A')}[/dim]",
                    title="[bold red]INVESTIGATING INSTITUTION[/bold red]",
                    border_style="red"
                )
                console.print(header)
            
            if data.get('case'):
                case = data['case']
                case_panel = Panel(
                    f"[yellow]Case Number:[/yellow] {case.get('case_number', 'N/A')}\n"
                    f"[yellow]Type:[/yellow] {case.get('investigation_type', 'N/A')}\n"
                    f"[yellow]Status:[/yellow] {case.get('status', 'N/A')}\n"
                    f"[yellow]Amount:[/yellow] [green]{case.get('currency', 'USD')} {case.get('amount_involved', 0):,.2f}[/green]",
                    title="[bold red]CASE DETAILS[/bold red]",
                    border_style="red"
                )
                console.print(case_panel)
            
            if data.get('findings'):
                findings_table = Table(title="FINDINGS")
                findings_table.add_column("Finding", style="cyan")
                findings_table.add_column("Confidence", style="yellow")
                for f in data['findings'][:5]:
                    findings_table.add_row(f.get('finding', 'N/A'), f.get('confidence', 'N/A'))
                console.print(findings_table)
        else:
            print(json.dumps(data, indent=2)[:2000])
    
    def quick_investigation(self):
        """Quick auto-generated investigation"""
        if not self.institution_details:
            if console:
                console.print("[yellow]Please set institution details first (option 4)[/yellow]")
                console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
                input()
            return
        
        # Create quick investigation with minimal input
        self.current_investigation = InvestigationReport()
        self.current_investigation.institution = self.institution_details
        
        # Generate default case
        self.current_investigation.case = CaseDetails(
            case_number=f"QUICK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            investigation_type=random.choice([t.value for t in InvestigationType]),
            case_title="Rapid Investigation - Suspicious Activity Detected",
            reporting_date=datetime.now().strftime("%Y-%m-%d"),
            status="IN_PROGRESS",
            priority="HIGH",
            jurisdiction=self.institution_details.country,
            amount_involved=random.randint(10000, 5000000),
            currency="USD"
        )
        
        self.current_investigation.subject = SubjectDetails(
            subject_name="UNDER INVESTIGATION",
            subject_type="Unknown",
            national_id="Pending",
            account_numbers=[],
            known_addresses=[],
            phone_numbers=[],
            email_addresses=[],
            registration_number=""
        )
        
        self.current_investigation.report_id = f"FINREP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.current_investigation.generated_at = datetime.now().isoformat()
        
        self._generate_findings_from_data()
        self._generate_recommendations()
        self._save_complete_report()
        
        if console:
            console.print("\n[bold green]✓ Quick investigation completed![/bold green]")
            console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
            input()
    
    def live_financial_crime_monitor(self):
        """Live financial crime monitoring simulation"""
        if not RICH_AVAILABLE or not console:
            print("Live monitor requires rich library")
            return
        
        console.clear()
        
        header = Panel(
            Align.center(
                "[bold red]🌐 LIVE FINANCIAL CRIME MONITOR 🌐[/bold red]\n\n"
                f"[yellow]Monitoring Institution: {self.institution_details.institution_name if self.institution_details else 'Global Monitor'}[/yellow]\n"
                "[dim]Press Ctrl+C to stop monitoring[/dim]",
                vertical="middle"
            ),
            border_style="red",
            width=80
        )
        console.print(header)
        
        crimes = [
            ("💰 Suspicious Transaction", "National Bank of Malawi", "$2.5M", "High", "🇲🇼"),
            ("🌐 Crypto Alert", "Binance", "500 BTC", "Critical", "🌍"),
            ("🏦 Wire Fraud", "Standard Bank Malawi", "$750K", "High", "🇲🇼"),
            ("🆔 Identity Theft", "FDH Bank", "$150K", "Medium", "🇲🇼"),
            ("📈 Insider Trading", "London Stock Exchange", "$3.2M", "Critical", "🇬🇧"),
            ("🏢 Shell Company", "Delaware", "$8M", "High", "🇺🇸"),
            ("💸 Money Laundering", "Cayman Islands", "$12M", "Critical", "🇰🇾")
        ]
        
        alert_count = 0
        total_amount = 0
        
        try:
            with Live(refresh_per_second=4, screen=True) as live:
                for i in range(20):
                    crime, institution, amount, severity, location = random.choice(crimes)
                    severity_color = "red" if severity == "Critical" else "yellow"
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    alert_count += 1
                    
                    try:
                        if "BTC" in amount:
                            num_amount = float(amount.split()[0]) * 50000
                        else:
                            num_amount = float(amount.replace('$', '').replace('M', 'e6').replace('K', 'e3'))
                            if 'M' in amount:
                                num_amount = float(amount.replace('$', '').replace('M', '')) * 1000000
                            else:
                                num_amount = float(amount.replace('$', '').replace('K', '')) * 1000
                    except:
                        num_amount = 0
                    total_amount += num_amount
                    
                    left_panel = Panel(
                        f"[bold cyan]LIVE ALERTS[/bold cyan]\n\n"
                        f"[dim]Alert #{alert_count}[/dim]\n"
                        f"[{severity_color}]{severity}[/{severity_color}] {crime}\n"
                        f"Institution: {institution}\n"
                        f"Location: {location}",
                        title="[bold red]⚠️ ALERT[/bold red]",
                        border_style="red"
                    )
                    
                    center_panel = Panel(
                        f"[bold yellow]TRANSACTION DETAILS[/bold yellow]\n\n"
                        f"Amount: [green]{amount}[/green]\n"
                        f"Time: {timestamp}\n"
                        f"Risk Score: {random.randint(75, 100)}/100",
                        title="[bold cyan]DETAILS[/bold cyan]",
                        border_style="cyan"
                    )
                    
                    right_panel = Panel(
                        f"[bold green]STATISTICS[/bold green]\n\n"
                        f"Total Alerts: {alert_count}\n"
                        f"Total Value: ${total_amount:,.0f}\n"
                        f"Institution: {self.institution_details.institution_name if self.institution_details else 'Global'}",
                        title="[bold yellow]SUMMARY[/bold yellow]",
                        border_style="yellow"
                    )
                    
                    layout = Layout()
                    layout.split_row(
                        Layout(left_panel, ratio=1),
                        Layout(center_panel, ratio=1),
                        Layout(right_panel, ratio=1)
                    )
                    
                    live.update(layout)
                    time.sleep(random.uniform(0.5, 1.5))
            
            console.print(f"\n[bold green]✓ Monitoring session complete. {alert_count} potential crimes detected.[/bold green]")
            
        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]Monitoring stopped by user[/bold yellow]")
        
        console.print("\n[bold yellow]Press Enter to continue...[/bold yellow]")
        input()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def financial_forensics_menu():
    """
    Main entry point for DSTerminal integration
    """
    try:
        forensics = EnhancedFinancialForensics()
        forensics.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Financial Forensics interrupted by user{Style.RESET_ALL}" if 'Fore' in dir() else "\n[!] Interrupted")
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}" if 'Fore' in dir() else f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{Fore.CYAN}[*] Returning to DSTerminal...{Style.RESET_ALL}" if 'Fore' in dir() else "\n[*] Returning to DSTerminal...")
    time.sleep(1)


if __name__ == "__main__":
    print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}" if 'Fore' in dir() else "="*60)
    print(f"{Fore.CYAN}║     DSTERMINAL FINANCIAL FORENSICS - ENHANCED MODE           ║{Style.RESET_ALL}" if 'Fore' in dir() else "DSTERMINAL FINANCIAL FORENSICS - ENHANCED MODE")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}" if 'Fore' in dir() else "="*60)
    print(f"{Fore.YELLOW}[*] Reports saved to: ~/dsterminal_workspace/financial_reports/{Style.RESET_ALL}" if 'Fore' in dir() else "[*] Reports saved to: ~/dsterminal_workspace/financial_reports/")
    print(f"{Fore.YELLOW}[*] PDF Reports saved to: ~/dsterminal_workspace/financial_reports/pdf_reports/{Style.RESET_ALL}" if 'Fore' in dir() else "[*] PDF Reports saved to: ~/dsterminal_workspace/financial_reports/pdf_reports/")
    print(f"{Fore.YELLOW}[*] Install reportlab for PDF generation: pip install reportlab{Style.RESET_ALL}\n" if 'Fore' in dir() else "\n[*] Install reportlab for PDF generation: pip install reportlab\n")
    
    financial_forensics_menu()