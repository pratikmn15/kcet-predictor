from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from sqlalchemy import create_engine, text
from pdf_handler import create_pdf
from file_cleanup import cleanup_manager
import os
import atexit

app = Flask(__name__)

DATABASE_URI = 'sqlite:///instance/cutoffs.db'
engine = create_engine(DATABASE_URI)

def init_cleanup_manager():
    """Initialize the cleanup manager if it's not already running"""
    if not cleanup_manager.running:
        cleanup_manager.start()
        # Register cleanup_all to run when the app shuts down
        atexit.register(cleanup_manager.stop)
        atexit.register(cleanup_manager.cleanup_all)

# Only start the cleanup manager in the main process
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    init_cleanup_manager()

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
        filename = create_pdf(data, columns, year, round_name)
        filepath = os.path.join('static', 'pdfs', filename)
        return jsonify({"filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download-pdf/<filename>')
def download_pdf(filename):
    try:
        return send_from_directory('static/pdfs', filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
