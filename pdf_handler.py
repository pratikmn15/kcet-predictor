from fpdf import FPDF
import os
from datetime import datetime
from file_cleanup import cleanup_manager

def create_pdf(data, columns, year, round_name):
    """Create a PDF file with the query results"""
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'KCET College Predictor Results', 0, 1, 'C')
    pdf.ln(5)
    
    # Add round information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'Year: {year} - {round_name}', 0, 1, 'C')
    pdf.ln(5)
    
    # Add timestamp
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'R')
    pdf.ln(10)
    
    # Table headers
    pdf.set_font('Arial', 'B', 10)
    col_widths = [pdf.w * 0.22, pdf.w * 0.1, pdf.w * 0.6]  # Adjust column widths as needed
    for i, header in enumerate(columns):
        pdf.cell(col_widths[i], 10, str(header), 1, 0, 'C')
    pdf.ln()
    
    # Table data
    pdf.set_font('Arial', '', 9)
    for row in data:
        for i, item in enumerate(row):
            if i == 2:  # For the third column
                x, y = pdf.get_x(), pdf.get_y()
                pdf.multi_cell(col_widths[i], 10, str(item), 1, 'C')
                pdf.set_xy(x + col_widths[i], y)  # Move to the next cell position
            else:
                pdf.cell(col_widths[i], 10, str(item), 1, 0, 'C')
        pdf.ln()
    
    # Generate unique filename
    filename = f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join('static', 'pdfs', filename)
    
    # Ensure directory exists
    os.makedirs(os.path.join('static', 'pdfs'), exist_ok=True)
    
    # Save PDF
    pdf.output(filepath)
    
    # Register file for cleanup
    cleanup_manager.track_file(filepath)
    
    return filename