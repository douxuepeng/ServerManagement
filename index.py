from flask import Flask,render_template,request
import time
from config.config import port
from sqlitedb.sqlitedb import sqlClass
sql = sqlClass()
app=Flask(__name__)
app.secret_key='1996-05-16'
from route.login import cklogin
@app.route('/',methods=['GET'])
@cklogin()
def index():
    return render_template('index.html')
if __name__ == '__main__':
    from route import *
    app.run(host='0.0.0.0',port=port,debug = False)