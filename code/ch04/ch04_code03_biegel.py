import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('maintenance.db')
    
    # Run the target query
    query = '''
        SELECT WT.DESCRIPTION, WT.COMPLETED_DATE
        FROM WORK_ORDER_TASK WT, WORK_ORDER W, ASSET A
        WHERE WT.STATUS = 'COMPLETED'
        AND WT.COMPLETED_BY = 'John Smith'
        AND WT.COMPLETED_DATE <= W.SCHEDULED_DATE
        AND WT.WORK_ORDER_ID = W.WORK_ORDER_ID
        AND W.ASSET_ID = A.ASSET_ID
        AND A.asset_id = 'F1'
    '''
    
    print("Tasks completed on/before scheduled date for asset F1:")
    results = pd.read_sql_query(query, conn)
    
    if results.empty:
        print("No results found")
    else:
        print(results.to_string(index=False))
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"Database error: {e}")
except FileNotFoundError:
    print("Error: maintenance.db file not found")
    print("Please ensure the database file exists in the current directory")