from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('calendar.html')

if __name__ == '__main__':
    app.run(debug=True)
