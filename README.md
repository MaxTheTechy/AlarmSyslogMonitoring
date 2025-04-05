# AlarmMon


To log all SNMP traps received on your system, follow these steps based on your OS:

---

### **1. Install SNMP Trap Daemon (`snmptrapd`)**
If `snmptrapd` is not installed, install it first:

#### **Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install snmptrapd -y
```

#### **RHEL/CentOS:**
```bash
sudo yum install net-snmp net-snmp-utils -y
```

#### **Arch Linux:**
```bash
sudo pacman -Sy net-snmp
```

---

### **2. Configure `snmptrapd` to Log Traps**
Edit the SNMP trap daemon config file:
```bash
sudo nano /etc/snmp/snmptrapd.conf
```
Add the following lines:
```
authCommunity log,execute,net public
outputOption s
```
- `authCommunity log,execute,net public` → Allows SNMP traps with the community "public" (adjust if needed).
- `outputOption s` → Ensures logs are written to syslog.

Save the file (`CTRL + X`, then `Y`, then `Enter`).

---

### **3. Enable and Start `snmptrapd`**
Start and enable the SNMP trap daemon:
```bash
sudo systemctl start snmptrapd
sudo systemctl enable snmptrapd
```

---

### **4. Verify SNMP Trap Logs**
Check logs using:
```bash
sudo journalctl -u snmptrapd -f
```
Or:
```bash
sudo tail -f /var/log/syslog  # (Debian/Ubuntu)
sudo tail -f /var/log/messages  # (RHEL/CentOS)
```

---

### **5. (Optional) Log Traps to a Custom File**
To log SNMP traps to a separate file, modify `/etc/snmp/snmptrapd.conf`:
```
authCommunity log,execute,net public
outputOption s
logOption f /var/log/snmptraps.log
```
Create the log file and set permissions:
```bash
sudo touch /var/log/snmptraps.log
sudo chmod 666 /var/log/snmptraps.log
```
Restart the service:
```bash
sudo systemctl restart snmptrapd
```
Now, traps will be logged in `/var/log/snmptraps.log`:
```bash
tail -f /var/log/snmptraps.log
```

---

This setup will capture and log all incoming SNMP traps. 


##

# Great! 🎉 Your `snmptrapd` service is now running successfully from the **system version** (`/usr/sbin/snmptrapd`).  

### **Verify It's Working**  
Now, let's confirm that SNMP traps are being received and logged:  

#### **1. Check if `snmptrapd` is Listening on Port 162**
Run:
```bash
sudo ss -tuln | grep 162
```
You should see an output like:
```
udp   UNCONN  0  0  0.0.0.0:162  0.0.0.0:*  
udp6  UNCONN  0  0  [::]:162     [::]:*  
```
This confirms that `snmptrapd` is listening for SNMP traps.

#### **2. Check Logs for SNMP Traps**
By default, SNMP traps are logged in `/var/log/syslog` (Ubuntu). To monitor incoming traps in real time, run:
```bash
sudo tail -f /var/log/syslog | grep snmptrapd
```
If you're using RHEL/CentOS, check:
```bash
sudo tail -f /var/log/messages | grep snmptrapd
```

#### **3. Send a Test SNMP Trap**
From another device (or the same machine), send a test SNMP trap:
```bash
snmptrap -v 2c -c public 127.0.0.1 "" .1.3.6.1.4.1.8072.2.3.0.1
```
If everything is working, you should see the trap logged in `/var/log/syslog`.

---

### **(Optional) Log Traps to a Separate File**
If you want to log SNMP traps to a dedicated file instead of `/var/log/syslog`, edit the `snmptrapd` config:
```bash
sudo nano /etc/snmp/snmptrapd.conf
```
Add:
```
authCommunity log,execute,net public
logOption f /var/log/snmptraps.log
```
Create the log file and set permissions:
```bash
sudo touch /var/log/snmptraps.log
sudo chmod 666 /var/log/snmptraps.log
```
Restart `snmptrapd`:
```bash
sudo systemctl restart snmptrapd
```
Now, traps will be logged in `/var/log/snmptraps.log`:
```bash
tail -f /var/log/snmptraps.log
```

---

Everything looks good now! 🚀 Let me know if you need more help.
















To monitor the status of your application (e.g., ensuring that the SNMP process is running, and the application is decoding SNMP traps as expected), you can set up a simple monitoring system using SNMP to periodically check the status of the application and the SNMP process. Here’s a breakdown of how you can approach this:

### Steps:

1. **Monitor the SNMP Trap Daemon (snmptrapd) Process:**
   - Ensure that the `snmptrapd` process is running.
   - If it stops, you can use a monitoring system (such as a simple script, Nagios, or Prometheus) to alert you when it's not running.

2. **Monitor the SNMP Application Logic:**
   - Implement periodic health checks within your application to verify that it is decoding SNMP traps.
   - Return specific SNMP traps or system metrics to monitor its operational status.

3. **Create an SNMP Monitoring Trap for Your Application:**
   - Define a custom SNMP trap that indicates the status of your application (running/decoding properly).
   - If any issue occurs (e.g., `snmptrapd` isn't running, or your app isn't processing traps), send a specific SNMP trap that indicates a failure.

4. **Use Another SNMP Server for Monitoring:**
   - Set up another SNMP server that listens for the health monitoring traps you send from your application.
   - The monitoring server can then alert you if it doesn’t receive the expected traps or receives a failure trap.

### 1. **Monitor the SNMP Trap Daemon Process (snmptrapd)**

To ensure that the SNMP trap daemon (`snmptrapd`) is running, you can use a simple script to check for the process and restart it if needed.

#### Example Script to Monitor snmptrapd:

```bash
#!/bin/bash
# Check if snmptrapd is running
if ! pgrep -x "snmptrapd" > /dev/null; then
    echo "$(date) - snmptrapd is not running. Restarting..." >> /var/log/snmp_monitor.log
    systemctl start snmptrapd
