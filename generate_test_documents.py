#!/usr/bin/env python3
"""
Generate test documents (PDFs and images) for LLM provider testing.

This script creates realistic receipts, invoices, and payment records
to test the document processing pipeline.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-27
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import random


def create_receipt_pdf(filename: str, data: dict):
    """Create a realistic receipt PDF."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Company header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, height - 1*inch, data['vendor'])

    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, data['address'])
    c.drawString(1*inch, height - 1.5*inch, data['phone'])

    # Receipt title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, height - 2*inch, "RECEIPT")

    # Receipt details
    c.setFont("Helvetica", 10)
    y_pos = height - 2.5*inch

    c.drawString(1*inch, y_pos, f"Date: {data['date']}")
    y_pos -= 0.3*inch
    c.drawString(1*inch, y_pos, f"Receipt #: {data['receipt_number']}")
    y_pos -= 0.5*inch

    # Items
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*inch, y_pos, "Description")
    c.drawString(4.5*inch, y_pos, "Amount")
    y_pos -= 0.05*inch
    c.line(1*inch, y_pos, 6*inch, y_pos)
    y_pos -= 0.3*inch

    c.setFont("Helvetica", 10)
    for item in data['items']:
        c.drawString(1*inch, y_pos, item['description'])
        c.drawString(4.5*inch, y_pos, f"${item['amount']:.2f}")
        y_pos -= 0.25*inch

    y_pos -= 0.2*inch
    c.line(1*inch, y_pos, 6*inch, y_pos)
    y_pos -= 0.3*inch

    # Totals
    c.setFont("Helvetica", 10)
    c.drawString(3.5*inch, y_pos, "Subtotal:")
    c.drawString(4.5*inch, y_pos, f"${data['subtotal']:.2f}")
    y_pos -= 0.25*inch

    c.drawString(3.5*inch, y_pos, f"Tax ({data['tax_rate']}%):")
    c.drawString(4.5*inch, y_pos, f"${data['tax_amount']:.2f}")
    y_pos -= 0.05*inch
    c.line(4.5*inch, y_pos, 6*inch, y_pos)
    y_pos -= 0.25*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(3.5*inch, y_pos, "TOTAL:")
    c.drawString(4.5*inch, y_pos, f"${data['total']:.2f}")

    # Payment method
    y_pos -= 0.5*inch
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_pos, f"Payment Method: {data['payment_method']}")

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(1*inch, 0.5*inch, "Thank you for your business!")

    c.save()
    print(f"✓ Created receipt: {filename}")


