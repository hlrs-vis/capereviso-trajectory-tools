import struct
import sys

import argparse
import math
import configparser
from toolchain import camera_stuff
from postprocessing.grid import * 
from postprocessing import projection
from postprocessing.trajectory_calculations import *
from postprocessing.trajectory_io import *
from postprocessing.projection_helper import *
from postprocessing.trajectory_interactions import *
from postprocessing.trajectory_plotting import *
from postprocessing import video_io


# Import the matplotlib and animation libraries
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import numpy as np
import scipy.stats as stats

from postprocessing.plot_helper import *

def calculate_velocity(x, y, time, steps=3):
    vx = [0]*5  # initial x velocity is 0
    vy = [0]*5  # initial y velocity is 0
    if len(x) > steps:
      for i in range(steps, len(x)):
          vx.append((x[i] - x[i-steps]) / (time[i] - time[i-steps]))
          vy.append((y[i] - y[i-steps]) / (time[i] - time[i-steps]))
    return vx, vy

def calculate_acceleration(x, y, time):
    vx, vy = calculate_velocity(x, y, time)
    ax = [0]  # initial x acceleration is 0
    ay = [0]  # initial y acceleration is 0
    for i in range(1, len(x)):
        ax.append((vx[i] - vx[i-1]) / (time[i] - time[i-1]))
        ay.append((vy[i] - vy[i-1]) / (time[i] - time[i-1]))
    return ax, ay

def smooth_data(data, window_size):
  smoothed_data = []
  for i in range(len(data)):
    if i < window_size:
      smoothed_data.append(sum(data[:i+1]) / (i+1))
    else:
      smoothed_data.append(sum(data[i-window_size:i]) / window_size)
  return smoothed_data

def calculate_smoothed_velocity(x, y, time, window_size):
  vx, vy = calculate_velocity(x, y, time)

  smoothed_v = smooth_data([math.sqrt(vx**2 + vy**2) for vx, vy in zip(vx, vy)],window_size)

  return smoothed_v

def calculate_smoothed_acceleration(x, y, time, window_size):
  ax, ay = calculate_acceleration(x, y, time)

  smoothed_ax = smooth_data(ax, window_size)
  smoothed_ay = smooth_data(ay, window_size)
  smoothed_a = [math.sqrt(ax**2 + ay**2) for ax, ay in zip(smoothed_ax, smoothed_ay)]

  return smoothed_a

# create custom colormap
transparent_coolwarm = create_transparent_coolwarm()


#fig, axs = plt.subplots(1, 2)
#fig, axs = plt.subplots(1, 1)
fig, axs = plt.subplots()

encounter_to_plot = 0
objects = []

def on_key_press(event):
    global encounter_to_plot
    global objects
    if event.key == 'a':
        # Remove all lines from the previous plot
        for obj in objects:
            obj.remove()
        objects = []
        fig.canvas.draw()
        while encounters[encounter_to_plot]['Distance'] > 0.5:
          encounter_to_plot += 1
        if encounter_to_plot < len(encounters):
            new_objects = plot_encounter(axs, encounters[encounter_to_plot], trajectories1.all_trajectories)
            objects.extend(new_objects)
            encounter_to_plot += 1
            fig.canvas.draw()

fig.canvas.mpl_connect('key_press_event', on_key_press)


class_selection = ['bicycle', 'car', 'person', 'motorbike', 'bus', 'truck'] #['bicycle', 'car', 'person', 'motorbike'] #['bicycle', 'person']  # ['bicycle', 'car', 'person', 'motorbike']
class_colors = {'bicycle': 'blue', 'car': 'red', 'person': 'green', 'motorbike': 'black', 'bus':'magenta', 'truck':'yellow'}



colors = ['red', 'lime', 'orange', 'cyan', 'magenta', 'yellow', 'black']  # Add more colors if needed

real_camera = camera_stuff.camera


parser = argparse.ArgumentParser(description = "This program should analyse bcrtf-Files.")
parser.add_argument("inputfile", type=str, help = "Input bcrtf")
parser.add_argument("-c", "--config", type=str, required=True, help="Path to config.ini data")
args = parser.parse_args()

config_path = args.config
config_file = configparser.ConfigParser()
config_file.read(config_path)

# Create display object and read in config values
display = projection.screen_display(config_file)

# Create scene object and draw the background image to the plot
scene1 = projection.scene(config_file)
scene1.calculate_scene(display)
scene1.calculate_camera_homography()
scene1.draw_image_to_plot(axs, display)

if (display.draw_axis):
  draw_coordinate_axis(axs, 0, 0)

# Set up the grid for counting visits and a copy for temporary use
grid_visited = Grid(display.extent, display.grid_resolution)
grid_temp = Grid(display.extent, display.grid_resolution)

