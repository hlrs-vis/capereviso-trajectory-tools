import numpy as np
import math


class trajectory_interactions:
    def __init__(self, trajectories, class_selection):
        self.trajectories = trajectories
        self.class_selection = class_selection
        pass

    def min_simultaneous_distance(self, x1, y1, time1, x2, y2, time2):
        min_distance = float('inf')
        for t1z, x1z, y1z in zip(time1, x1, y1):
            for t2z, x2z, y2z in zip(time2, x2, y2):
                if t1z == t2z:
                    distance = math.sqrt((x2z - x1z)**2 + (y2z - y1z)**2)
                    if distance < min_distance:
                        min_distance = distance
        return min_distance, t1z

    def find_latest_coincidence(self):
        for i, trajectory in enumerate(self.trajectories):
            last_timestep = trajectory['last_timestep']
            #check all consequent trajectories
            for j in range(i, len(self.trajectories)):
                if self.trajectories[j]['first_timestep'] > last_timestep:
                    break
                else:
                    trajectory['last_coincidence'] = j

    def find_closest_encounter(self):
        encounters = []
        for i, trajectory in enumerate(self.trajectories):
            # Coordinates are inverted for some reason ToDo: explain why or change!
            x1 = [-point['x'] for point in trajectory['positions']]
            y1 = [-point['y'] for point in trajectory['positions']]
            z1 = [1 for _ in range(len(x1))]
            time1 = [point['time'] for point in trajectory['positions']]

            for j in range(i+1, trajectory['last_coincidence']):
                x2 = [-point['x'] for point in self.trajectories[j]['positions']]
                y2 = [-point['y'] for point in self.trajectories[j]['positions']]
                z2 = [1 for _ in range(len(x2))]
                time2 = [point['time'] for point in self.trajectories[j]['positions']]

                # find closest encounter
                min_distance, time_of_encounter = self.min_simultaneous_distance(x1, y1, time1, x2, y2, time2)
                if min_distance < 5.0:
                    encounter = {
                        'Trajectory1': i,
                        'Trajectory2': j,
                        'Time': time_of_encounter,
                        'Distance': min_distance
                    }
                    encounters.append(encounter)

                #if min_distance < 0.5:
                #    print('Closest encounter: ', min_distance)
                #    print('Trajectory 1: ', trajectory['global_id'])
                #    print('Trajectory 2: ', self.trajectories[j]['global_id'])
                #    print('Time: ', time1[0])
                #    print('Class 1: ', trajectory['class_name'])
                #    print('Class 2: ', self.trajectories[j]['class_name'])
                #    print('')

        return encounters

