import mgclient

# Connect and build graph
conn = mgclient.connect(host="127.0.0.1", port=7687)
c = conn.cursor()

# Clear and create graph
c.execute("MATCH (n) DETACH DELETE n")
c.execute(
    """
CREATE (hotel:Building {name: 'Hotel'})
CREATE (l1:Level {name: 'level1'})
CREATE (l2:Level {name: 'level2'})
CREATE (room:Room {name: 'Room 209'})
CREATE (thermo:Equipment {name: 'Thermostat 24967', WiFiSignalStrength: -70, BatteryPercentage: 83})
CREATE (l1)-[:isPartOf]->(hotel)
CREATE (l2)-[:isPartOf]->(hotel)
CREATE (room)-[:isPartOf]->(l2)
CREATE (thermo)-[:locatedIn]->(room)
"""
)

# Run traversals
print("=== Equipment on Level2 ===")
c.execute(
    """
MATCH (l:Level {name: 'level2'})<-[:isPartOf]-(room)-[:locatedIn]-(e:Equipment) 
RETURN l.name, e.name, e.BatteryPercentage
"""
)
for row in c.fetchall():
    print(f"{row[0]} has {row[1]} (Battery: {row[2]}%)")

conn.close()
