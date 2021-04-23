import datetime
from datetime import datetime as dt

def get_parsed_time(d: str):
    if not d:
        return '00:00'
    # return dt.fromtimestamp(t / 1000).strftime('%H:%M')
    return dt.strptime(d, '%Y-%m-%d %H:%M').strftime('%H:%M')

