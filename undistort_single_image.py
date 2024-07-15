from toolchain import camera_stuff
import cv2 as cv
import argparse

if __name__=="__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--intrinsic", type=str, required=True,
        help="Give path to the intrinsic camera calibration")

    ap.add_argument("-s", "--save", type=str, required=True,
        help="Set path to save the undisturbed calibration image")

    ap.add_argument("-f", "--file", type=str, required=False,
        help="read image from file")

    args = vars(ap.parse_args())

    intrinsic = args["intrinsic"]
    save = args["save"]
    file = args["file"]
    #imagepath = 'backup_kalib/calibration02_img.jpg'

    brio = camera_stuff.camera(1920,1080,0)

    if file:
        print("Reading from file...\n")
        img = cv.imread(file, 1)
    else:
        print("Opening Camera...\n")
        # Define Camera 
        brio = camera_stuff.camera(1920,1080,0)
        brio.start_camera()


        # New Image 
        img,retval = brio.run_static()

    brio.load_intrinsic_parameters(intrinsic)

    unimg = cv.undistort(img,brio.mtx,brio.dist)

    #brio.store_extrinsic_parameters('Kalibrierung/kalibration_extrinsic')
    cv.imwrite(save, unimg)
    cv.imshow('Aufnahme',unimg)
    cv.waitKey(5000)
    print('Saved undistorted Image')


