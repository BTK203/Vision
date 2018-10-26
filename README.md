# Vision
A Computer Vision repository full of code for Raspberry Pi that makes it see things with USB cameras. It is not finished. Only java build does stuff

This repository is a heavily edited version of the starter repository provided by FIRST. Inital repository found here: https://github.com/wpilibsuite/VisionBuildSamples/

NOTE: The code from this repository is only tested for Raspberry pi running Raspbian. Run at your own risk if you heckin be running it on anything else >:D
----------------------------
Steps to build and deploy on Raspberry pi:
  ---On your Windows computer---
1). Open up CMD or a new Power Shell window and change the navigate to Vision/Java
2). type "./gradlew build" (or just "gradlew build" for CMD) and press enter to build it for RPi
3). in File Explorer there should now be a folder in Vision/Java called "output", go to that
4). Copy "CameraVision.zip" in Vision/Java/output to a USB flash drive of your choice
5). Put the USB flash drive into your RPi

 ---On the Raspberry pi---
6). Take CameraVision.zip out of the USB flash drive and put it somewhere on your Pi
7). Unzip CameraVision.zip in the folder on your Pi
8). rename the file "runCameraVision" to "runCameraVision.sh" (shell file)
9). open up a new terminal window
10). navigate the terminal to your folder with the unzipped CameraVision files
11). type "sh runCameraVision.sh" to run the application
