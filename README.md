# Person Location Detector
This is desktop application for real-time person location detection. This application works on Linux and Windows machines with NVIDIA GPU installed. The main end device for this application is NVIDIA Jetson Nano. Follow guidelines below in order to run the application on it.

# Steps to run the application on NVIDIA Jetson Nano
You need to perform following steps in order to run the application on NVIDIA Jetson Nano:
1. Clone the repository: `git clone https://github.com/KyryloAntoshyn/person-location-detector.git`
2. Go to the repository directory: `cd person-location-detector/`
3. Remove OpenCV that is installed with JetPack SDK: `sudo apt-get purge -y libopencv*`
4. Change *DEFAULT_VERSION* variable value inside OpenCV installation script to the OpenCV version you want to use: `nano installation/build_and_install_opencv.sh`
5. Make this script executable and run it in order to build and install OpenCV: `chmod +x installation/build_and_install_opencv.sh && installation/build_and_install_opencv.sh`
6. Install application dependencies: `sudo apt-get update && sudo apt-get install python3-pyqt5 python3-shapely`
7. Run the application: `python3 person_location_detector/person_location_detector.py`

# Neural network training scripts
This repository contains following neural network training scripts inside the *training* directory:
1. `download_coco_single_class_images.py` — can be used to download COCO dataset images for 1 class (before running you need to install *pycocotools*)
2. `generate_dataset_images_relative_paths.py` — can be used to generate dataset images relative paths (place it into the *scripts* directory inside the *darknet*)