def create_invoice_pdf(filename: str, data: dict):
    """Create a realistic invoice PDF."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Company header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, height - 1*inch, data['company_name'])

    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, data['company_address'])
    c.drawString(1*inch, height - 1.5*inch, f"Phone: {data['company_phone']}")
    c.drawString(1*inch, height - 1.7*inch, f"Email: {data['company_email']}")

    # Invoice title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(5*inch, height - 1.5*inch, "INVOICE")

    # Invoice details
    c.setFont("Helvetica", 10)
    c.drawString(5*inch, height - 1.8*inch, f"Invoice #: {data['invoice_number']}")
    c.drawString(5*inch, height - 2.0*inch, f"Date: {data['date']}")
    c.drawString(5*inch, height - 2.2*inch, f"Due Date: {data['due_date']}")

    # Bill to
    y_pos = height - 2.5*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(1*inch, y_pos, "BILL TO:")
    y_pos -= 0.3*inch

    c.setFont("Helvetica", 10)
    c.drawString(1*inch, y_pos, data['customer_name'])
    y_pos -= 0.2*inch
    c.drawString(1*inch, y_pos, data['customer_address'])
    y_pos -= 0.2*inch
    if data.get('customer_email'):
        c.drawString(1*inch, y_pos, data['customer_email'])
        y_pos -= 0.5*inch
    else:
        y_pos -= 0.3*inch

    # Items table
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*inch, y_pos, "Description")
    c.drawString(4*inch, y_pos, "Qty")
    c.drawString(4.7*inch, y_pos, "Rate")
    c.drawString(5.5*inch, y_pos, "Amount")
    y_pos -= 0.05*inch
    c.line(1*inch, y_pos, 6.5*inch, y_pos)
    y_pos -= 0.3*inch

    c.setFont("Helvetica", 10)
    for item in data['items']:
        c.drawString(1*inch, y_pos, item['description'])
        c.drawString(4*inch, y_pos, str(item['quantity']))
        c.drawString(4.7*inch, y_pos, f"${item['rate']:.2f}")
        c.drawString(5.5*inch, y_pos, f"${item['amount']:.2f}")
        y_pos -= 0.25*inch

    y_pos -= 0.2*inch
    c.line(1*inch, y_pos, 6.5*inch, y_pos)
    y_pos -= 0.3*inch

    # Totals
    c.setFont("Helvetica", 10)
    c.drawString(4.5*inch, y_pos, "Subtotal:")
    c.drawString(5.5*inch, y_pos, f"${data['subtotal']:.2f}")
    y_pos -= 0.25*inch

    if data.get('tax_amount', 0) > 0:
        c.drawString(4.5*inch, y_pos, f"Tax ({data['tax_rate']}%):")
        c.drawString(5.5*inch, y_pos, f"${data['tax_amount']:.2f}")
        y_pos -= 0.05*inch
        c.line(5.5*inch, y_pos, 6.5*inch, y_pos)
        y_pos -= 0.25*inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(4.5*inch, y_pos, "TOTAL:")
    c.drawString(5.5*inch, y_pos, f"${data['total']:.2f}")

    # Payment terms
    y_pos -= 0.5*inch
    c.setFont("Helvetica", 9)
    c.drawString(1*inch, y_pos, "Payment Terms: Net 30")
    y_pos -= 0.2*inch
    c.drawString(1*inch, y_pos, "Please make payment to the address above.")

    c.save()
    print(f"✓ Created invoice: {filename}")


def generate_test_documents():
    """Generate a variety of test documents."""
    output_dir = Path("samples/test_documents")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Receipt 1: Office supplies
    receipt1_data = {
        'vendor': 'Office Depot',
        'address': '123 Business Blvd, Business City, BC 12345',
        'phone': '(555) 123-4567',
        'date': '2025-10-20',
        'receipt_number': 'R20251020-001',
        'items': [
            {'description': 'Paper (5 reams)', 'amount': 24.99},
            {'description': 'Pens (box of 12)', 'amount': 8.99},
            {'description': 'Stapler', 'amount': 12.50},
        ],
        'subtotal': 46.48,
        'tax_rate': 13,
        'tax_amount': 6.04,
        'total': 52.52,
        'payment_method': 'Visa ****1234'
    }
    create_receipt_pdf(str(output_dir / "receipt_office_supplies.pdf"), receipt1_data)

    # Receipt 2: Restaurant (meals and entertainment)
    receipt2_data = {
        'vendor': 'The Gourmet Bistro',
        'address': '456 Main Street, Downtown, BC 23456',
        'phone': '(555) 234-5678',
        'date': '2025-10-21',
        'receipt_number': 'R20251021-089',
        'items': [
            {'description': 'Business Lunch for 2', 'amount': 45.00},
            {'description': 'Beverages', 'amount': 8.00},
            {'description': 'Gratuity (18%)', 'amount': 9.54},
        ],
        'subtotal': 53.00,
        'tax_rate': 13,
        'tax_amount': 6.89,
        'total': 69.43,
        'payment_method': 'Mastercard ****5678'
    }
    create_receipt_pdf(str(output_dir / "receipt_restaurant.pdf"), receipt2_data)

    # Receipt 3: Gas/Travel
    receipt3_data = {
        'vendor': 'QuickFill Gas Station',
        'address': '789 Highway 1, Suburb, BC 34567',
        'phone': '(555) 345-6789',
        'date': '2025-10-22',
        'receipt_number': 'GAS-20251022-456',
        'items': [
            {'description': 'Regular Unleaded - 45.2L', 'amount': 72.32},
        ],
        'subtotal': 72.32,
        'tax_rate': 5,
        'tax_amount': 3.62,
        'total': 75.94,
        'payment_method': 'Debit ****9012'
    }
    create_receipt_pdf(str(output_dir / "receipt_gas.pdf"), receipt3_data)

    # Invoice 1: Consulting services (income)
    invoice1_data = {
        'company_name': 'Tech Consulting Inc.',
        'company_address': '100 Professional Way, Suite 200, Tech City, BC 45678',
        'company_phone': '(555) 456-7890',
        'company_email': 'billing@techconsulting.com',
        'invoice_number': 'INV-2025-1001',
        'date': '2025-10-23',
        'due_date': '2025-11-22',
        'customer_name': 'ACME Corporation',
        'customer_address': '500 Corporate Plaza, Business District, BC 56789',
        'customer_email': 'accounts@acmecorp.com',
        'items': [
            {'description': 'Software Development - 40 hours', 'quantity': 40, 'rate': 150.00, 'amount': 6000.00},
            {'description': 'Project Management - 10 hours', 'quantity': 10, 'rate': 125.00, 'amount': 1250.00},
        ],
        'subtotal': 7250.00,
        'tax_rate': 0,
        'tax_amount': 0.00,
        'total': 7250.00
    }
    create_invoice_pdf(str(output_dir / "invoice_consulting.pdf"), invoice1_data)

    # Invoice 2: Product sale (income)
    invoice2_data = {
        'company_name': 'Software Solutions Ltd.',
        'company_address': '200 Innovation Drive, Tech Park, BC 67890',
        'company_phone': '(555) 567-8901',
        'company_email': 'sales@softwaresolutions.com',
        'invoice_number': 'INV-2025-1045',
        'date': '2025-10-24',
        'due_date': '2025-11-23',
        'customer_name': 'StartUp Ventures Inc.',
        'customer_address': '300 Startup Lane, Innovation Hub, BC 78901',
        'customer_email': 'finance@startupventures.com',
        'items': [
            {'description': 'Enterprise Software License (Annual)', 'quantity': 1, 'rate': 5000.00, 'amount': 5000.00},
            {'description': 'Premium Support Package', 'quantity': 1, 'rate': 1500.00, 'amount': 1500.00},
        ],
        'subtotal': 6500.00,
        'tax_rate': 13,
        'tax_amount': 845.00,
        'total': 7345.00
    }
    create_invoice_pdf(str(output_dir / "invoice_software_license.pdf"), invoice2_data)

    # Receipt 4: Internet/Phone (utilities)
    receipt4_data = {
        'vendor': 'TeleCom Services',
        'address': '400 Network Street, Connection City, BC 89012',
        'phone': '1-800-TELECOM',
        'date': '2025-10-25',
        'receipt_number': 'BILL-202510-789456',
        'items': [
            {'description': 'Business Internet (100Mbps)', 'amount': 89.99},
            {'description': 'Business Phone Line', 'amount': 45.00},
        ],
        'subtotal': 134.99,
        'tax_rate': 13,
        'tax_amount': 17.55,
        'total': 152.54,
        'payment_method': 'Auto-Pay (Bank Account)'
    }
    create_receipt_pdf(str(output_dir / "receipt_internet_phone.pdf"), receipt4_data)

    print(f"\n✅ Generated 6 test documents in {output_dir}/")
    print("\nTest documents created:")
    print("  EXPENSES:")
    print("    - receipt_office_supplies.pdf ($52.52)")
    print("    - receipt_restaurant.pdf ($69.43)")
    print("    - receipt_gas.pdf ($75.94)")
    print("    - receipt_internet_phone.pdf ($152.54)")
    print("  INCOME:")
    print("    - invoice_consulting.pdf ($7,250.00)")
    print("    - invoice_software_license.pdf ($7,345.00)")


if __name__ == "__main__":
    generate_test_documents()
