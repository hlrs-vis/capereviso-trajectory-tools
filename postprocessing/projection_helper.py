import numpy as np

def img2world(image_points,invHmat):
    if image_points.ndim == 1:
        image_points = image_points.reshape(1, -1)
    all_world_points = np.array([])
    for image_pt in image_points:
        ip = np.append(image_pt.reshape(1,2),1)
        world_points = np.matmul(invHmat,ip)
        if world_points[2] == 0:  # Check if the depth value is zero
            world_points[:2] = np.inf  # Set the x and y coordinates to infinity
        elif world_points[2] < 0:  # Check if the depth value is negative
            world_points[:2] = np.nan  # Set the x and y coordinates to NaN
        else:
            world_points /= world_points[2]
        all_world_points = np.append(all_world_points, world_points.reshape(1,3)[0:2])
    all_world_points = all_world_points.reshape(-1,3)
    return all_world_points

def world2image(world_points,Hmat):
    all_image_points = np.array([])
    for world_pt in world_points:
        wp = np.append(world_pt[0:2].reshape(1,2),1)
        image_points = np.matmul(Hmat,wp)
        image_points[0] = image_points[0]/image_points[2]
        image_points[1] = image_points[1]/image_points[2]
        image_points[2] = image_points[2]/image_points[2]
        all_image_points = np.append(all_image_points, image_points[0:2].reshape(1,2))
    all_image_points = all_image_points.reshape(-1,2)
    return all_image_points