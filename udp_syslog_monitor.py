#!/usr/bin/env python3
import os
import re
import socket
import sqlite3
import logging
import time
import signal
import sys

# Configuration
DB_FILE = "/rsyslogapp/alarmsys.db"
TARGET_SERVER = "192.168.200.64"
TARGET_PORT = 5001
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 514  # Standard syslog port
LOG_FILE = "/var/log/alarmsys-monitor.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logging.info("Shutting down syslog monitor...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def search_database(sensor_id):
    """
    Search the database for the sensor ID and return the corresponding record.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Using LocationID as the field to match with sensor_id
        cursor.execute("SELECT LocationID, AlarmType, URN FROM alarms WHERE LocationID = ?", (sensor_id,))
        record = cursor.fetchone()
        
        conn.close()
        
        if record:
            logging.info(f"Found record for sensor {sensor_id}: {record}")
        else:
            logging.warning(f"No record found for sensor {sensor_id}")
            
        return record
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return None

def send_notification(location_id, alarm_type, urn):
    """
    Send notification to the target server in the format LocationID|AlarmType|URN|
    """
    message = f"{location_id}|{alarm_type}|{urn}|"
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        sock.connect((TARGET_SERVER, TARGET_PORT))
        sock.sendall(message.encode())
        sock.close()
        
        logging.info(f"Notification sent: {message}")
        return True
    except socket.error as e:
        logging.error(f"Failed to send notification: {e}")
        return False

def process_syslog_message(message):
    """
    Process a syslog message and extract sensor ID if it matches our patterns.
    """
    # Log the full message for debugging
    logging.debug(f"Processing message: {message}")
    
    # Pattern 1: "NB: Sensor Disconnected for SENSOR_ID"
    match1 = re.search(r"NB: Sensor Disconnected for (.+?)($|\s)", message)
    
    # Pattern 2: "NB: Sensor Abnormal SENSOR_ID"
    match2 = re.search(r"NB: Sensor Abnormal (.+?)($|\s)", message)
    
    if match1:
        sensor_id = match1.group(1).strip()
        logging.info(f"Detected sensor disconnection for: {sensor_id}")
        return sensor_id
    elif match2:
        sensor_id = match2.group(1).strip()
        logging.info(f"Detected sensor abnormal for: {sensor_id}")
        return sensor_id
    
    return None

def start_udp_server():
    """
    Start a UDP server to listen for syslog messages.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the address and port
    sock.bind((LISTEN_HOST, LISTEN_PORT))
    
    logging.info(f"Listening for syslog messages on UDP {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"Listening for syslog messages on UDP {LISTEN_HOST}:{LISTEN_PORT}")
    
    while True:
        try:
            # Receive data from the socket
            data, addr = sock.recvfrom(4096)  # Buffer size is 4096 bytes
            message = data.decode('utf-8')
            
            # Log the message
            logging.debug(f"Received message from {addr}: {message}")
            print(f"Received message from {addr}: {message}")
            
            # Process the message
            sensor_id = process_syslog_message(message)
            
            if sensor_id:
                # Look up the sensor ID in the database
                record = search_database(sensor_id)
                
                if record:
                    location_id, alarm_type, urn = record
                    # Send notification to target server
                    send_notification(location_id, alarm_type, urn)
                else:
                    logging.warning(f"Sensor ID {sensor_id} not found in database")
                    
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            continue

if __name__ == "__main__":
    try:
        start_udp_server()
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        sys.exit(1)
