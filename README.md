# CapeReviso trajectory creation and utilities for calibration and visualization 

## Intrduction
The cameras use a fork of [tkDNN](https://github.com/hlrs-vis/tkdnn) to record data. If the system is installed to site, all calibration and data analysis can be done as postprocessing. The files saved by the system are json-files for the detection and background-images.

Calibration and postprocessing involves these steps

### 1. Calibration
After obtaining a background image, precise global positions for static points in the image shpuld be obtained. Consider satellite imagery, or own measurements with a RTK GNSS receiver.
Follow [README_calibration.md](README_calibration.md)

### 2. Creating trajectory files
With a valid calibration and a config file (you can check them with test_global_utm_calib.py), trajectory files can be created. As a reference implementation, a SORT-Tracker is used for now to work on single camera scenes (sort_create_bcrtf.py). Adding a deepSORT-Tracker for reidentification of obscured objects and among multiple cameras is work in progress.

### 3. Analyzing the trajectory files
A sample application is provided with read_trajectories.py . 


## Description of components
### Calibration-GUI
Work in Progress: A GUI for loading images from the system, marking spots with known global position coordinates and generating a calibration. 


### example_intrinsic_calibration
Intrinsic camera calibrations of Logitech Brio cameras used in the project

### ImageCoordinateTool

Tool for marking spots in images from the system for manual calibration

### intrinsicCalibration
Tool for generating intrisic calibration from a series of opencv-chessboard-markers takinf from different perspectives.

### postprocessing
Python-classes and functions used by the programs in the root directory, no standalone programs in here.

### scripts
Scripts for batch processing of recorded files

### sort
Submodule for [SORT](https://github.com/abewley/sort)

### SORT_utils
Python classes used by sort_main.py and sort_create_bcrtf.py

### toolchain
Files from an obsolete tracking algorithms, however some files are still used, for example for openCV-camera init.

### sort_create_bcrtf.py
Create trajectory files from recorded json files, using the SORT-Tracker
Usage
```
python sort_create_bcrtf.py inputfile.json -c configfile.ini
```


### read_trajectories.py
Tool for reading bcrtf-files, doing postprocessing, analyzing and visualization

Usage
```
python read_trajectories.py inputfile.bcrtf -c configfile.ini
```


### test_global_utm_calib.py
When executed with a valid config file, it will show the reference points for calibration and hint to the projection error by showing the transformed global coordinates in the image.
```
python test_global_utm_calib.py -p config.ini
```

## Installation

### Dependencies

Install eigen3 and tk
```
sudo apt-get install python3-tk
sudo apt-get install libeigen3-dev
```


### Install new Python if needed (min required 3.7)
These tools have been tested with Python>=3.7, any newer versions should be fine.

```
sudo apt-get install python3.7
sudo apt-get install python3.7-dev
apt-get install python3.7-venv
```
### Python Environment

Install pip
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```

Install Python virtual environment 
```
sudo pip install virtualenv virtualenvwrapper
```

Configure virtualenvwrapper with these lines in your .bashrc
```
# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
```

Create virtual environment for this project
```
mkvirtualenv capereviso-tools -p python3
```

Activate the environment inside the setup shell
```
workon capereviso-tools
```

install current pip and all required Python packages
```
pip install --upgrade pip
pip install -r requirements.txt
```

### OpenCV

OpenCV is not included in requirements.txt, if you want to use your CUDA-accelerated installation, follow https://pyimagesearch.com/2020/02/03/how-to-use-opencvs-dnn-module-with-nvidia-gpus-cuda-and-cudnn/

otherwise install opencv-python 

```
pip install opencv
```
Consider getting a newer CMake, if you encounter problems building the newest openCV: https://apt.kitware.com/


### Clone Repo

```
git clone git@github.com:hlrs-vis/capereviso-trajectory-tools.git
cd capereviso-trajectory-tools/
```

Sync submodules
```
git submodule sync
```

Init submodules 
```
git submodule update --init --recursive
```

```
pip install -r requirements.txt
```



