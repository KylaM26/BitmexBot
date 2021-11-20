import pandas as pd

time_frames = {
    "1m" : "1T",
    "3m" : "3T",
    "5m" : "5T",
    "10m" : "10T",
    "15m" : "15T",
    "30m" : "30T",
    "45m" : "45T",
    "1h" : "60min",
    "2h" : "120min",
    "4h" : "240min",
    "1D" : "1D",
    "W"  : "W",
    "M"  : "M",
    "Q"  : "Q"
}

def resample_dataframe(df: pd.DataFrame, time_frame:str):
    return df.resample(time_frames[time_frame]).agg({'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume':'sum'})