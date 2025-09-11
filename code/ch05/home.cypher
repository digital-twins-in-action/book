// This script creates a graph data model for a house, including its physical structure, meters, and equipment.
CREATE
// Create the top-level Land node and its direct components
(l:Land {name: '10 North St.'})<-[:isPartOf]-(h:Building {name: 'House', address: '10 North Ave'}),
(l)<-[:isPartOf]-(g:Garage {name: 'Garage'}),
(l)<-[:isPartOf]-(sp:Space {name: 'Swimming pool'}),
(l)<-[:locatedIn]-(rt:PlumbingStorageTank {name: 'Rainwater Tank'}),

// Create the Building's components: Levels and Roof, and change the relationship to isPartOf
(h)<-[:isPartOf]-(l1:Level {name: 'Level 1'}),
(h)<-[:isPartOf]-(l2:Level {name: 'Level 2'}),
(h)<-[:isPartOf]-(r:RoofLevel {name: 'Roof'}),

// Create all Rooms on Level 1 and link them
(l1)<-[:isPartOf]-(br1:Room {name: 'Bedroom 1'}),
(l1)<-[:isPartOf]-(br2:Room {name: 'Bedroom 2'}),
(l1)<-[:isPartOf]-(br3:Room {name: 'Bedroom 3'}),
(l1)<-[:isPartOf]-(b:Room {name: 'Bathroom', label: 'Bathroom'}),
(l1)<-[:isPartOf]-(hl:Room {name: 'Hallway', label: 'Hallway'}),
(l1)<-[:isPartOf]-(laundry:Room {name: 'Laundry'}),
(l1)<-[:isPartOf]-(lr:LivingRoom {name: 'Lounge'}),
(l1)<-[:isPartOf]-(rumpus:LivingRoom {name: 'Rumpus'}),
(l1)<-[:isPartOf]-(k:CookingRoom {name: 'Kitchen'}),

// Create Meters located in the House
(h)<-[:locatedIn]-(em:ElectricityMeter {name: 'Electricity Meter'}),
(h)<-[:locatedIn]-(wm:WaterMeter {name: 'Water Meter'}),

// Create Faucet located in the House
(h)<-[:locatedIn]-(ot1:Faucet {name: 'Front Outdoor Tap'}),
(h)<-[:locatedIn]-(ot2:Faucet {name: 'Back Outdoor Tap'}),

//Swimming pool motor
(sp)<-[:locatedIn]-(mtr:Motor {name: 'Pool pump'}),

// Create Electrical Equipment and their locations
(laundry)<-[:locatedIn]-(wmach:ElectricalEquipment {name: 'Washing Machine'}),
(k)<-[:locatedIn]-(ref:ElectricalEquipment {name: 'Refrigerator'}),
(k)<-[:locatedIn]-(ov:ElectricalEquipment {name: 'Oven'}),
(g)<-[:locatedIn]-(f:ElectricalEquipment {name: 'Freezer'}),
(laundry)<-[:locatedIn]-(de:ElectricalEquipment {name: 'Dehumidifier'}),
(r)<-[:locatedIn]-(pv:ElectricalEquipment {name: 'PV Array'}),

// Create HVAC Equipment and associated document
(lr)<-[:locatedIn]-(ac:HVACEquipment {name: 'Air Conditioner'}),
(ac)-[:hasDocument]->(sm1:Document {name: 'Service Manual'}),
(ac)-[:hasDocument]->(mr1:Document {name: 'Maintenance Record'}),

(mtr)-[:hasDocument]->(sm2:Document {name: 'Service Manual'}),

// Create all Sensors and the nodes they serve
(sp)<-[:serves]-(phs1:Sensor {name: 'ph_sensor_1'}),
(em)<-[:serves]-(ps1:PowerSensor {name: 'power_meter_1'}),
(wmach)<-[:serves]-(ps2:PowerSensor {name: 'power_meter_2'}),
(mtr)<-[:serves]-(ps3:PowerSensor {name: 'power_meter_3'}),
(ref)<-[:serves]-(ps4:PowerSensor {name: 'power_meter_4'}),
(wm)<-[:serves]-(vfs1:VolumeFlowSensor {name: 'camera_sensor_1'}),
(lr)<-[:serves]-(aqs:PM10AirQualitySensor {name: 'air_quality_sensor_1'}),
(br1)<-[:serves]-(ts1:TemperatureSensor {name: 'temp_sensor_1', sensorId: 'a84041ce41845d13'}),
(br2)<-[:serves]-(ts2:TemperatureSensor {name: 'temp_sensor_2'}),
(br3)<-[:serves]-(ts3:TemperatureSensor {name: 'temp_sensor_3'}),
(lr)<-[:serves]-(ts4:TemperatureSensor {name: 'temp_sensor_4', sensorId: '24e124710b423527'}),
(l)<-[:serves]-(ts5:TemperatureSensor {name: 'temp_sensor_5', sensorId: 'a840411971871c86'}),
(ot1)<-[:serves]-(vfs2:VolumeFlowSensor {name: 'flow_meter_2'}),
(ot2)<-[:serves]-(vfs3:VolumeFlowSensor {name: 'flow_meter_3'}),
(wmach)<-[:serves]-(vfs4:VolumeFlowSensor {name: 'flow_meter_4'}),
(l)<-[:serves]-(ms1:PercentSensor {name: 'soil_moisture_sensor_1'}),
(l)<-[:serves]-(ms2:PercentSensor {name: 'soil_moisture_sensor_2'}),
(rt)<-[:serves]-(ls1:PercentSensor {name: 'level_sensor_1'});