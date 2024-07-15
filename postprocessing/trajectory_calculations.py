import numpy as np
import csv

class line_intersection:
  def __init__(self, class_selection):
    self.line_sets = []
    self.intersections_counts = []
    self.class_selection = class_selection

  def add_line_set(self, line_set):
    self.line_sets.append(line_set)
    # Create a new dictionary for this line set
    count_dict = {}
    for class_name in self.class_selection:
        count_dict[class_name] = 0
    self.intersections_counts.append(count_dict)

  def test_all_intersections(self, x, y, class_name):
      for i, lines in enumerate(self.line_sets):
          if all(self.test_trajectory_intersection(x, y, line) for line in lines):
              self.intersections_counts[i][class_name] += 1

  def intersect(self, line_segment1, line_segment2):
    # Extract the coordinates of the first line segment
    x1, y1, x2, y2 = line_segment1

    # Extract the coordinates of the second line segment
    x3, y3, x4, y4 = line_segment2

    # Compute the intersection point of the two lines
    denom = ((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
    if denom != 0:
      x = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
      y = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

      # Check if the intersection point is within both line segments
      if ((x >= x1 and x <= x2) or (x >= x2 and x <= x1)) and ((y >= y1 and y <= y2) or (y >= y2 and y <= y1)):
        if ((x >= x3 and x <= x4) or (x >= x4 and x <= x3)) and ((y >= y3 and y <= y4) or (y >= y4 and y <= y3)):
          return True

    # If the intersection point is not within both line segments or the lines are parallel, return False
    return False

  def test_trajectory_intersection(self, x, y, line):
      # Convert trajectory points to numpy array
      # trajectory_points = np.array(x,y)
      trajectory_points = np.array(list(zip(x, y)))
      #print('Trajectory points:\n')
      #print(trajectory_points)
      # Get the number of segments in the trajectory
      n_segments = trajectory_points.shape[0] - 1
      # Loop through each segment in the trajectory
      for i in range(n_segments):
          # Get the start and end points of the current segment
          segment_start = trajectory_points[i]
          segment_end = trajectory_points[i+1]
          segment = (segment_start[0], segment_start[1], segment_end[0], segment_end[1])
          # Test if the segment intersects with the line
          if self.intersect(segment, line):
            return True
      # If no intersections were found, return False
      return False

  def display_counts(self, axs, colors):
    for i, counts in enumerate(self.intersections_counts):
      lines = self.line_sets[i]
      line = lines[0]
      x1, y1, x2, y2 = line
      x = max(x1, x2)
      y = max(y1, y2)
      for j, (class_name, count) in enumerate(counts.items()):
        print(f"Counted intersections for set {i+1}, class {class_name}: {count} {colors[i]}")
        axs.annotate(f"{class_name}: {count}", [x+0.5, y - j*0.8], color=colors[i], size=5)
  
  def write_intersection_counts(self, filename, colors):
    outputfilename = filename.split('.')[0]
    outputfilename = outputfilename + '_intersections.csv'

    prefix = filename.split('.')[0]
    prefix = prefix.replace('test_', '')
    prefix = prefix.rsplit('/', 1)[-1]
    prefix = prefix.split('_', 1)[0]

    with open(outputfilename, 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(["Date", "Intersection-set", "Class", "Count", "Color"])  # Write the header

      for i, counts in enumerate(self.intersections_counts):
        for j, (class_name, count) in enumerate(counts.items()):
            writer.writerow([prefix, i+1, class_name, count, colors[i]])

  def draw_lines(self, axs, colors):
    for i, lines in enumerate(self.line_sets):
      # Draw each line in the set
      for line in lines:
        # Draw the lines
        x1, y1, x2, y2 = line
        axs.plot([x1, x2], [y1, y2], color=colors[i % len(colors)], linewidth=2.5)