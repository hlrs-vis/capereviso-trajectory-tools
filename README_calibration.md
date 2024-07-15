# Calibration of CapeReviso Camera System

## Prerequisites
### Instrinsic calibration with chessboard markers
Some routines to capture these on a system (including IDS-Cameras) are included with the tkDNN-Fork, so calibration can be done with the same sttings as image capturing later on.

## Distort the background image of the location using the intrinsic calibration
`python undistort_single_image.py -i  calibration/calibration02_i -f vhs-calibration/visagx2_background_image_2022-11-30_11-41-11.jpg`

## Convert a csv-File to opencv-file containing obj-points
`python utmcoordinatetransform.py vhs.cvs` will result in a YAML-file with object points

## Extrinsic calibration 
`python ImageCoordinatesTool2.py -p vhs-calibration/visagx2_background_image_2022-11-30_11-41-11_undistorted.jpg` will result in a YAML-file with image points
If the same locations are chosen in the same order as in the previous step converting the csv file, the resulting files can work together.

## Edit config
image_pts_path = vhs-calibration/visagx2_background_image_2022-11-30_11-41-11_undistorted_2022_12_12_1516.yml
object_pts_path = vhs-calibration/vhs_obj_points_2022-12-13_1315.yml
calibration_image_path = vhs-calibration/visagx2_background_image_2022-11-30_11-41-11_undistorted.jpg


## Check calibration by running 
`python test_global_utm_calib.py -p vhs-calibration/config_vhs_wg_noshow.ini`

