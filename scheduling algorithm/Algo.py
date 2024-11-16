import pandas as pd
import numpy as np

def scheduleMix(schedules: list[np.ndarray], group: list[int]) -> list[np.ndarray]: 
    return np.sum(schedules[group], axis = 0)

class event:
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

def algorithe(events: event, schedules: np.ndarray):
    eventMixes = [scheduleMix(schedules, oneEvent.group) for oneEvent in events]
    everbodyEvents = [oneEvent for oneEvent in events if oneEvent.everybodyNeeded]
    for everbodyEvent in everbodyEvents:
        pass