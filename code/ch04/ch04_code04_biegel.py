import pandas as pd
import sqlite3, requests

db = sqlite3.connect('taxi.db')
db.execute('''CREATE TABLE IF NOT EXISTS trips (
    pickup_time TEXT, distance REAL, fare REAL, tip REAL, total REAL)''')
    
def download():
  url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-06.parquet'
  with open('taxi.parquet', 'wb') as f:
    f.write(requests.get(url).content)
    
def process():
  df = pd.read_parquet('taxi.parquet')
  clean = df[
    (df['fare_amount'] > 0) & (df['fare_amount'] < 500) &
    (df['trip_distance'] > 0) & (df['trip_distance'] < 100)
  ][['tpep_pickup_datetime', 'trip_distance', 'fare_amount', 'tip_amount', 'total_amount']]
        
  clean.columns = ['pickup_time', 'distance', 'fare', 'tip', 'total']
        
  clean.to_sql('trips', db, if_exists='append', index=False)
  print(f"Complete: {len(clean):,} trips loaded")
     
def summarize():
  stats = pd.read_sql_query("""
    SELECT COUNT(*) trips, ROUND(AVG(distance),1) avg_miles, 
      ROUND(AVG(fare),2) avg_fare, ROUND(SUM(total)) revenue
    FROM trips""", db)
  print("\n", stats.to_string(index=False))

download()
process()
summarize()