from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from sqlalchemy import create_engine, text
from pdf_handler import create_pdf
from io import BytesIO
import os

app = Flask(__name__)

DATABASE_URI = 'sqlite:///instance/cutoffs.db'
engine = create_engine(DATABASE_URI)

@app.route('/',methods=['POST','GET'])
def home():
    return render_template('index.html')

@app.route('/submit',methods=['POST','GET'])
def query_entries():
    if request.method == 'POST':
        cat = request.form.get('cat')
        lrank = request.form.get('lrank')
        urank = request.form.get('urank')
        round = request.form.get('round')
        query = f"SELECT BRANCH, {cat}, COLLEGES FROM '{round}' WHERE {cat} BETWEEN {lrank} AND {urank} ORDER BY {cat} ASC;"

        response = {"rows": [], "columns": []}
        try:
            with engine.connect() as connection:
                result = connection.execute(text(query))
                rows = result.fetchall()
                response["rows"] = [tuple(row) for row in rows] 
                response["columns"] = list(result.keys())
        except Exception as e:
            return f"An error occurred: {e}"

        return jsonify({"message": response})
    else:
        return redirect(url_for('home'))

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json.get('rows', [])
    columns = request.json.get('columns', [])
    round_code = request.json.get('round')
    
    if not round_code or len(round_code) < 6:
        return jsonify({"error": "Invalid round format"}), 400

    year = round_code[0:4]
    round_type = round_code[4:6]
    
    if round_type == "r1":
        round_name = "1st Round"
    elif round_type == "r2":
        round_name = "2nd Round"
    elif round_type == "r3":
        round_name = "2nd Extended Round"
    else:
        return jsonify({"error": "Invalid round code"}), 400

    if not data or not columns:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Generate PDF in memory
        pdf_content = create_pdf(data, columns, year, round_name)
        
        # Create BytesIO object
        pdf_buffer = BytesIO(pdf_content)
        pdf_buffer.seek(0)
        
        # Generate filename for download
        filename = f'kcet_results_{year}_{round_type}.pdf'
        
        # Send file directly from memory
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
