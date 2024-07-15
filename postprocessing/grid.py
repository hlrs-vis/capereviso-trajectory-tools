import math
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt

class Grid:
    def __init__(self, extent, res):
        self.x_min = extent[0]
        self.x_max = extent[1]
        self.y_min = extent[2]
        self.y_max = extent[3]
        self.res = res
     
        self.grid_width = int(math.ceil((self.x_max - self.x_min) / res))
        self.grid_height = int(math.ceil((self.y_max - self.y_min) / res))
        self.grid = [[0 for i in range(self.grid_width)] for j in range(self.grid_height)]
    def add_grid(self, other_grid):
        if (self.x_min == other_grid.x_min and self.x_max == other_grid.x_max and self.y_min == other_grid.y_min and self.y_max == other_grid.y_max and self.res == other_grid.res):
            for i in range(self.grid_width):
                for j in range(self.grid_height):
                    self.grid[i][j] += other_grid.grid[i][j]
        else:
            raise ValueError("Both grids should have the same metadata (x_min, x_max, y_min, y_max, res)")
    def reset(self):
        for i in range(self.grid_width):
            for j in range(self.grid_height):
                self.grid[i][j] = 0

    def mark_visited_cells(self, x, y):
        for i in range(len(x)):
            if x[i] >= self.x_min and x[i] <= self.x_max and y[i] >= self.y_min and y[i] <= self.y_max:
                grid_x = int((x[i] - self.x_min) / self.res)
                grid_y = int((y[i] - self.y_min) / self.res)
                self.grid[grid_y][grid_x] = 1

    def set_max_value(self, x, y, value, limit):
        for i in range(len(x)):
            if x[i] >= self.x_min and x[i] <= self.x_max and y[i] >= self.y_min and y[i] <= self.y_max:
                grid_x = int((x[i] - self.x_min) / self.res)
                grid_y = int((y[i] - self.y_min) / self.res)
                if self.grid[grid_y][grid_x] < value[i] and value[i] < limit:
                    self.grid[grid_y][grid_x] = value[i]


    def display_grid(self, target_plot, colormap):
        #im = axs[0].imshow(self.grid, cmap=custom_cmap, extent=[self.x_min, self.x_max, self.y_min, self.y_max], origin='lower')
        im = target_plot.imshow(self.grid, cmap=colormap, extent=[self.x_min, self.x_max, self.y_min, self.y_max], origin='lower')
        #divider = make_axes_locatable(axs[0])
        divider = make_axes_locatable(target_plot)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(im, cax=cax)