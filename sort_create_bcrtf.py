from sort.sort import *
from SORT_utils.json_io import *
from SORT_utils.trajectory_data import *
from SORT_utils.crtf_writer import *
#import cv2
import numpy
import argparse
import configparser
import time

from postprocessing import projection
from postprocessing.projection_helper import *

from toolchain import camera_stuff

# Start the timer for performance measuring
start_time = time.time()

parser = argparse.ArgumentParser(description = "This program should run the SORT-tracker on json-Files.")
parser.add_argument("inputfile", type=str, help = "Input json")
parser.add_argument("-c", "--config", type=str, required=True, help="Path to config.ini data")
args = parser.parse_args()

config_path = args.config
config_file = configparser.ConfigParser()
config_file.read(config_path)

real_camera = camera_stuff.camera
display = projection.screen_display(config_file)

scene1 = projection.scene(config_file)
scene1.calculate_scene(display)
scene1.calculate_camera_homography()


colours = np.random.rand(32, 3) * 255 #used only for display
colors = [matplotlib.colors.hsv_to_rgb((h,1,1)) * 255 for h in numpy.arange(0,1, 1/32)]


# Initialize the SORT tracker
max_age = 20
sort_tracker = Sort(max_age, min_hits=2, iou_threshold=0.05)

# Trajectories should be ignored if they persist 
# todo: but dont leave the radius after this time
ignore_age = 600  # time in seconds
ignore_radius = 2 # radius in meters

class_allow_list = ['person', 'car', 'truck', 'bicycle', 'bus', 'motorbike']

#filename = "test_SORT_trajectories"

status_update_interval = 100

exception_count = 0
trajectories_written_or_ignored_count = 0
last_trajectory_written = None

data = {}

# Read the detections from the JSON file

data, classes = read_json(args.inputfile, 1920, 1080)

if data is None or classes is None:
    print("Error reading JSON file")
    exit()
