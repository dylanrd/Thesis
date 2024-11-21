import serial  # import Serial Library
import numpy as np  # Import numpy
import matplotlib
from matplotlib import pyplot as plt
import time
matplotlib.use('TkAgg')

fiveV_lines = 15
read_lines = 16

tempF = []
pressure = []
arduinoData = serial.Serial('com9', 115200)  # Creating our serial object named arduinoData

fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((read_lines, fiveV_lines)), cmap='plasma')
plt.colorbar(heatmap)
cnt = 0
sensorTracker = 0
initialiser = 0
mean = 0
std = 0
max = np.zeros(read_lines * fiveV_lines, dtype=float)
current = np.zeros(read_lines * fiveV_lines, dtype=float)

# plt.show(block=False)
while True:  # While loop that loops forever
    # tim = time.perf_counter()
    arduinoString = arduinoData.readline()  # read the line of text from the serial port
    #print(arduinoString)
    dataArray = arduinoString.decode('utf-8').split(',')  # Split it into an array called dataArray
    temp = float(dataArray[0])
    index = int(dataArray[1])

    if initialiser < 10:
        max[index] += temp

        if index == 0:
            initialiser += 1
        if initialiser >= 10:
            max = max / float(10)
            # mean = np.mean(1. / max)
            # std = np.std(1. / max)
    else:
        current[index] = temp

        if index == 0:
            norm = (current/max)
            minimum = current.min()
            maximum = current.max()
            normalisation = (current - minimum) / (maximum - minimum)
            #
            # deviation = (max - current)
            #
            # max_deviation = np.max(deviation)
            # normalized_values = deviation / max
            G = (1. /current) - mean + 4*std
            R = 1/G
            # normalized_values = np.clip(normalized_values, 0, 1)
            normalisationArray = norm.reshape(fiveV_lines, read_lines)
            #print(G)
            heatmap.set_data(normalisationArray)
            # end_time = time.perf_counter()  # End time
            # duration = end_time - tim
            #
            # print(f"Time taken: {duration} seconds")
            plt.draw()
            plt.pause(0.1)
