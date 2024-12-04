import numpy as np
import numpy.random
import matplotlib.pyplot as plt
from matplotlib import cm
import serial
from Filters import *
from crosstalk import fixed_point_recover_conductances, compute_equivalent_conductance
# # To generate some test data
# x = np.random.randn(500)
# y = np.random.randn(500)

fiveV_lines = 15
read_lines = 16

tempF = []
pressure = []
arduinoData = serial.Serial('com9', 115200)  # Creating our serial object named arduinoData

# Sample data
x = np.arange(read_lines)  # X positions
y = np.arange(fiveV_lines)  # Y positions
x, y = np.meshgrid(x, y)  # Create a grid
x = x.ravel()  # Flatten to 1D array
y = y.ravel()

z = np.zeros_like(x)
max = np.zeros(read_lines * fiveV_lines, dtype=float)
i = 0
loop = 0
while True:  # While loop that loops forever
    # tim = time.perf_counter()
    arduinoString = arduinoData.readline()  # read the line of text from the serial port
    # print(arduinoString)
    dataArray = arduinoString.decode('utf-8').split(',')  # Split it into an array called dataArray
    temp = float(dataArray[0])
    index = int(dataArray[1])
    loop = (loop + 1) % (fiveV_lines*read_lines)
    if loop == 0:
        i += 1
    max[index] += temp

    if i >= 19:
        max = max / float(20)
        break
        # mean = np.mean(1. / max)
        # std = np.std(1. / max)



mat = (1/max).reshape(15, 16)
fig, ax = plt.subplots()
heatmap = ax.imshow(mat)
plt.colorbar(heatmap)

# fig, ax = plt.subplots()
# heatmap = ax.imshow(moving_average_filter(mat))
# plt.colorbar(heatmap)
#
# fig, ax = plt.subplots()
# heatmap = ax.imshow(exponential_moving_average(mat))
# plt.colorbar(heatmap)
#
# fig, ax = plt.subplots()
# heatmap = ax.imshow(apply_median_filter(mat))
# plt.colorbar(heatmap)
#
# fig, ax = plt.subplots()
# heatmap = ax.imshow(apply_savitzky_golay_filter(mat))
# plt.colorbar(heatmap)

# fig, ax = plt.subplots()
# heatmap = ax.imshow(apply_spatial_filter(weighted_neighbor_correction(adaptive_thresholding(mat))))
# plt.colorbar(heatmap)

# fig, ax = plt.subplots()
# heatmap = ax.imshow(compensate_row_and_column_minimum(mat))
# plt.colorbar(heatmap)

plt.title("3D Bar Chart")
plt.show()













# print(np.array(1/max).reshape(15,16))
# heights = np.random.randint(1, 10, size=len(x))  # Heights of the bars
#
# # Width and depth of bars
# dx = dy = 1
#
#
#
# # Create the 3D bar chart
# fig = plt.figure(figsize=(10, 10))
# ax = fig.add_subplot(111, projection='3d')
# colors = cm.viridis(1/max)
# ax.bar3d(x, y, z, dx, dy, 1/max, color=colors, shade=True)
#
# # Add labels
# ax.set_xlabel('X Axis')
# ax.set_ylabel('Y Axis')
# ax.set_zlabel('Z Axis')
#
# print('hiiiiii')
# temp = compute_equivalent_conductance(np.array(1/max).reshape(15,16))
# print(temp)
# res,error = fixed_point_recover_conductances(temp)
# print(res)
# fig2 = plt.figure(figsize=(10, 10))
# ax2 = fig2.add_subplot(111, projection='3d')
# colors = cm.viridis(res.flatten())
# ax2.bar3d(x, y, z, dx, dy, res.flatten(), color=colors, shade=True)
#
# # Add labels
# ax2.set_xlabel('X2 Axis')
# ax2.set_ylabel('Y2 Axis')
# ax2.set_zlabel('Z2 Axis')
#
#
#
