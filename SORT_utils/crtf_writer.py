import struct


class crtf_writer:
    def __init__(self, filename_prefix, write_binary = True, write_ascii = False) -> None:
        self.ascii_format_header = '{0} {1} {2} {3} {4:.3f} {5:.3f}\n'
        self.ascii_format_lines = '{0:.3f} {1:.3f} {2:.3f}\n'
        self.binary_format_header = "<ii%usidd" % (1 + 20)
        self.binary_format_lines = "<ffd"
        self.write_binary = write_binary
        self.write_ascii = write_ascii
        if write_ascii:
            self.ascii_outputfile = open(filename_prefix+".crtf", "w")
        if write_binary:
            self.binary_outputfile = open(filename_prefix+".bcrtf", "wb")


    def write(self, trajectory):
        if self.write_ascii:
            self.ascii_outputfile.write(self.ascii_format_header.format(trajectory.total_id, 
                                                                        trajectory.perclass_id,
                                                                        trajectory.class_name,
                                                                        len(trajectory.points),
                                                                        trajectory.start_time,
                                                                        trajectory.end_time))
            for point in trajectory.points:
                #print("Testing: point('x')")
                #print(point['x'])
                self.ascii_outputfile.write(self.ascii_format_lines.format(point['x'], point['y'], point['time'])) #x,y,t with 3 decimal places (millimeter and milliseconds)
        if self.write_binary:
            self.binary_outputfile.write(struct.pack(self.binary_format_header, 
                                                     trajectory.total_id,
                                                     trajectory.perclass_id,
                                                     bytes(trajectory.class_name, 'utf-8'),
                                                     len(trajectory.points),
                                                     trajectory.start_time,
                                                     trajectory.end_time))
            for point in trajectory.points:
                self.binary_outputfile.write(struct.pack(self.binary_format_lines, point['x'], point['y'], point['time']))
        if (trajectory.total_id != 0) and (trajectory.total_id % 1000 == 0):
            if self.write_ascii:
                self.ascii_outputfile.flush()
            if self.write_binary:
                self.binary_outputfile.flush()
            

