import cv2
from postprocessing import json_io


class video_data:
    def __init__(self, config_file, class_selection, output_video_path="test-trajectory_output2.avi", fps = 30):
        self.orig_json = json_io.json_data()
        json_path = config_file.get('Data', 'original_json_path')
        self.video_path = config_file.get('Data', 'video_path')
        self.orig_json.read_file(json_path)
        self.class_selection = class_selection

        self.output_file_path = output_video_path
        self.fps = fps
        self.fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        self.cap = cv2.VideoCapture(self.video_path)
        self.frame_width = int(self.cap.get(3))
        self.frame_height = int(self.cap.get(4))
        self.video_writer = cv2.VideoWriter(self.output_file_path, self.fourcc, self.fps, (self.frame_width, self.frame_height))

        
    def draw_trajectories_on_video(self, trajectories):
        # Open the video stream
        cap = cv2.VideoCapture(self.video_path)

        # Process each frame of the video
        frame_number = 0
        while True:
            ret, frame = cap.read()
            if not ret:
            #if frame_number == 500:
                break
            frame_time = self.orig_json.get_frame_time(frame_number)
            self.process_frame(frame, frame_time, trajectories)
            frame_number += 1

        # Release the video stream
        cap.release()
        cv2.destroyAllWindows()

    def process_frame(self, frame, frame_time, trajectories):
        for class_name, trajectories in trajectories.trajectories_by_class.items():
            if class_name in self.class_selection:
                for trajectory in trajectories:
                    if trajectory["first_timestep"] <= frame_time <= trajectory["last_timestep"]:
                        for i in range(len(trajectory["trajectory_image_coordinates"]) - 1):
                            point_1 = (trajectory["trajectory_image_coordinates"][i][0], trajectory["trajectory_image_coordinates"][i][1])
                            point_2 = (trajectory["trajectory_image_coordinates"][i + 1][0], trajectory["trajectory_image_coordinates"][i + 1][1])
                            #print("Point1: ", point_1)
                            #print("Point2: ", point_2)                           
                            #cv2.line(frame, (trajectory["trajectory_image_coordinates"][i][0], trajectory["trajectory_image_coordinates"][i][1]), (trajectory["trajectory_image_coordinates"][i + 1][0], trajectory["trajectory_image_coordinates"][i + 1][1]), (0, 255, 0), 2)
                            #cv2.line(frame, (0,0), (100.123,100), (0, 255, 0), 2)
                            cv2.line(frame, (int(trajectory["trajectory_image_coordinates"][i][0]), int(trajectory["trajectory_image_coordinates"][i][1])), (int(trajectory["trajectory_image_coordinates"][i + 1][0]), int(trajectory["trajectory_image_coordinates"][i + 1][1])), (0, 255, 0), 2)
        cv2.putText(frame, str(int(frame_time)), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)
        self.video_writer.write(frame)