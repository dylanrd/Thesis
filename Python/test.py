import numpy as np

np.random.seed(0)
import seaborn as sns
import matplotlib
matplotlib.use('TkAgg')
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

data = np.random.rand(120, 5900)
data_to_draw = np.zeros(shape = (1, 5900))

grid_kws = {'width_ratios': (0.9, 0.05), 'wspace': 0.2}
fig, (ax, cbar_ax) = plt.subplots(1, 2, gridspec_kw = grid_kws, figsize = (10, 8))

for i, d in enumerate(data):
    # update data to be drawn
    data_to_draw = np.vstack((data_to_draw, data[i]))
    # keep max 5 rows visible
    if data_to_draw.shape[0] > 5:
        data_to_draw = data_to_draw[1:]

    sns.heatmap(ax = ax, data = data_to_draw, cmap = "coolwarm", cbar_ax = cbar_ax)

    plt.draw()
    plt.pause(0.1)