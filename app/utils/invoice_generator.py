from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os
from flask import current_app


def generate_invoice_pdf(invoice):
    """Generate PDF invoice"""
    try:
        # Create filename
        filename = f"invoice_{invoice.invoice_number}_{datetime.utcnow().timestamp()}.pdf"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12
        )
        
        # Title
        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice info table
        invoice_info_data = [
            ['Invoice Number:', invoice.invoice_number, 'Invoice Date:', invoice.issue_date.strftime('%Y-%m-%d')],
            ['Due Date:', invoice.due_date.strftime('%Y-%m-%d'), 'Status:', invoice.status.upper()],
        ]
        
        info_table = Table(invoice_info_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EEF7')),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Bill To section
        story.append(Paragraph("Bill To:", heading_style))
        story.append(Paragraph(f"{invoice.user.full_name}<br/>{invoice.user.email}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice details table
        details_data = [
            ['Description', 'Amount', 'Currency'],
            [invoice.description, f"${invoice.amount:.2f}", invoice.currency],
        ]
        
        details_table = Table(details_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('RIGHTPADDING', (1, 0), (-1, -1), 10),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Total section
        total_data = [
            ['Total Amount:', f"${invoice.amount:.2f} {invoice.currency}"],
        ]
        
        total_table = Table(total_data, colWidths=[4*inch, 2*inch])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        
        story.append(total_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = "Thank you for your business! | Amahle Rentals"
        story.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=1,
            textColor=colors.grey
        )))
        
        # Build PDF
        doc.build(story)
        
        return filename
    
    except Exception as e:
        print(f"Error generating invoice PDF: {str(e)}")
        return None


def generate_lease_agreement_pdf(lease):
    """Generate lease agreement PDF"""
    try:
        filename = f"lease_{lease.lease_number}_{datetime.utcnow().timestamp()}.pdf"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        )
        
        story.append(Paragraph("RESIDENTIAL LEASE AGREEMENT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Lease details
        lease_info = f"""
        <b>Lease Number:</b> {lease.lease_number}<br/>
        <b>Property:</b> {lease.property.title}, {lease.property.address}<br/>
        <b>Landlord:</b> {lease.property.landlord.full_name}<br/>
        <b>Tenant:</b> {lease.property.landlord.full_name}<br/>
        <b>Lease Start Date:</b> {lease.start_date.strftime('%Y-%m-%d')}<br/>
        <b>Lease End Date:</b> {lease.end_date.strftime('%Y-%m-%d')}<br/>
        <b>Monthly Rent:</b> ${lease.monthly_rent:.2f}<br/>
        <b>Security Deposit:</b> ${lease.security_deposit:.2f if lease.security_deposit else 0.00}<br/>
        """
        
        story.append(Paragraph(lease_info, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Terms and conditions
        story.append(Paragraph("<b>Terms and Conditions:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        terms = """
        1. <b>Rent Payment:</b> Tenant agrees to pay rent in full by the due date each month.<br/>
        2. <b>Property Maintenance:</b> Tenant agrees to maintain the property in good condition.<br/>
        3. <b>Utilities:</b> Tenant is responsible for utilities unless otherwise specified.<br/>
        4. <b>Occupancy:</b> Property is for residential use only.<br/>
        5. <b>Subletting:</b> Subletting is not permitted without landlord's written consent.<br/>
        6. <b>Damage:</b> Tenant is liable for damages beyond normal wear and tear.<br/>
        7. <b>Entry Rights:</b> Landlord has the right to enter for maintenance with proper notice.<br/>
        8. <b>Termination:</b> Either party may terminate with 30 days' written notice.<br/>
        """
        
        story.append(Paragraph(terms, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Signature section
        story.append(Paragraph("<b>Signatures:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        signature_data = [
            ['Landlord Signature:', '_' * 30, 'Date:', '_' * 20],
            ['', '', '', ''],
            ['Tenant Signature:', '_' * 30, 'Date:', '_' * 20],
        ]
        
        sig_table = Table(signature_data, colWidths=[2*inch, 2*inch, 1*inch, 1.5*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        story.append(sig_table)
        
        doc.build(story)
        
        return filename
    
    except Exception as e:
        print(f"Error generating lease agreement PDF: {str(e)}")
        return None