else:
    # Start bcrtf-File
    filename = os.path.splitext(args.inputfile)[0]  # Get the base filename without the extension
    # in case of json.gz files, only .gz was removed, so we have to remove .json as well
    if filename.endswith('.json'):
        filename = os.path.splitext(filename)[0]
    writer = crtf_writer(filename, True, True)



    # trajectory data
    trajectories = {}
    total_id=1
    total_frames = 0
    first_time = 0
    total_time = 0 
    ignored_by_radius = 0
    ignored_by_class = 0
    perclass_ids = {}
    frames_without_detections = 0
    frames_with_detections = 0
    for yolo_class in classes:
        perclass_ids[yolo_class] = 0

    next_trajectory_to_write = 1

    # For each subsequent frame, pass the new set of detections to the SORT tracker
    for frame_number, frame in enumerate(data):
        if frame_number == 0:
            first_time = frame['frame_time']
        detections = np.array(frame['detections'])
        if detections.size == 0:
            detections = np.empty((0, 6))
            frames_without_detections += 1
            if frames_without_detections % 10000 == 0:
                print("Frames with no detections : ", frames_without_detections)
        else:
            frames_with_detections += 1
            if frames_with_detections % 10000 == 0:
                print("Frames with detections:", frames_with_detections)
        frame_time = frame['frame_time']
        frame_id = frame['frame_id']
        total_frames = frame_id
        total_time = frame_time
        #print("frame_id: ", frame_id)
        track_bbs_ids = sort_tracker.update(detections)
        for bb in track_bbs_ids:
            x1, y1, x2, y2, sort_id, class_id = bb
            sort_id = int(sort_id)
            #if id == 5:
                #print("Found id: ", id)
            class_id = int(class_id)
            ref_point_image_x = (x1+x2)/2
            ref_point_image_y = y2
            trajectory_image_coordinates = np.column_stack((ref_point_image_x, ref_point_image_y))
            trajectory_world_coordinates = img2world(trajectory_image_coordinates, scene1.real_camera_setup.invHmat)
            if sort_id not in trajectories:
                trajectories[sort_id] = Trajectory(sort_id, total_id, None, None, None, frame_time, None, frame_id, frame_time)
            trajectories[sort_id].add_point(trajectory_world_coordinates[0][0], trajectory_world_coordinates[0][1], frame_time, class_id)
            trajectories[sort_id].set_alive_id(frame_id)
            trajectories[sort_id].set_alive_time(frame_time)


        # Write bcrtf-File, SORT-ids are given in the order objects are "born"
        # Keeping this order is important, but new ascending ids without gaps have to be assigned
        # Always write the trajectories from the beginning to file which exceed max_age, then stop
        try:
            while (frame_id - max_age) > trajectories[next_trajectory_to_write].latest_alive_frame_id:
                #print("Trajectory ", next_trajectory_to_write, " is old, should be written")
                trajectories[next_trajectory_to_write].distance_from_start()
                #print("Trajectory ", next_trajectory_to_write, " is ", trajectories[next_trajectory_to_write].length , "m long")
                if trajectories[next_trajectory_to_write].length > ignore_radius:
                    assumed_class = trajectories[next_trajectory_to_write].add_class(classes)
                    if classes[assumed_class] in class_allow_list:
                        trajectories[next_trajectory_to_write].set_total_id(total_id)
                        total_id += 1

                        # Assume the class of the trajectory and set it with id
                        perclass_ids[assumed_class] += 1
                        trajectories[next_trajectory_to_write].set_perclass_id(perclass_ids[assumed_class])
                        

                        #set end_time
                        trajectories[next_trajectory_to_write].end_time = trajectories[next_trajectory_to_write].latest_alive_time

                        writer.write(trajectories[next_trajectory_to_write])
                        #print("Trajectory ", next_trajectory_to_write, " written")
                        trajectories_written_or_ignored_count += 1
                        last_trajectory_written = next_trajectory_to_write

                        next_trajectory_to_write +=1
                        #print("next is:", next_trajectory_to_write)
                        if (total_id != 0) and (total_id % status_update_interval == 0):
                            print(total_id, " trajectories written")
                            for detected_class in perclass_ids:
                                if classes[detected_class] in class_allow_list:
                                    print(classes[detected_class], ": ", perclass_ids[detected_class])
                    else:
                        ignored_by_class += 1
                        #print("trajectory with class", classes[assumed_class], " ignored")
                        trajectories_written_or_ignored_count += 1
                        next_trajectory_to_write +=1

                else:
                    #print("Trajectory ", next_trajectory_to_write, " is short, ", trajectories[next_trajectory_to_write].length , "m and ignored")
                    ignored_by_radius += 1
                    trajectories_written_or_ignored_count += 1
                    next_trajectory_to_write +=1

            while (frame_id - ignore_age) > trajectories[next_trajectory_to_write].latest_alive_frame_id:
                #print("Trajectory ", next_trajectory_to_write, " is very old, should be ignored")
                trajectories_written_or_ignored_count += 1
                next_trajectory_to_write +=1
        except:
            # Catch the exception if the trajectory does not exist
            # list(trajectories.keys())[-1] wont work before the fisrt trajectory exists
            # so at first we compare the number of trajectories to the number of trajectories written or ignored
            # after that we assume that the exception is because the next trajectory does not exist (yet) so we advance
            # only if the last item on the list has not been written yet to avoid advancing too far before the trajectory exists.
            if len(trajectories) <= trajectories_written_or_ignored_count:
                #print("No new trajectories")
                pass
            else:
                if next_trajectory_to_write < list(trajectories.keys())[-1]:
                    #print("Trajectory ", next_trajectory_to_write, " does not exist because it was discarded by SORT, advancing...")
                    next_trajectory_to_write +=1
                else:
                    #print("Trajectory ", next_trajectory_to_write, " does not exist yet")
                    pass

# End the timer
end_time = time.time()

# Calculate the elapsed time
execution_time = end_time - start_time

# Print the execution time
print("Execution Time:", execution_time, "seconds for ", total_frames, "frames covering", int(total_time - first_time), "s with ", total_id, " trajectories" )
for detected_class in perclass_ids:
    if classes[detected_class] in class_allow_list:
        print(classes[detected_class], ": ", perclass_ids[detected_class])
    else:
        print(classes[detected_class], " ignored")