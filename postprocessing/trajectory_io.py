import math
import struct

class trajectories_io:

    def __init__(self):
        # trajectories
        self.trajectories_by_class = {}
        self.total_counter = {}
        self.selected_counter = {}
        self.all_trajectories = []

    # Define a function to read the header from a binary file
    def read_header(self, header_binary):
        # Read the global id, class id, and class name the number of timesteps, first timestep, and last 
        # timestep from the binary file
        global_id, class_id, class_name, num_timesteps, first_timestep, last_timestep= struct.unpack('<ii%usidd' %(21), header_binary)

        # remove any trailing null bytes from the string
        class_name = class_name.rstrip(b'\x00')
        #positions = []
        
        # Return the header information as a dictionary
        return {
            "global_id": global_id,
            "class_id": class_id,
            "class_name": class_name.decode(),
            "num_timesteps": num_timesteps,
            "first_timestep": first_timestep,
            "last_timestep": last_timestep,
            "positions": [],
            "trajectory_image_coordinates": []
            }



    def read(self, filename):
        with open(filename, "rb") as file:
        # Read the header from the binary file
            while True:
                header_binary = file.read(8+21+20)
                if header_binary == b'':
                    break
                trajectory = self.read_header(header_binary)
                class_name = trajectory["class_name"]
                # print (class_name)
                if class_name not in self.total_counter:
                    self.total_counter[class_name] = 0
                self.total_counter[class_name] += 1

                # Read the positions from the binary file
                positions, distance_covered, time_covered = self.read_positions(file, trajectory['num_timesteps'])
            
                trajectory["positions"]= positions
                # trajectories longer than 10 minutes and shorter than 2 meters are discarded for now. ToDo: make this configurable
                if time_covered < 600:
                #if trajectory['num_timesteps'] > 30:
                    if distance_covered > 2:
                        if class_name not in self.trajectories_by_class:
                            self.trajectories_by_class[class_name] = []
                        if class_name not in self.selected_counter:
                            self.selected_counter[class_name] = 0
                        self.trajectories_by_class[class_name].append(trajectory)
                        self.selected_counter[class_name] += 1
                        self.all_trajectories.append(trajectory)

        print(self.selected_counter, 'trajectories of', self.total_counter, 'selected')



    # Define a function to read the positions from a binary file
    def read_positions(self, file, num_timesteps):
        # Create an empty list to store the positions
        positions = []
        distance_covered = 0
        # Read the positions from the binary file
        # Use a for loop to iterate over the number of timesteps
        # Use the 'ffi' format specifier to read the x position, y position, and time as floating-point values, and the class id as an integer
        for i in range(num_timesteps):
            # Read the x position, y position, time, and class id from the binary file
            x, y, time = struct.unpack('<ffd', file.read(16))

            if i > 0:
                prev_x = positions[i - 1]["x"]
                prev_y = positions[i - 1]["y"]
                distance = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                distance_covered += distance

            # Add the position to the list of positions
            positions.append({
            "x": x,
            "y": y,
            "time": time,
            })
        
        # Calculate the time covered by the trajectory
        start_time = positions[0]["time"]
        end_time = positions[-1]["time"]
        time_covered = end_time - start_time

        # Return the list of positions
        return positions, distance_covered, time_covered