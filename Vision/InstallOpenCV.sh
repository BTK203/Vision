#Text Colors! dont change
#
yellow='\033[1;33m'
blue='\033[0;36m'
green='\033[0;32m'
NC='\033[0m'

confirm = ""
update = ""
#make sure that the user really meant to launch script
echo "${yellow}This script will install OpenCV for C++ and Python, along with any necessary libraries. The process may take several hours. Do you want to continue? [y,n]"
read confirm
if [ "$confirm" = 'y' ];
then
#see if system needs update
	echo "${yellow} Do you want to update your system? [y,n]"
	read update
	if [ "$update" = 'y' ]
	then
		sudo apt-get update
		sudo apt-get upgrade
		sudo rpi-update
		sudo reboot
	fi
	
	#now install opencv
	echo "${green} Preparing to download OpenCV"
	echo "${blue} Removing old outdated libraries..."
	echo "${NC}"
	sudo apt-get --assume-yes autoremove
	
	echo "${blue}Installing devel tools...${NC}"
	sudo apt-get --assume-yes install build-essential cmake cmake-curses-gui pkg-config
	
	echo "${green}Installing OpenCV Dependencies...${NC}"
	sudo apt-get --assume-yes install libjpeg-dev
	
	echo "${blue}Install libtiff5-dev${NC}"
	sudo apt-get --assume-yes install libtiff5-dev 

	echo "${blue}Install libjasper-dev${NC}"
	sudo apt-get --assume-yes install libjasper-dev

	echo "${blue}Install libpng12-dev${NC}"
	sudo apt-get --assume-yes install libpng12-dev

	echo "${blue}Install libavcodec-dev${NC}"
	sudo apt-get --assume-yes install libavcodec-dev

	echo "${blue}Install libavformat-dev${NC}"
	sudo apt-get --assume-yes install libavformat-dev

	echo "${blue}Install libswscale-dev${NC}"
	sudo apt-get --assume-yes install libswscale-dev

	echo "${blue}Install libeigen3-dev${NC}"
	sudo apt-get --assume-yes install libeigen3-dev

	echo "${blue}Install libxvidcore-dev${NC}"
	sudo apt-get --assume-yes install libxvidcore-dev

	echo "${blue}Install libx264-dev${NC}"
	sudo apt-get --assume-yes install libx264-dev

	echo "${blue}Install libgtk2.0-dev${NC}"
	sudo apt-get --assume-yes install libgtk2.0-dev

	echo "${blue}Installing Video4Linux${NC}"
	sudo apt-get -y --assume-yes install libv4l-dev v4l-utils
	sudo modprobe bcm2835-v4l2
	
	echo "${blue}Installing a few last dependencies${NC}"
	sudo apt-get --assume-yes install libatlas-base-dev
	sudo apt-get --assume-yes install gfortran
	
	echo "${blue}Installing some python things...${NC}"
	sudo apt-get --assume-yes install python2.7-dev
	sudo apt-get --assume-yes install python3-dev
	sudo apt-get --assume-yes install python2-numpy
	sudo apt-get --assume-yes install python3-numpy
	
	echo "${green}Downloading OpenCV...${NC}"
	cd
	mkdir OpenCV
	cd OpenCV
	wget https://github.com/opencv/opencv/archive/3.2.0.zip -O opencv_source.zip
	wget https://github.com/opencv/opencv_contrib/archive/3.2.0.zip -O opencv_contrib.zip
	
	echo "${green}Unzipping OpenCV...${NC}"
	unzip opencv_source.zip
	unzip opencv_contrib.zip
	
	echo "${blue}Preparing to compile OpenCV...${NC}"
	cd opencv-3.2.0
	mkdir build
	cd build
	cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D BUILD_WITH_DEBUG_INFO=OFF \
-D BUILD_DOCS=OFF \
-D BUILD_EXAMPLES=OFF \
-D BUILD_TESTS=OFF \
-D BUILD_opencv_ts=OFF \
-D BUILD_PERF_TESTS=OFF \
-D INSTALL_C_EXAMPLES=ON \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-3.2.0/modules \
-D ENABLE_NEON=ON \
-D WITH_LIBV4L=ON \
-D BUILD_SHARED_LIBS=OFF \
../

	echo "${blue}Compiling...${NC}"
	make 
	echo "${blue}Finishing up...${NC}"
	sudo make install 
	sudo ldconfig

fi

