import datetime
from datetime import datetime as dt

def get_parsed_time(t: int):
    if not t:
        return '00:00'
    
    return dt.fromtimestamp(t / 1000).strftime('%H:%M')

