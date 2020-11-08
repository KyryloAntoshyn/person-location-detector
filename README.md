# Person Location Detector
This is desktop application for real-time person location detection. This application works on Linux and Windows machines with NVIDIA GPU installed. The main end device for this application is NVIDIA Jetson Nano. Follow guidelines below in order to run the application on NVIDIA Jetson Nano.

# Steps to run the application on NVIDIA Jetson Nano
You need to perform following steps in order to run the application on NVIDIA Jetson Nano:
1. Clone the repository: `git clone ssh://git@gitlab.itd.pub:55522/digitalmoo/person-location-detector.git`
2. Go to the repository directory: `cd person-location-detector/`
3. Remove OpenCV that is installed with JetPack SDK: `sudo apt-get purge -y libopencv*`
4. Change *DEFAULT_VERSION* variable value to the OpenCV version you want to use inside OpenCV installation script: `nano installation/build_and_install_opencv.sh`
5. Make this script executable: `chmod +x installation/build_and_install_opencv.sh`
6. Run this script to build and install OpenCV: `installation/build_and_install_opencv.sh`
7. Install application dependencies: `sudo apt-get update && sudo apt-get install python3-pyqt5 python3-shapely`
8. Run the application: `python3 person_location_detector/person_location_detector.py`
