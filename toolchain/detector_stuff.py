from toolchain.camera_stuff import camera
import os
import numpy as np
import cv2 as cv
import time
import json
from types import SimpleNamespace

COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]


class detector:

    def __init__(self,darknet_path = None,GPU=False,json_stream=False,T_0_i=np.eye(3)):
        
        self.T_0_i = T_0_i

        if json_stream == False:
            if not os.path.exists(darknet_path):
                print('Darknet is not found')
            
            # Set directory of Darknet
            #path = '/home/AD.EKUPD.COM/robert.valder/Dokumente/GIT_REPOS/darknet'
            self.path = darknet_path

            # Load names of classes and get random colors
            self.classes = open(os.path.join(self.path,'cfg/coco.names')).read().strip().split('\n')
            np.random.seed(42)
            self.colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype='uint8')

            # Give the configuration and weight files for the model and load the network.
            self.net = cv.dnn.readNetFromDarknet(os.path.join(self.path,'cfg/yolov4.cfg'),os.path.join(self.path, 'yolov4.weights'))
            
            if GPU:
                self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
            #    self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA) 
                self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)            
            else:
                self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

            self.model = cv.dnn_DetectionModel(self.net)
            self.model.setInputParams(size=(320, 320), scale=1/255, swapRB=True)


            # determine the output layer
            self.ln = self.net.getLayerNames()
            self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        else:
            pass


    def run_from_camera(self,img,camera: camera ,timestamp,CONFIDENCE_THRESHOLD=0.5,NMS_THRESHOLD=0.5,id_list=None,verbose=False):
        '''Outputs:
            classes_output: list - Name Classes strings ['class1', ... , 'classn']
            imagepoints_output: list - [element1, ... , element2] element: array.shape() = (2,1)
            position_output: list - [element1, ... , element2] element: array.shape() = (2,1)   '''
        
        start = time.time()
        classes, scores, boxes = self.model.detect(img, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        end = time.time()

        classes_idx = []
        classes_output = []
        imagepoints_output = []
        positions_output = []

        start_drawing = time.time()
        if id_list == None:
            for (classid, score, box) in zip(classes, scores, boxes):
                classes_idx.append(classid[0])
                classes_output.append(self.classes[classid[0]])
                cp_dist = detector.calc_contact_Point(box[0],box[1],box[2],box[3])
                x_dist = cp_dist[0]
                y_dist = cp_dist[1]
                x,y = detector.undistort(camera,x_dist,y_dist)
                cp = np.array([[x],[y]])
                imagepoints_output.append(cp)
                positions_output.append(self.img2world(cp,camera.invHmat))
        else:
            for (classid, score, box) in zip(classes, scores, boxes):
                if classid in id_list:
                    classes_idx.append(classid[0])
                    classes_output.append(self.classes[classid[0]])
                    cp_dist = detector.calc_contact_Point(box[0],box[1],box[2],box[3])
                    x_dist = cp_dist[0]
                    y_dist = cp_dist[1]
                    x,y = detector.undistort(camera,x_dist,y_dist)
                    cp = np.array([[x],[y]])
                    imagepoints_output.append(cp)
                    positions_output.append(self.img2world(cp,camera.invHmat))        
        end_drawing = time.time()

        if verbose:
            print("FPS: %.2f (excluding drawing time of %.2fms)" % (1 / (end - start), (end_drawing - start_drawing) * 1000))


        return detected_objects(classes=classes_output,classes_idx=classes_idx,positions=positions_output,imagepoints=imagepoints_output,timestamp=time.time(),T_0_i = self.T_0_i)        

    
    def run_from_json(self,json_frame,camera: camera,id_list = None):
        '''obj = 
            special variables
            class_id:XX
            confidence:0.xxx
            name:'Class Name'
            relative_coordinates: namespace(center_x=0.xxx, center_y=0.xxx, height=0.xxx, width=0.xxx)'''    
        detections = json.loads(json_frame, object_hook=lambda d: SimpleNamespace(**d))
        
        timestamp = detections.frame_time
        classes_idx = []
        classes_output = []
        imagepoints_output = []
        positions_output = []


        if id_list == None:
            for obj in detections.objects:
                x_dist = obj.relative_coordinates.center_x*camera.width
                y_dist = obj.relative_coordinates.center_y*camera.height
                x,y = detector.undistort(camera,x_dist,y_dist)
                classes_output.append(obj.name)
                cp = detector.calc_contact_Point_centered(x,y,obj.relative_coordinates.height*camera.height)
                classes_idx.append(obj.class_id)
                imagepoints_output.append(cp)
                positions_output.append(self.img2world(cp,camera.invHmat))
        else:
            for obj in detections.objects:
                if obj.class_id in id_list:
                    x_dist = obj.relative_coordinates.center_x*camera.width
                    y_dist = obj.relative_coordinates.center_y*camera.height
                    x,y = detector.undistort(camera,x_dist,y_dist)
                    classes_output.append(obj.name)
                    cp = detector.calc_contact_Point_centered(x,y,obj.relative_coordinates.height*camera.height)
                    classes_idx.append(obj.class_id)
                    imagepoints_output.append(cp)
                    positions_output.append(self.img2world(cp,camera.invHmat))
    
        return detected_objects(classes=classes_output,classes_idx=classes_idx,positions=positions_output,imagepoints=imagepoints_output,timestamp=timestamp,undisturbed=True,T_0_i=self.T_0_i)


    def undistort(camera: camera, dist_x,dist_y, iter_num=3):
        #https://yangyushi.github.io/code/2020/03/04/opencv-undistort.html
            
            k1 = camera.dist[0,0]
            k2 = camera.dist[0,1]
            p1 = camera.dist[0,2]
            p2 = camera.dist[0,3]
            k3 = camera.dist[0,4]

            

            #k1, k2, p1, p2, k3 = distortion
            fx, fy = camera.mtx[0, 0], camera.mtx[1, 1]
            cx, cy = camera.mtx[:2, 2]
            #x, y = xy.astype(float)
            
            

            x = dist_x
            y = dist_y

            x = (x - cx) / fx
            x0 = x
            y = (y - cy) / fy
            y0 = y
            for _ in range(iter_num):
                r2 = x ** 2 + y ** 2
                k_inv = 1 / (1 + k1 * r2 + k2 * r2**2 + k3 * r2**3)
                delta_x = 2 * p1 * x*y + p2 * (r2 + 2 * x**2)
                delta_y = p1 * (r2 + 2 * y**2) + 2 * p2 * x*y
                x = (x0 - delta_x) * k_inv
                y = (y0 - delta_y) * k_inv
            return x * fx + cx, y * fy + cy


    def img2world(self,image_points,invHmat):
        ip = np.append(image_points.reshape(1,2),1)
        world_points = np.matmul(invHmat,ip)
        world_points[0] = world_points[0]/world_points[2]
        world_points[1] = world_points[1]/world_points[2]
        world_points[2] = world_points[2]/world_points[2]
        return world_points.reshape(3,1)[0:2]*(10**-3)

    def img2world_ref(self, image_points,invHmat):
        all_world_points = np.array([])
        for image_pt in image_points:
            ip = np.append(image_pt.reshape(1,2),1)
            world_points = np.matmul(invHmat,ip)
            world_points[0] = world_points[0]/world_points[2]
            world_points[1] = world_points[1]/world_points[2]
            world_points[2] = world_points[2]/world_points[2]
            all_world_points = np.append(all_world_points, world_points.reshape(1,3)[0:2])
        all_world_points = all_world_points.reshape(-1,3)
        return all_world_points



    def calc_contact_Point(x,y,w,h):
        '''x,y is the top left corner of the bounding box. w,h are width and height of the bounding box'''
        cp_x = x + 0.5*w
        cp_y = y + h
        cp = np.array([[cp_x],[cp_y]])
        return cp


    def calc_contact_Point_centered(x,y,h):
        '''x,y is the center of the bounding box. w,h are width and height of the bounding box'''
        cp_x = x
        cp_y = y + 0.5*h
        cp = np.array([[cp_x],[cp_y]])
        return cp    


    def create_output_image(img,detected_objects,camera_object,classes=False,world_position=False,img_position=False):
        keypoints = []
        
        img_out = img

        color = np.array((0,0,255), dtype='uint8')
        color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ]))
        
        dpos_x = 10
        spacing = 15

        for detected_object_idx,imagepoint in enumerate(detected_objects.imagepoints):
            id = str(detected_object_idx).zfill(3)
            x,y = imagepoint
            x = int(x)
            y = int(y)

            fontsize = 0.8
            thickness = 2
            img_out = cv.putText(img_out, f'ID: {detected_object_idx}', (x+dpos_x,y+spacing*0), cv.FONT_HERSHEY_SIMPLEX, fontsize, color, thickness=thickness)
            
            if world_position==True:
                wx,wy = detected_objects.positions[detected_object_idx]
                wx = float(wx)
                wy = float(wy)
                img_out = cv.putText(img_out,f'x = {wx:.2f}m; y ={wy:.2f}m' , (x+dpos_x,y+spacing*1), cv.FONT_HERSHEY_SIMPLEX, fontsize, color, thickness=thickness)

            if classes == True:
               img_out = cv.putText(img_out,detected_objects.classes[detected_object_idx] , (x+dpos_x,y+spacing*2), cv.FONT_HERSHEY_SIMPLEX, fontsize, color, thickness=thickness) 

            keypoints.append(cv.KeyPoint(x,y,20))
        
        cv.drawKeypoints(img, keypoints, img_out,color=color)

      

        if img_position==True:
            img_out = cv.drawFrameAxes(img_out,camera_object.mtx,camera_object.dist,camera_object.rvec,camera_object.tvec,50)


        

        # if classes == True:
        #     for detected_object_idx,detected_object in enumerate(detected_objects):
        #         cv.putText(img, f', Position: {world_points2}', pos, cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # for idx,detected_object in enumerate(detected_objects):
        #     print(f'x = {detected_object.cp_x}; y = {detected_object.cp_y}')
        #     keypoints.append(cv.KeyPoint(detected_object.cp_x,detected_object.cp_y,20))
        #     texts.append(f'{idx}')

        #     color = np.array((0,0,255), dtype='uint8')
        #     color = ( int (color [ 0 ]), int (color [ 1 ]), int (color [ 2 ]))


        # print(f'Class: {detected_objects[index].classes}, position: {world_points}')

        # img_keypoints = np.empty((yi.img.shape[0], yi.img.shape[1], 3), dtype=np.uint8)
        # cv.drawKeypoints(dst, keypoints, img_keypoints,color=color)
        # for idx,text in enumerate(texts):
        #     pos = detected_objects[idx].get_contact_point()
        #     pos2 = np.asarray(detected_objects[idx].get_contact_point())
        #     pos2[1] = pos2[1]+15
        #     #cv.putText(img_keypoints, f'Object: {idx}, Position: {world_points}', pos, cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        #     

        return img_out



