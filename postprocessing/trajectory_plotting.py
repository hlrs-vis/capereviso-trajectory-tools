def plot_trajectory(axs,trajectory):
    # trajectories
    # Coordinates are inverted for some reason ToDo: explain why or change!
    x = [point['x'] for point in trajectory['positions']]
    y = [point['y'] for point in trajectory['positions']]
    z = [1 for _ in range(len(x))]
    time = [point['time'] for point in trajectory['positions']]

    line, = axs.plot(x, y, color='black')
    annotation1 = axs.annotate(trajectory['global_id'], xy=(x[0], y[0]), xytext=(x[0], y[0]), fontsize=8, color='black')
    annotation2 = axs.annotate(trajectory['class_name'], xy=(x[0], y[0]), xytext=(x[0], y[0]+1), fontsize=8, color='black')

    return [line, annotation1, annotation2]

def plot_encounter(axs, encounter, trajectories):
    # Plot both trajectories stored in encounter
    objects = []
    for i in range(2):
        trajectory = trajectories[encounter[f'Trajectory{i+1}']]
        new_objects = plot_trajectory(axs, trajectory)
        objects.extend(new_objects)
        distance_annotation = axs.annotate(f"{encounter['Distance']:.2f}", xy=(0,0), xytext=(0,1), fontsize=8, color='black')
        objects.append(distance_annotation)

    return objects