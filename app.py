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

    try:
        events = pd.read_csv(EVENTS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        events = pd.DataFrame(columns=['name', 'start_time', 'end_time', 'creator', 'wished_by'])
        events.to_csv(EVENTS_FILE, index=False)

# Modify the events route to handle POST
@app.route('/events', methods=['GET', 'POST'])
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
            'creator': session['user'],
            'wished_by': session['user']  # Set the creator as the first person in wished_by
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
    
    # Check if wished_by column exists, if not add it
    if 'wished_by' not in df.columns:
        df['wished_by'] = ''
        df.to_csv(EVENTS_FILE, index=False)
    
    events_dict = df.to_dict(orient='records')
    
    # Add has_wished flag for each event
    for event in events_dict:
        wishes = str(event.get('wished_by', '')).split(',') if pd.notna(event.get('wished_by', '')) else []
        event['has_wished'] = session['user'] in [w for w in wishes if w]
        
    return jsonify(events_dict)

@app.route('/wish_to_attend', methods=['POST'])
def wish_to_attend():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json
    df = pd.read_csv(EVENTS_FILE)
    
    # Find the specific event
    mask = ((df['name'] == data['name']) & 
            (df['start_time'] == float(data['start_time'])) & 
            (df['end_time'] == float(data['end_time'])))
    
    if df[mask].empty:
        return jsonify({'error': 'Event not found'}), 404
        
    event_idx = df[mask].index[0]
    
    # Get current wishes as a list
    current_wishes = str(df.at[event_idx, 'wished_by']).split(',') if pd.notna(df.at[event_idx, 'wished_by']) else []
    current_wishes = [w.strip() for w in current_wishes if w.strip()]
    
    # Add new wish if not already present
    if session['user'] not in current_wishes:
        current_wishes.append(session['user'])
        df.at[event_idx, 'wished_by'] = ','.join(current_wishes)
        df.to_csv(EVENTS_FILE, index=False)
        return jsonify({'status': 'success'})
    
    return jsonify({'error': 'Already wished to attend this event'}), 400


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
            return redirect('/home')
        return "Invalid credentials"
    
    return render_template('login.html')

@app.route('/')
def firstlogin():
    return redirect('/login')

@app.route('/calendar')
def return_calendar():
    return render_template('calendar.html', user = session["user"])

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('base.html', user=session['user'])

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
    group_avail = df.grouspby('time')['available'].agg(['sum', 'count']).reset_index()
    group_avail['percentage'] = (group_avail['sum'] / group_avail['count']) * 100
    
    return jsonify(group_avail.to_dict(orient='records'))

if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)

