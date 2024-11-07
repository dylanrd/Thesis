import serial  # import Serial Library
import numpy as np  # Import numpy
import matplotlib

matplotlib.use('TkAgg')

from drawnow import *

fiveV_lines = 8
read_lines = 16

tempF = []
pressure = []
arduinoData = serial.Serial('com3', 115200)  # Creating our serial object named arduinoData

fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((read_lines, fiveV_lines)), cmap='plasma', aspect='auto')
plt.colorbar(heatmap)
cnt = 0
sensorTracker = 0
initialiser = 0

max = np.zeros(read_lines * fiveV_lines)
current = np.zeros(read_lines * fiveV_lines)

# plt.show(block=False)
while True:  # While loop that loops forever

    arduinoString = arduinoData.readline()  # read the line of text from the serial port

    dataArray = arduinoString.decode('utf-8').split(',')  # Split it into an array called dataArray
    temp = float(dataArray[0])
    index = int(dataArray[1])

    if initialiser < 10:
        max[index] += temp

        if index == 0:
            initialiser += 1
        if initialiser >= 10:
            max = max / float(10)

    else:
        current[index] = temp

        if index == 0:
            norm = (current/max)
            normalisationArray = norm.reshape(fiveV_lines, read_lines)

            heatmap.set_data(normalisationArray)

            plt.draw()
            plt.pause(0.1)
