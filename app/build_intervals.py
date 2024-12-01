import json
from datetime import datetime, timedelta

def time_to_datetime(time_str):
    return datetime.strptime(time_str, "%H:%M:%S")

def build_intervals(timestamps, max_gap_minutes=5):
    if not timestamps:
        return []
    
    timestamps = sorted(timestamps, key=time_to_datetime)
    intervals = []
    start = timestamps[0]
    prev = timestamps[0]
    
    max_gap = timedelta(minutes=max_gap_minutes) 
    
    for current in timestamps[1:]:
        if (time_to_datetime(current) - time_to_datetime(prev)) > max_gap:
            intervals.append(f"{start}-{prev}")
            start = current  
        prev = current
    
    intervals.append(f"{start}-{prev}")
    return intervals