grid_max_a = Grid(display.extent, display.grid_resolution)
grid_max_v = Grid(display.extent, display.grid_resolution)


# Open the binary file in binary mode
if args.inputfile.endswith('.bcrtf'):
    print("File is ", args.inputfile)
    # data_path = sys.argv[1]
    trajectories1 = trajectories_io()
    trajectories1.read(args.inputfile)

    prefix = args.inputfile.split('.')[0]
    heatmap_outfile = prefix + '_heatmap'
    prefix = prefix.replace('test_', '')
    prefix = prefix.rsplit('/', 1)[-1]
    prefix = prefix.split('_', 1)[0]

    intersection_lines = line_intersection(class_selection)
    #set outbound south-east
    #intersection_lines.add_line_set([(-2, -10, 1, -7.5), (6.7, -20, 11, -16.7)])
    intersection_lines.add_line_set([(-9.13, -1.96, -4.22, 2.16), (6.7, -20, 11, -16.7)])
    line_offset = 0.5
    intersection_lines.add_line_set([(12.44, -6.0, 16.4, -13.0) ,(-9.13+line_offset, -1.96-line_offset, -4.22+line_offset, 2.16-line_offset)])

    #inbound from east
    #intersection_lines.add_line_set([(10.8, 3.5, 14.3, -3), (6.3, -19.6, 10.6, -16.3)])

    #intersection_lines.add_line_set([(13.5, -20, 17.7, -16.9), (-6.4, 4.0, -3.2, 7.0)])
    intersection_lines.add_line_set([(-3.2, 7.0, -6.4, 4.0)])
    intersection_lines.add_line_set([(-5.5, 10.9, -3.9, 15.4)])
    #intersection_lines.add_line_set([(-11.43, -3.65, -3.9, 15.4)])
 
    #interactions1 = trajectory_interactions(trajectories1.all_trajectories, class_selection)
    #interactions1.find_latest_coincidence()
    #encounters = interactions1.find_closest_encounter()
    import time

    #interactions1 = trajectory_interactions(trajectories1.all_trajectories, class_selection)

    #start_time = time.time()
    #interactions1.find_latest_coincidence()
    #end_time = time.time()
    #print(f"Time taken by find_latest_coincidence: {end_time - start_time} seconds")

    #start_time = time.time()
    #encounters = interactions1.find_closest_encounter()
    #end_time = time.time()
    #print(f"Time taken by find_closest_encounter: {end_time - start_time} seconds")

    for class_name, trajectories in trajectories1.trajectories_by_class.items():
      if class_name in class_selection:
        for trajectory in trajectories:
          # Initialize lists for x, y, z, and time
          x = []
          y = []
          z = []
          time = []
          for point in trajectory['positions']:
            if scene1.is_inside_polygon(point):  # Check if points are inside the camera image and region of interest
                x.append(point['x'])
                y.append(point['y'])
                z.append(1)
                time.append(point['time'])
          #x = [point['x'] for point in trajectory['positions']]
          #y = [point['y'] for point in trajectory['positions']]
          #z = [1 for _ in range(len(x))]
          #time = [point['time'] for point in trajectory['positions']]
          
          # calculate acceleration and velocity and smooth them by averaging
          v = calculate_smoothed_velocity(x, y, time, 20)
          a = calculate_smoothed_acceleration(x, y, time, 20)

          grid_max_a.set_max_value(x, y, a, 100000)
          grid_max_v.set_max_value(x, y, v, 40)
          # Plot all trajectories
          #color = class_colors[class_name]
          #axs[1].plot(x, y, color=color)

          intersection_lines.test_all_intersections(x,y,class_name)
          #for i, lines in enumerate(intersection_lines.lines):
          #      if all(test_trajectory_intersection(x, y, line) for line in lines):
          #          intersections_counts[i] += 1

          grid_temp.mark_visited_cells(x,y)
          grid_visited.add_grid(grid_temp)
          grid_temp.reset()
    
    intersection_lines.display_counts(axs, colors)
    intersection_lines.draw_lines(axs, colors)
    intersection_lines.write_intersection_counts(args.inputfile, colors)
    grid_visited.display_grid(axs, transparent_coolwarm)
    # label axis
    axs.set_xlabel('x [m]')
    axs.set_ylabel('y [m]')
    axs.set_title('Heatmap of Spatial Visitation Count - ' + prefix)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)

    #grid_max_a.display_grid(axs, transparent_coolwarm)
    #grid_max_v.display_grid(axs, transparent_coolwarm)

    # Show everything on the screen
    plt.savefig(heatmap_outfile+'_highres.png', dpi=300)
    #plt.show()

    # Trajectories can also be drawn into the video the detections were extracted off
    #video1 = video_io.video_data(config_file=config_file, class_selection=class_selection)
    #video1.draw_trajectories_on_video(trajectories1)
else:
  print("Error, please supply a bcrtf-File")
