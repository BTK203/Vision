#text colors yet again

yellow='\033[1;33m'
blue='\033[0;36m'
green='\033[0;32m'
NC='\033[0m'

echo "${green}Setting up..."
echo "${blue}Installing OpenCV${NC}"
sudo apt-get --assume-yes install python-opencv

echo "${blue}Installing Tkinter UI${NC}"
sudo apt-get --assume-yes install python-tk

echo "${green}Libraries set up and ready to go.${NC}"