else
    echo "$(date) - snmptrapd is running." >> /var/log/snmp_monitor.log
fi
```

You can set up this script to run periodically (e.g., every minute) using a cron job:

```bash
* * * * * /path/to/your/script.sh
```

This script will check if the `snmptrapd` service is running and will restart it if it’s stopped.

### 2. **Monitor the Application's Trap Decoding Status**

You should have a monitoring mechanism in place to check whether your application is successfully processing SNMP traps and decoding them. This could be as simple as a heartbeat or status trap sent by your application at regular intervals.

For example, every time your application processes an SNMP trap, it could send a custom "status" SNMP trap indicating that the application is working correctly. If it encounters an error (e.g., cannot decode the trap, or any other failure), the application can send a failure trap.

#### Sending a Heartbeat SNMP Trap (via your Application)

Using the `pysnmp` library, you can send a heartbeat trap from your application.

```python
from pysnmp.hlapi import *

def send_heartbeat_trap():
    # Send a simple heartbeat SNMP trap
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget(('127.0.0.1', 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.4.1.12345.0')  # Custom OID for heartbeat
            ).addVarBinds(
                ('1.3.6.1.4.1.12345.1', 'heartbeat')
            )
        )
    )
    
    if errorIndication:
        print(f"Error sending trap: {errorIndication}")
    else:
        print("Heartbeat trap sent successfully")

# Call this function at intervals in your app
send_heartbeat_trap()
```

### 3. **Create Custom SNMP Traps for Failure Detection**

You can extend the logic in your application to send a failure trap if it encounters an issue (e.g., cannot decode a trap, application crashes, etc.).

For example, if your application fails to decode a trap or encounters an error, you can send a failure trap with a specific message like:

```python
def send_failure_trap():
    errorIndication, errorStatus, errorIndex, varBinds = next(
        sendNotification(
            SnmpEngine(),
            CommunityData('public'),
            UdpTransportTarget(('127.0.0.1', 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity('1.3.6.1.4.1.12345.0')  # Custom OID for failure trap
            ).addVarBinds(
                ('1.3.6.1.4.1.12345.2', 'failure')
            )
        )
    )
    
    if errorIndication:
        print(f"Error sending trap: {errorIndication}")
    else:
        print("Failure trap sent successfully")

# Call this function whenever there's an issue decoding a trap
send_failure_trap()
```

### 4. **Monitoring SNMP Server:**

Now that your application is sending either heartbeat or failure traps, you need to configure an SNMP manager (monitoring server) that listens to these traps.

You can configure tools like **Nagios**, **Zabbix**, **Prometheus**, or even use a simple SNMP listener to capture these traps.

For example, an SNMP manager can be configured to receive traps from the SNMP server running on `localhost` and use those traps to monitor the application's status.

#### Example of an SNMP Listener using `snmptrapd`:

1. **Edit the `snmptrapd.conf` file** to log incoming traps and add custom OIDs for heartbeat/failure:
   
```bash
# /etc/snmp/snmptrapd.conf
authCommunity log,execute,net public
disableAuthorization yes
logOption f /var/log/snmptraps.log
# Trap OID for heartbeat and failure
trap2sink 127.0.0.1
```

2. **Monitoring the Log**: You can use a script to check if the expected traps are received and act accordingly (e.g., alerting if no heartbeat is received for a certain amount of time).

```bash
#!/bin/bash
# Check the snmptrapd logs for heartbeat traps and alert if failure traps are found
if grep -q "failure" /var/log/snmptraps.log; then
    echo "Failure detected! Sending alert..."
    # You can send an email, Slack message, or use any other alerting mechanism here
else
    echo "Application is running fine."
fi
```

### 5. **Automate the Monitoring with a Cron Job**

You can automate the monitoring and alerting script using cron:

```bash
* * * * * /path/to/your/monitoring_script.sh
```

This will check the `snmptrapd` logs every minute and alert you if a failure is detected.

---

By following this approach, you will have a monitoring system that ensures both the SNMP trap process (`snmptrapd`) and your application logic are continuously running and functional. If any issue occurs (e.g., traps are not being decoded), you will be alerted via the failure traps sent to the monitoring server.
