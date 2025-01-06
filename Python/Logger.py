import serial
import time
import csv


arduinoData = serial.Serial('com9', 2000000)

# Log file name
log_file = "sensor_readings.csv"

start_index = 0
# Open the log file in append mode
with open(log_file, mode="a", newline="") as file:
    writer = csv.writer(file)

    # Write a header row if the file is empty
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Sensor ID", "Resistance (Ohms)"])
    timestamp = 0
    # Continuously read from the serial port
    while True:
        try:

            # Read a line of data from the serial port
            line = arduinoData.readline().decode("utf-8").strip()
            if not line:
                continue  # Skip empty lines

            # Parse the sensor ID and resistance
            parts = line.split(",")
            if len(parts) != 3:
                print(f"Malformed data: {line}")
                continue

            resistance = float(parts[0])
            sensor_id = int(parts[1])
            #timestamp = str(parts[2])
            if sensor_id == start_index:
                print('captured an iteration')
                timestamp_temp = time.time()

                # Convert to a human-readable format with milliseconds
                formatted_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_temp))
                milliseconds = int((timestamp_temp - int(timestamp_temp)) * 1000)
                timestamp = formatted_timestamp + '.' + str(milliseconds)

            # Write the data to the CSV file
            writer.writerow([timestamp, sensor_id, resistance])
            #print(f"Logged: {timestamp}, Sensor {sensor_id}, Resistance {resistance} Ohms")

        except KeyboardInterrupt:
            print("Logging stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")