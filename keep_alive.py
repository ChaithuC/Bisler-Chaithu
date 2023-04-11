import os
from threading import Thread
from flask_wtf import FlaskForm
from data_handlers import Database
from flask import Flask, render_template , jsonify  
from wtforms import StringField, SubmitField


app = Flask('')
app.config['SECRET_KEY'] = 'mysecretkey'

class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Submit')

@app.route('/')
def home():
    return "Bot Gadu Called at time "
    

@app.route('/get_sales_data', methods=['GET', 'POST'])
def get_sales_data():
    print("sales data for web function invoked...")
    loading = True
    data = Database.get_sales_data(True)
    loading = False
    return render_template('sales_data.html', dataframe=data[0].to_html(), loading=loading, dict=data[1])



@app.route('/get_data_api/<password>')
def get_data_api(password):
    if password == os.getenv("sales_distribution"):
        data, meta = Database.get_sales_data(True)
        response_data = {'data': data.to_dict(orient='records'), 'meta': meta}
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

