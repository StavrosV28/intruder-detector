import sqlite3

def create_db():
    with sqlite3.connect("intruder-detector.db") as connection:
        # cursor object
        cursor = connection.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS detections (
                            detection_id INTEGER PRIMARY KEY, 
                            timestamp REAL, 
                            class_label TEXT, 
                            confidence_interval REAL, 
                            coordinates TEXT) ''')
        connection.commit()
        
        
def insert_row(timestamp, class_label, confidence_interval, coordinates):
    with sqlite3.connect("intruder-detector.db") as connection:
        cursor = connection.cursor()
        
        connection.execute('''INSERT INTO detections (timestamp, 
                            class_label, 
                            confidence_interval, 
                            coordinates) VALUES (?, ?, ?, ?)''', (timestamp, class_label, confidence_interval, coordinates))
        
        connection.commit()