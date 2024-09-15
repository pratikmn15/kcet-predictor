
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, text

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
        query = f"SELECT BRANCH, {cat}, COLLEGES FROM '{round}' WHERE {cat} BETWEEN {lrank} AND {urank};"

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

if __name__ == '__main__':
    app.run(debug=True)
