import numpy as np
import cv2 as cv
import glob
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((7*4,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:4].T.reshape(-1,2)
objp = objp*35
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('Data/*.jpg')
for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,4), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7,4), corners2, ret)
        #cv.imshow('img', img)
        #imS = cv.resize(img, (960, 540))                # Resize image
        #cv.imshow("output", imS)  
        #cv.waitKey(500)
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(f'ret: {ret}')


points = np.array([2005,1958])
points = points.transpose()
points.shape[0]

index = 0
rotvec = rvecs[index]
rotm = cv.Rodrigues(rotvec)
tranvec = tvecs[index]

mat = np.concatenate([rotm[0].transpose()[0:2,0:3],tvecs[index].transpose()])

mtx2 = mtx.transpose()

tform = np.matmul(mat,mtx2)

# X = [pts, ones(size(pts,1))]
# U = X / tform

# if isempty(U)
#   Y = zeros(0,2);
# else
#   U(:,1) = U(:,1)./U(:,3)
#   U(:,2) = U(:,2)./U(:,3)
#   Y = U(:,1:2)
#     
# (137.92 , 201,7815)