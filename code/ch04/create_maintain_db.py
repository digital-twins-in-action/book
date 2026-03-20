#!/usr/bin/env python3
"""
Create maintenance.db file with sample data
Run: python create_maintenance_db.py
"""

import sqlite3
from datetime import datetime, timedelta

# Create database file
conn = sqlite3.connect('maintenance.db')

# Create tables
conn.executescript('''
    DROP TABLE IF EXISTS WORK_ORDER_TASK;
    DROP TABLE IF EXISTS WORK_ORDER;
    DROP TABLE IF EXISTS ASSET;
    
    CREATE TABLE ASSET (
        asset_id TEXT PRIMARY KEY,
        name TEXT,
        number TEXT,
        location TEXT
    );
    
    CREATE TABLE WORK_ORDER (
        work_order_id TEXT PRIMARY KEY,
        asset_id TEXT,
        work_type TEXT,
        priority TEXT,
        status TEXT,
        created_date TEXT,
        scheduled_date TEXT,
        started_date TEXT,
        completed_date TEXT,
        estimated_cost REAL,
        FOREIGN KEY (asset_id) REFERENCES ASSET (asset_id)
    );
    
    CREATE TABLE WORK_ORDER_TASK (
        task_id TEXT PRIMARY KEY,
        work_order_id TEXT,
        description TEXT,
        status TEXT,
        completed_date TEXT,
        completed_by TEXT,
        FOREIGN KEY (work_order_id) REFERENCES WORK_ORDER (work_order_id)
    );
''')

# Insert sample data
base_date = datetime.now() - timedelta(days=30)

# Assets
conn.executemany('INSERT INTO ASSET VALUES (?, ?, ?, ?)', [
    ('F1', 'Conveyor Belt #1', 'CB-001', 'Factory Floor A'),
    ('F2', 'Pump System #2', 'PS-002', 'Utility Room'),
    ('F3', 'HVAC Unit #3', 'HV-003', 'Roof Level 2'),
])

# Work Orders
conn.executemany('INSERT INTO WORK_ORDER VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [
    ('WO001', 'F1', 'Preventive', 'Medium', 'Completed', 
     (base_date - timedelta(days=5)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=2)).strftime('%Y-%m-%d'),
     base_date.strftime('%Y-%m-%d'),
     (base_date + timedelta(days=1)).strftime('%Y-%m-%d'), 850.00),
    
    ('WO002', 'F1', 'Corrective', 'High', 'In Progress',
     (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=10)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=8)).strftime('%Y-%m-%d'),
     None, 1200.00),
    
    ('WO003', 'F2', 'Preventive', 'Low', 'Completed',
     (base_date - timedelta(days=10)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=5)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=3)).strftime('%Y-%m-%d'),
     (base_date + timedelta(days=4)).strftime('%Y-%m-%d'), 450.00),
])

# Work Order Tasks
conn.executemany('INSERT INTO WORK_ORDER_TASK VALUES (?, ?, ?, ?, ?, ?)', [
    ('T001', 'WO001', 'Inspect belt tension', 'COMPLETED', 
     base_date.strftime('%Y-%m-%d'), 'John Smith'),
    ('T002', 'WO001', 'Lubricate bearings', 'COMPLETED',
     (base_date + timedelta(days=1)).strftime('%Y-%m-%d'), 'John Smith'),
    ('T003', 'WO001', 'Check motor alignment', 'COMPLETED',
     base_date.strftime('%Y-%m-%d'), 'Jane Doe'),
    
    ('T004', 'WO002', 'Replace worn belt', 'In Progress',
     None, None),
    ('T005', 'WO002', 'Test system operation', 'Pending',
     None, None),
    
    ('T006', 'WO003', 'Check pump pressure', 'COMPLETED',
     (base_date + timedelta(days=4)).strftime('%Y-%m-%d'), 'Mike Johnson'),
    ('T007', 'WO003', 'Replace filter', 'COMPLETED',
     (base_date + timedelta(days=4)).strftime('%Y-%m-%d'), 'Mike Johnson'),
])

conn.commit()
conn.close()

print("Created maintenance.db with sample data")
print("Run 'python maintenance_query.py' to test the query")