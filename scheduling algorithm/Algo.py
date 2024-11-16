import pandas as pd
import numpy as np

def scheduleMix(schedules: list[np.ndarray], group: list[int]) -> list[np.ndarray]: 
    return np.sum(schedules[group], axis = 0)

class Event:
    scheduled = False
    def __init__(self, eventLength: int, startTime : list, endTime: list, group: np.ndarray, everybodyNeeded: bool): #event length is stored in terms of how many time interval blocks it takes.
        """ 
        eventLength is stored as an int being the amount of time blocks it would take up
        start Time and end time need some work as how they will be stored is still in question
        """
        self.eventLength = eventLength
        self.startTime = startTime
        self.endTime = endTime
        self.group = group
        self.everybodyNeeded = everybodyNeeded

    def scheduleEvent(self, schedules: np.ndarray , time: list, cancelIfEverybodyNeeded: bool):
        "Time is stored as a 3d cordinate being (day of the week, time of day by block #)"
        if cancelIfEverybodyNeeded:
            scheduleMix(schedules, self.group)
            for idx in range(self.eventLength): # Asummes 1 means the spot is filled already
                if not schedules[idx]:
                    return
        for member in self.group:
            for idx in range(self.eventLength): 
                if not schedules[(member,idx)]:
                    schedules[(member,idx)] = 1
        self.scheduled = True



def bestEventTime(schedules: list[np.ndarray], event: Event):
    """ 
    generator to yield the best times in succession from a pre-computed list
    """
    mix = scheduleMix(schedules, event.group)
    
    # Create a list to store all possible time slots with their scores
    all_slots = []
    
    # Generate all possible time slots
    for i, day in enumerate(mix):
        for idx in range(len(day)-event.length):
            array = day[idx:idx+event.length]
            score = max(array) 
            all_slots.append({
                'day': i,
                'start': idx,
                'score': score
            })
    
    all_slots.sort(key=lambda x: x['score'])
    
    # Yield each slot in order
    for slot in all_slots:
        yield slot



def simpleAlgowrithe(events: list[Event], schedules: list[np.ndarray]):
    """
    Schedule events optimally, prioritizing events with larger groups
    
    Args:
        events: list of Event objects to schedule
        schedules: list of numpy arrays representing individual schedules
    
    Returns:
        np.ndarray: Map of scheduled events where the value is the event index + 1 
                   (0 means no event scheduled)
    """
    # Initialize the schedule map with correct shape based on first schedule
    scheduledEventMap = np.zeros_like(schedules[0])
    
    # Sort events by group size in descending order (largest first)
    events.sort(key=lambda x: len(x.group), reverse=True)
    
    for event_idx, event in enumerate(events):
        # Create generator for this event's possible times
        time_generator = bestEventTime(schedules, event)
        
        scheduled = False
        for time_slot in time_generator:
            day, start = time_slot
            
            # Check if this slot is free in the scheduled event map
            slot_is_free = True
            for t in range(event.length):
                if scheduledEventMap[day][start + t] != 0:
                    slot_is_free = False
                    break
            
            if slot_is_free:
                # Schedule the event (mark with event_idx + 1 to distinguish from 0)
                for t in range(event.length):
                    scheduledEventMap[day][start + t] = event_idx + 1
                scheduled = True
                break
        
        if not scheduled:
            print(f"Warning: Could not schedule event {event_idx}")
    
    return scheduledEventMap