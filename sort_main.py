from sort.sort import *
from SORT_utils.json_io import *
import cv2
import numpy

colours = np.random.rand(32, 3) * 255 #used only for display
colors = [matplotlib.colors.hsv_to_rgb((h,1,1)) * 255 for h in numpy.arange(0,1, 1/32)]

#from sort import Sort

# Initialize the SORT tracker
sort_tracker = Sort(max_age=20, min_hits=2, iou_threshold=0.05)

# Read the detections from the JSON file
data = read_json('/home/hpcthobs/home-visnuc/home/visadmin/playback1_2023-01-13_11-52-31.json',1920,1080)

cap = cv2.VideoCapture('/home/hpcthobs/home-visnuc/home/visadmin/VideoCapture2.mp4')


output_file_path = "SORT-Video-test.mp4"
fps = 30
fourcc = cv2.VideoWriter_fourcc(*"XVID")
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
video_writer = cv2.VideoWriter(output_file_path, fourcc, fps, (frame_width, frame_height))



#cap = cv2.VideoCapture('/home/visadmin/Videoresult_2023-01-13_11-52-31.mp4')
# Process each frame of the video

# For each subsequent frame, pass the new set of detections to the SORT tracker
for frame_number, frame in enumerate(data):
    ret, cap_frame = cap.read()
    
    if not ret:
        break
    #if frame_number >= 500:
        #break
    cap_frame = cv2.flip(cap_frame, -1)
    detections = np.array(frame['detections'])
    #print(detections)
    track_bbs_ids = sort_tracker.update(detections)
    for bb in track_bbs_ids:
        x1, y1, x2, y2, id = bb
        id = int(id)
        #cv2.rectangle(cap_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        #rect = cv2.rectangle(cap_frame, (d[0], d[1]), (d[2], d[3]), colors[d[4] % 32, :], 3)
        cv2.rectangle(cap_frame, (int(x1), int(y1)), (int(x2), int(y2)), colors[id % 32], 3)
    #cv2.imshow("image", cap_frame)
    #print(track_bbs_ids)
    #cv2.waitKey(0)

    #break
    video_writer.write(cap_frame)

cap.release()
cv2.destroyAllWindows()