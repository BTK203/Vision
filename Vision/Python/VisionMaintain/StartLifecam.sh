#text colors
blue='\033[0;36m'
NC='\033[0m'

echo "${blue}Starting Vision...${NC}"

#set the formatting options for V4L2 (yay video 4 linux!!)
v4l2-ctl -d 0 --set-fmt-video=width=600,height=400,pixelformat=YUYV
v4l2-ctl -d 0 --set-ctrl=exposure_auto=1
v4l2-ctl -d 0 --set-ctrl=exposure_absolute=5
v4l2-ctl -d 0 --set-ctrl=brightness=30
#v4l2-ctl -d 0 --set-ctrl=saturation=5

#starts the python files
python Vision.py
