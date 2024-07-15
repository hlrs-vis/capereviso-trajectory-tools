import json

class json_data:
    def __init__(self) -> None:
        pass
    def read_file(self, file_path):
        with open(file_path) as json_file:
            data = json.load(json_file)

        self.frame_data = []
        for entry in data:
            frame_id = entry["frame_id"]
            frame_time = entry["frame_time"]
            self.frame_data.append({"frame_id": frame_id, "frame_time": frame_time})

        return self.frame_data
        
    def get_frame_time(self,frame_id):
        for entry in self.frame_data:
            if entry["frame_id"] == frame_id:
                return entry["frame_time"]
        return None