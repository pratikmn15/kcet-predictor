from fpdf import FPDF
from io import BytesIO
from datetime import datetime

def create_pdf(data, columns, year, round_name):
    """Create a PDF file in memory and return the bytes"""
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
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')