class detected_objects:
    '''Detectes Objects in PMBM format'''
    
    
    def __init__(self,classes = [] ,classes_idx = [],positions = [], positions_global = [],imagepoints = [],timestamp=None,undisturbed=False,T_0_i=np.eye(3)):
        ''' input: \n
                classes - list with class names  \n
                classes_idx - list with class indexes \n
                positions - list with the object positions in camera coorinate system \n
                imagepoints - list with the object positions in the image coordinate system \n
                timestamp - time image taken'''
        self.classes = classes
        self.classes_idx = classes_idx
        self.positions = positions
        self.positions_global = positions_global
        self.imagepoints = imagepoints
        self.timestamp = timestamp
        self.disturbed = undisturbed
        self.T_0_i = T_0_i
        #self.coordiante_transformation()


    def __str__(self):
        return f"Detected_objects Time: {self.timestamp} \n Numer of objects: {len(self.classes)}"    


    def coordiante_transformation(self):
        if np.array_equal(self.T_0_i,np.eye(3)):
            self.positions_global = self.positions.copy() 
        else:
            position_global = []
            for position in self.positions:
                #print(position)
                p_i = np.concatenate((position, np.array([[1]])), axis=0)
                p_0 = self.T_0_i@p_i
                position_global.append(p_0[0:2]) 
            self.positions_global = position_global
     

    def delete_elements_outside(self,arrangement):

        delete = []

        x_m = arrangement.x0 + (arrangement.x1 - arrangement.x0)/2
        y_m = arrangement.y0 + (arrangement.y1 - arrangement.y0)/2

        for index, position in enumerate(self.positions_global):
            
            
            if (arrangement.side == 0):
                if x_m  < position[0]:
                    delete.append(index)
            elif (arrangement.side == 1):
                if y_m  < position[1]:
                    delete.append(index)
            elif (arrangement.side == 2):
                if x_m  > position[0]:
                    delete.append(index)
            elif (arrangement.side == 3):
                if y_m  > position[1]:
                    delete.append(index)

        if len(delete) > 0:
            for d in reversed(delete): 
                self.classes.pop(d)
                self.classes_idx.pop(d)
                self.positions.pop(d)
                self.positions_global.pop(d)
                self.imagepoints.pop(d)


    def get_overlapping_detections(self,arrangement):
        # 1. check if inside rectange

        overlapping_detections = []

        for index, position in enumerate(self.positions_global):
            if arrangement.x0 < position[0] and position[0] < arrangement.x1:
               if arrangement.y1 < position[1] and position[1] < arrangement.y0:
                   overlapping_detections.append(index)

        self.overlapping_detections = overlapping_detections          
                   


            

class arrangement:
    '''Defines the area to be observed and the overlap zone. Values refere to the global coordinate system \n
    P1 = [x1 y1] - is the top left point \n
    P2 = [x2 y2] - is the bottom right point'''

    def __init__(self,x0,y0,x1,y1,side):
       '''Defines the area to be observed and the overlap zone. Values refere to the global coordinate system \n
    P0 = [x0 y0] - is the top left point \n
    P1 = [x1 y1] - is the bottom right point \n
    side - specifies the side that limits the measurements. 0 = right; 1 = top; 2 = left; 3 = bottom''' 
       
       self.x0 = x0
       self.x1 = x1
       self.y0 = y0 
       self.y1 = y1
       self.side = side 

       #self.get_Area()



    def load_arrangement(self):
        #load from imageCoordinatesTool.py
        
        self.get_Area()
           

class IMU:
    def __init__(self, frame, vf, vl, ru):
        self.frame = frame
        self.vf = vf    # Velocity forward
        self.vl = vl    # Velocity left
        self.ru = ru    # Rotation around up        