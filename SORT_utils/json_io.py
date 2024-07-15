import json
import tarfile

def read_json(json_file, width, height):
    try:
        if json_file.endswith('.gz'):
            with tarfile.open(json_file, 'r:gz') as tar:
                json_files = [member for member in tar.getmembers() if member.isfile() and member.name.endswith('.json')]
                if len(json_files) > 1:
                    raise ValueError("More than one JSON file in archive")
                file = tar.extractfile(json_files[0])
                data = json.load(file)
        elif json_file.endswith('.json'):
            with open(json_file, 'r') as file:
                data = json.load(file)
        else: 
            print("File is not .json or .gz")
            return None, None
    except IOError as e:
        print(f"Error opening file: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None, None

    frames = []
    classes = {}
    for frame in data:
        frame_id = frame['frame_id']
        frame_time = frame['frame_time']
        detections = []
        for obj in frame['objects']:
            detection = [
                #frame['frame_id'],
                (obj['relative_coordinates']['center_x'] - obj['relative_coordinates']['width']/2)*width,
                (obj['relative_coordinates']['center_y'] - obj['relative_coordinates']['height']/2)*height,
                (obj['relative_coordinates']['center_x'] + obj['relative_coordinates']['width']/2)*width,
                (obj['relative_coordinates']['center_y'] + obj['relative_coordinates']['height']/2)*height,
                obj['confidence'],
                obj['class_id']
            ]
            if obj['class_id'] not in classes:
                classes[obj['class_id']] = obj['name']
            detections.append(detection)
        frames.append({'frame_id': frame_id, 'frame_time': frame_time, 'detections': detections})
    return frames, classes
