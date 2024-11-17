import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_user_availability(user: str, availability_df: pd.DataFrame) -> dict:
    try:
        user_data = availability_df[
            (availability_df['user'] == user) & 
            (availability_df['available'] == 1)
        ]
        
        available_slots = {}
        for _, row in user_data.iterrows():
            dt = pd.to_datetime(row['time'])
            date = dt.date()
            hour = dt.hour
            
            if date not in available_slots:
                available_slots[date] = set()
            available_slots[date].add(hour)
            
        print(f"User {user} availability: {available_slots}")
        return available_slots
    except Exception as e:
        print(f"Error getting availability for {user}: {str(e)}")
        return {}

def find_best_time(event: pd.Series, availability_df: pd.DataFrame, start_hour: int, end_hour: int) -> dict:
    try:
        wished_users = [u.strip() for u in str(event['wished_by']).split(',') if u.strip()]
        print(f"Processing event '{event['name']}' for users: {wished_users}")

        user_availabilities = {}
        for user in wished_users:
            avail = get_user_availability(user, availability_df)
            if avail:
                user_availabilities[user] = avail

        if not user_availabilities:
            print("No availability data found for any users")
            return None

        duration = int(float(event['end_time'])) - int(float(event['start_time']))
        print(f"Event duration: {duration} hours")

        best_slot = None
        max_attendance = 0

        # Get dates where at least one user is available
        all_dates = set()
        for user_avail in user_availabilities.values():
            all_dates.update(user_avail.keys())

        print(f"Checking dates: {all_dates}")
        for date in all_dates:
            # Check each possible starting hour
            for start_hour in range(24 - duration):
                end_hour = start_hour + duration
                available_users = []

                for user in wished_users:
                    if user in user_availabilities:
                        user_hours = user_availabilities[user].get(date, set())
                        # Check if user is available for the entire duration
                        hours_needed = set(range(start_hour, end_hour))
                        if hours_needed.issubset(user_hours):
                            available_users.append(user)

                attendance = (len(available_users) / len(wished_users)) * 100
                print(f"Time slot {start_hour}:00-{end_hour}:00 on {date}: {attendance}% attendance")
                
                if attendance > max_attendance:
                    max_attendance = attendance
                    best_slot = {
                        'event_name': event['name'],
                        'date': date.strftime('%Y-%m-%d'),
                        'start_hour': start_hour,
                        'end_hour': end_hour,
                        'available_users': available_users,
                        'attendance_percentage': attendance,
                        'day_name': date.strftime('%A')
                    }

        if best_slot:
            print(f"Found best slot: {best_slot}")
        return best_slot
    except Exception as e:
        print(f"Error finding best time: {str(e)}")
        return None

def schedule_events(events_df: pd.DataFrame, availability_df: pd.DataFrame, 
                   start_hour: int, end_hour: int) -> list:
    try:
        scheduled_events = []
        print(f"Processing {len(events_df)} events")
        
        for idx, event in events_df.iterrows():
            print(f"Processing event {idx}: {event['name']}")
            print(f"Wished by: {event['wished_by']}")
            
            # Changed this line to only pass the required arguments
            best_slot = find_best_time(event, availability_df)
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