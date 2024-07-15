import math

class Trajectory:
    def __init__(self, sort_id, total_id, perclass_id, class_id, class_name, start_time, end_time, alive_id, alive_time):
        self.sort_id = sort_id
        self.total_id = total_id
        self.perclass_id = perclass_id
        self.class_id = class_id
        self.class_name = class_name
        self.start_time = start_time
        self.end_time = end_time
        self.points = []
        self.latest_alive_frame_id = alive_id
        self.latest_alive_time = alive_time
        self.length = 0
        self.point_count = 0
        #self.classes = []

    def add_point(self, x, y, time, class_id):
        point = {'x': x, 'y': y, 'time': time, 'class_id': class_id}
        self.points.append(point)
        self.point_count += 1
    
    def print(self):
        print("SORT ID:", self.sort_id)
        print("total ID:", self.total_id)
        print("per Class ID:", self.perclass_id)
        print("Class ID:", self.class_id)
        print("Class Name:", self.class_name)
        print("Start Time:", self.start_time)
        print("End Time:", self.end_time)
        print("Points:")
        for point in self.points:
            print("   X:", point['x'])
            print("   Y:", point['y'])
            print("   Time:", point['time'])
            print("   Class_ID:", point['class_id'])
        print("---------------")

    def add_class(self, classes):
        detected_classes = {}
        for point in self.points:
            if point['class_id'] in detected_classes:
                detected_classes[point['class_id']] +=1
            else:
                detected_classes[point['class_id']] = 1
        assumed_class = max(detected_classes, key=detected_classes.get)
        self.class_id = assumed_class
        self.class_name = classes[assumed_class]
        #print(classes[assumed_class])
        #print(assumed_class)
        return assumed_class
        
    def set_total_id(self, id):
        self.total_id = id
    
    def set_perclass_id(self, id):
        self.perclass_id = id

    def set_alive_id(self, frame_id):
        self.latest_alive_frame_id = frame_id

    def set_alive_time(self, frame_time):
        self.latest_alive_time = frame_time

    def distance_from_start(self):
        self.length = math.dist([self.points[0]['x'], 
                                 self.points[0]['y']],
                                [self.points[self.point_count-1]['x'], 
                                 self.points[self.point_count-1]['y']])
        #print("length is ", self.length )
        return self.length
