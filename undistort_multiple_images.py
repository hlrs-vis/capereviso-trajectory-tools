from toolchain import camera_stuff
import cv2 as cv
import argparse
import glob


if __name__=="__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--intrinsic", type=str, required=True,
        help="Give path to the intrinsic camera calibration")

    ap.add_argument("-f", "--file", type=str, required=False,
        help="read image from file")

    args = vars(ap.parse_args())

    intrinsic = args["intrinsic"]

    images_path = args["file"]
    #imagepath = 'backup_kalib/calibration02_img.jpg'

    brio = camera_stuff.camera(1920,1080,0)
    brio.load_intrinsic_parameters(intrinsic)

    if images_path:
        print("Reading from file...\n")
        images = glob.glob(images_path)
        for fname in images:
            img = cv.imread(fname)
            unimg = cv.undistort(img,brio.mtx,brio.dist)
            fname_undist = fname.replace(".jpg", "_undistorted.jpg")
            cv.imwrite(fname_undist, unimg)
            cv.imshow('Aufnahme',unimg)
            cv.waitKey()
    else:
        print("Opening Camera...\n")
        # Define Camera 
        brio = camera_stuff.camera(1920,1080,0)
        brio.start_camera()


        # New Image 
        img,retval = brio.run_static()


    unimg = cv.undistort(img,brio.mtx,brio.dist)

    #brio.store_extrinsic_parameters('Kalibrierung/kalibration_extrinsic')
    cv.imshow('Aufnahme',unimg)
    cv.waitKey(5000)
    print('Extrinsic calibration done')


