
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

DATABASE_URI = 'sqlite:///instance/cutoffs.db'
engine = create_engine(DATABASE_URI)

@app.route('/',methods=['POST','GET'])
def home():
    # svg = render_template('templates/to.svg')
    # svg = './templates/to.svg'
    return render_template('index.html')

@app.route('/submit',methods=['POST','GET'])
def query_entries():
    cat = request.form.get('cat')
    lrank = request.form.get('lrank')
    urank = request.form.get('urank')
    round = request.form.get('round')
    query = f"SELECT BRANCH, {cat}, COLLEGES FROM '{round}' WHERE {cat} BETWEEN {lrank} AND {urank};"

    rows = []
    columns = []
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
    except Exception as e:
        return f"An error occurred: {e}"

    return render_template('index.html',rows=rows, columns= columns,cat=cat,lrank=lrank,urank=urank,rounds=round)

if __name__ == '__main__':
    app.run(debug=True)
