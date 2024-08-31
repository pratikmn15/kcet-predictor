
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

DATABASE_URI = 'sqlite:///2023r3.db'
engine = create_engine(DATABASE_URI)

@app.route('/',methods=['POST','GET'])
def home():
    return render_template('index.html')

@app.route('/submit',methods=['POST','GET'])
def query_entries():
    cat = request.form.get('cat')
    lrank = request.form.get('lrank')
    urank = request.form.get('urank')
    query = f"SELECT BRANCH, {cat}, COLLEGES FROM cutoff WHERE {cat} BETWEEN {lrank} AND {urank};"

    rows = []
    columns = []
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
    except Exception as e:
        return f"An error occurred: {e}"

    return render_template('index.html',rows=rows, columns= columns,cat=cat,lrank=lrank,urank=urank)

if __name__ == '__main__':
    app.run(debug=True)
