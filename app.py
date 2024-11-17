from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
from datetime import datetime, timedelta
import os
from config import START_HOUR, END_HOUR, TIME_INTERVAL
from Algo import get_user_availability, find_best_time, schedule_events


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
        # Add date column if it doesn't exist
        if 'date' not in events.columns:
            events['date'] = ''
            events.to_csv(EVENTS_FILE, index=False)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        events = pd.DataFrame(columns=['name', 'date', 'start_time', 'end_time', 'creator', 'wished_by'])
        events.to_csv(EVENTS_FILE, index=False)

@app.route('/events', methods=['GET', 'POST'])
def events():
    if 'user' not in session:
        return redirect('/login')
        
    if request.method == 'POST':
        data = request.json
        df = pd.read_csv(EVENTS_FILE)
        
        new_event = {
            'name': data['name'],
            'date': data['date'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'creator': session['user'],
            'wished_by': session['user']
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
    
    return jsonify({'error': 'Already wished to attend this event'}), 400@app.route('/wish_to_attend', methods=['POST'])
def wish_to_attend():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json
    df = pd.read_csv(EVENTS_FILE)
    
    mask = ((df['name'] == data['name']) & 
            (df['date'] == data['date']) &
            (df['start_time'] == float(data['start_time'])) & 
            (df['end_time'] == float(data['end_time'])))
    
    if df[mask].empty:
        return jsonify({'error': 'Event not found'}), 404
        
    event_idx = df[mask].index[0]
    
    current_wishes = str(df.at[event_idx, 'wished_by']).split(',') if pd.notna(df.at[event_idx, 'wished_by']) else []
    current_wishes = [w.strip() for w in current_wishes if w.strip()]
    
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
    
    mask = ~((df['name'] == data['name']) & 
           (df['date'] == data['date']) &
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
    group_avail = df.groupby('time')['available'].agg(['sum', 'count']).reset_index()
    group_avail['percentage'] = (group_avail['sum'] / group_avail['count']) * 100
    
    return jsonify(group_avail.to_dict(orient='records'))

@app.route('/generate_schedule', methods=['GET', 'POST'])
def generate_schedule_page():
    if 'user' not in session:
        return redirect('/login')
    return render_template('generate_schedule.html', user=session['user'])

@app.route('/update_config', methods=['POST'])
def update_config():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.json
    global START_HOUR, END_HOUR
    
    START_HOUR = int(data['start_hour'])
    END_HOUR = int(data['end_hour'])
    
    # Update config.py file
    with open('config.py', 'w') as f:
        f.write(f'START_HOUR = {START_HOUR}\n')
        f.write(f'END_HOUR = {END_HOUR}\n')
        f.write('TIME_INTERVAL = 1')
    
    return jsonify({
        'START_HOUR': START_HOUR,
        'END_HOUR': END_HOUR
    })
@app.route('/optimize_schedule', methods=['POST'])
def optimize_schedule():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        events_df = pd.read_csv(EVENTS_FILE)
        availability_df = pd.read_csv(AVAILABILITY_FILE)
        
        # Convert time column to datetime
        availability_df['time'] = pd.to_datetime(availability_df['time'])
        
        if availability_df.empty:
            return jsonify({'error': 'No availability data found'})
            
        # Add the required START_HOUR and END_HOUR parameters
        scheduled_events = schedule_events(
            events_df, 
            availability_df,
            START_HOUR,
            END_HOUR
        )
        return jsonify(scheduled_events)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def schedule_events(events_df: pd.DataFrame, availability_df: pd.DataFrame, 
                   start_hour: int, end_hour: int) -> list:
    try:
        scheduled_events = []
        print(f"Processing {len(events_df)} events")
        
        for idx, event in events_df.iterrows():
            print(f"Processing event {idx}: {event['name']}")
            print(f"Wished by: {event['wished_by']}")
            
            best_slot = find_best_time(event, availability_df, start_hour, end_hour)
            if best_slot:
                print(f"Found slot for event {event['name']}: {best_slot}")
                scheduled_events.append(best_slot)
            else:
                print(f"No suitable slot found for event {event['name']}")
        
        print(f"Total scheduled events: {len(scheduled_events)}")
        scheduled_events.sort(key=lambda x: x['attendance_percentage'], reverse=True)
        return scheduled_events
    except Exception as e:
        print(f"Error scheduling events: {str(e)}")
        return []
    
if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)

