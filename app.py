from flask import Flask, render_template, request, jsonify, session, redirect
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Data file paths
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
AVAILABILITY_FILE = os.path.join(DATA_DIR, "availability.csv")

def initialize_data():
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Initialize users
    try:
        users = pd.read_csv(USERS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        users = pd.DataFrame({
            'username': ['User1', 'User2'],
            'password': ['password1', 'password2']
        })
        users.to_csv(USERS_FILE, index=False)

    # Initialize availability - FIXED: Moved outside of users exception block
    try:
        availability = pd.read_csv(AVAILABILITY_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Create time slots for the next 7 days
        start_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        times = pd.date_range(start_date, end_date, freq="1H")
        times = times[times.hour.isin(range(8, 22))]  # Only include 8 AM to 9 PM
        
        # Create availability data
        data = []
        users = pd.read_csv(USERS_FILE)  # Read users again to ensure we have the latest data
        for user in users['username']:
            for time in times:
                data.append({
                    'user': user,
                    'time': time.strftime('%Y-%m-%d %H:%M'),
                    'available': 0  # 0 = unavailable, 1 = available
                })
        
        availability = pd.DataFrame(data)
        availability.to_csv(AVAILABILITY_FILE, index=False)

    return users, availability  # Return both DataFrames for verification

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
        user_availability = df[df['user'] == session['user']]
        return jsonify(user_availability.to_dict(orient='records'))
    
    elif request.method == 'POST':
        data = request.json
        df = pd.read_csv(AVAILABILITY_FILE)
        
        # Update availability
        df.loc[(df['user'] == session['user']) & 
               (df['time'] == data['time']), 'available'] = data['available']
        
        df.to_csv(AVAILABILITY_FILE, index=False)
        return jsonify({'status': 'success'})

@app.route('/group_availability')
def group_availability():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    df = pd.read_csv(AVAILABILITY_FILE)
    total_users = len(df['user'].unique())
    
    # Calculate group availability
    group_avail = df.groupby('time')['available'].agg(['sum', 'count']).reset_index()
    group_avail['percentage'] = (group_avail['sum'] / group_avail['count']) * 100
    
    return jsonify(group_avail.to_dict(orient='records'))

if __name__ == '__main__':
    initialize_data()
    app.run(debug=True)