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

# Add to your existing constants in app.py
EVENTS_FILE = os.path.join(DATA_DIR, "events.csv")

# Add to initialize_data() function
def initialize_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Your existing users and availability initialization...

    try:
        events = pd.read_csv(EVENTS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        events = pd.DataFrame(columns=['name', 'start_time', 'end_time', 'creator'])
        events.to_csv(EVENTS_FILE, index=False)

# Modify the events route to handle POST
@app.route('/events', methods=['GET', 'POST'])
def events():
    if 'user' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        data = request.json
        df = pd.read_csv(EVENTS_FILE)
        
        new_event = {
            'name': data['name'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'creator': session['user']
        }
        
        df = pd.concat([df, pd.DataFrame([new_event])], ignore_index=True)
        df.to_csv(EVENTS_FILE, index=False)
        
        return jsonify({'status': 'success'})
        
    return render_template('events.html', user=session['user'])

@app.route('/get_events')
def get_events():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    df = pd.read_csv(EVENTS_FILE)
    user_events = df[df['creator'] == session['user']]
    return jsonify(user_events.to_dict(orient='records'))

@app.route('/delete_event', methods=['POST'])
def delete_event():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json
    df = pd.read_csv(EVENTS_FILE)
    
    # Fixed deletion logic - remove matching rows
    mask = ~((df['name'] == data['name']) & 
           (df['start_time'] == float(data['start_time'])) & 
           (df['end_time'] == float(data['end_time'])) & 
           (df['creator'] == session['user']))
    
    df = df[mask]
    df.to_csv(EVENTS_FILE, index=False)
    return jsonify({'status': 'success'})

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

