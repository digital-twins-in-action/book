import duckdb, requests, time

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
with open('taxi.parquet', 'wb') as f:
    f.write(requests.get(url).content)

start_time = time.time()
result = duckdb.query("""
    SELECT 
        COUNT(*) as trips,
        ROUND(AVG(fare_amount), 2) as avg_fare,
        ROUND(MIN(fare_amount), 2) as min_fare,
        ROUND(MAX(fare_amount), 2) as max_fare
    FROM 'taxi.parquet'
""").fetchone()
query_time = time.time() - start_time

print(f"\nResults: {result[0]:,} trips, avg ${result[1]}, range ${result[2]}-${result[3]}")
print(f"⚡ Query time: {query_time:.3f} seconds")
