from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
from datetime import datetime, timedelta
import os
from config import START_HOUR, END_HOUR, TIME_INTERVAL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Data file paths
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
AVAILABILITY_FILE = os.path.join(DATA_DIR, "availability.csv")

def initialize_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    try:
        users = pd.read_csv(USERS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        users = pd.DataFrame({
            'username': ['User1', 'User2'],
            'password': ['password1', 'password2']
        })
        users.to_csv(USERS_FILE, index=False)

    try:
        availability = pd.read_csv(AVAILABILITY_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Create full day range (0-23 hours)
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        times = pd.date_range(start=start_date, end=end_date, freq="1H")
        
        data = []
        users = pd.read_csv(USERS_FILE)
        for user in users['username']:
            for time in times:
                data.append({
                    'user': user,
                    'time': time.strftime('%Y-%m-%d %H:%M'),
                    'available': 0
                })
        
        availability = pd.DataFrame(data)
        availability.to_csv(AVAILABILITY_FILE, index=False)

    return users, availability

@app.route('/config')
def get_config():
    return jsonify({
        'START_HOUR': START_HOUR,
        'END_HOUR': END_HOUR
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = pd.read_csv(USERS_FILE)
        user = users[(users['username'] == username) & (users['password'] == password)]
        
        if not user.empty:
            session['user'] = username
            return redirect('/')
        return "Invalid credentials"
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('calendar.html', user=session['user'])

@app.route('/availability', methods=['GET', 'POST'])
def availability():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    if request.method == 'GET':
        df = pd.read_csv(AVAILABILITY_FILE)
        df['hour'] = pd.to_datetime(df['time']).dt.hour
        
        # Filter by configured hours
        user_availability = df[
            (df['user'] == session['user']) & 
            (df['hour'] >= START_HOUR) & 
            (df['hour'] <= END_HOUR)
        ]
        return jsonify(user_availability.to_dict(orient='records'))
    
    elif request.method == 'POST':
        data = request.json
        df = pd.read_csv(AVAILABILITY_FILE)
        
        df.loc[(df['user'] == session['user']) & 
               (df['time'] == data['time']), 'available'] = data['available']
        
        df.to_csv(AVAILABILITY_FILE, index=False)
        return jsonify({'status': 'success'})

@app.route('/group_availability')
def group_availability():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    df = pd.read_csv(AVAILABILITY_FILE)
    df['hour'] = pd.to_datetime(df['time']).dt.hour
    
    # Filter by configured hours
    df = df[(df['hour'] >= START_HOUR) & (df['hour'] <= END_HOUR)]
    
    total_users = len(df['user'].unique())
    group_avail = df.groupby('time')['available'].agg(['sum', 'count']).reset_index()
    group_avail['percentage'] = (group_avail['sum'] / group_avail['count']) * 100
    
    return jsonify(group_avail.to_dict(orient='records'))

if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)