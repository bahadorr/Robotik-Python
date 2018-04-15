#Name:
#Bahador Yousefpour
import cv2
import time
import imutils
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import almath
from naoqi import ALProxy
from vision_definitions import kQVGA,kBGRColorSpace

NAO="nao.local"

#converts the distance to speed. Greater distance -> Greater speed
def pixelToSpeed(pixels):
    speed = pixels/320
    if speed < 0.1:
        speed = 0.1
    return speed

if __name__=="__main__":    # this is to check if we are importing 
    
    camera_index=0 # top camera
    
    # http://colorizer.org/
    # define the lower and upper boundaries of the "yellow"
    # ball in the HSV color space, then initialize the

    #for yellow ball
    yellowLower = (25, 86, 6)
    yellowUpper = (35, 255, 255)

    #red ball
    redLower = (0, 80, 75)
    redUpper = (5, 255, 255)

    #colorLower = yellowLower
    #colorUpper = yellowUpper
    colorLower = redLower
    colorUpper = redUpper

    # Create a proxy for ALVideoDevice
    name="nao_opencv"
    video=ALProxy("ALVideoDevice",NAO,9559)    

    # subscribe to video device on a specific camera # BGR for opencv
    name=video.subscribeCamera(name,camera_index,1,kBGRColorSpace,30) 
    print "subscribed name",name

    x_previous = 160
    y_previous = 120
    
    try: 
        frame=None
        # keep looping
        while True:
            key=cv2.waitKey(33)&0xFF
            if  key == ord('q') or key==27:
                break

            # obtain image
            alimg=video.getImageRemote(name)
            
            # extract fields
            width=alimg[0]
            height=alimg[1]
            nchannels=alimg[2]
            imgbuffer=alimg[6]
                            
            # build opencv image (allocate on first pass)
            if frame is None:
                print 'Grabbed image: ',width,'x',height,' nchannels=',nchannels
                frame=np.asarray(bytearray(imgbuffer), dtype=np.uint8)
                frame=frame.reshape((height,width,3))
            else:
                frame.data=bytearray(imgbuffer)
            
            # Smoothing Images 
            # http://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html#gsc.tab=0 
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            # Converts an image from one color space to another 
            #http://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html#gsc.tab=0
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # construct a mask for the color, then perform
            #  a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, colorLower, colorUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)


		    #move the head
		    motionProxy = ALProxy("ALMotion", NAO, 9559)
		    motionProxy.setStiffnesses("Head", 1.0)

                    yawCurrent = motionProxy.getAngles("HeadYaw", True)
                    pitchCurrent = motionProxy.getAngles("HeadPitch", True)

                    #Debug information
                    print "Current Yaw: " ,yawCurrent
                    print "CurrenPitch: " , pitchCurrent
                    print "Ball X: " ,x
                    print "Ball Y: " ,y

                    #Pixel sizes according to the camera resolution
		    x_size = 320
	            y_size = 240

                    #Retrieve the movement area of the head in RAD
	            max_yaw_rad = video.getHorizontalFOV(0)
	            max_pitch_rad = video.getVerticalFOV(0)


                    #calculate the relatvie distance from the pixels in order to convert it the actual movement in RAD
                    relative_distance_x = x/x_size
                    relative_distance_y = y/y_size
                    pitchAngleRad = (relative_distance_y * max_pitch_rad - max_pitch_rad/2) 
                    yawAngleRad = (relative_distance_x * max_yaw_rad - max_yaw_rad/2)  

                    #for debug purposes
                    print "PitchAngle: " ,pitchAngleRad
                    print "YawAngle: " ,yawAngleRad


                    #calculate speed depending on the distance in pixels
                    speed_y = pixelToSpeed(abs(y - y_previous))
                    speed_x = pixelToSpeed(abs(x - x_previous))

                    #no motion for small distances because it creates a problem
                    if (abs(yawAngleRad) > 0.12):
                        motionProxy.post.changeAngles("HeadYaw", -yawAngleRad, speed_x)
                    if (abs(pitchAngleRad) > 0.12):
                        motionProxy.post.changeAngles("HeadPitch", pitchAngleRad, speed_y)
                     
                    x_previous = x
                    y_previous = y

            # show the frame to our screen
            # Do not run this code if your run your python in the robot 
            # NAO has no screen to show 
            cv2.imshow("Frame", frame) 

    finally: # if anything goes wrong we'll make sure to unsubscribe
        print "unsubscribing",name
        video.unsubscribe(name)

        #moves the head back to neutral and removes stiffness
        motion = ALProxy("ALMotion", NAO, 9559)
        motion.setStiffnesses("Head", 1.0)
        motion.setAngles("HeadYaw", 0.0, 0.3)
        motion.setAngles("HeadPitch", 0.0, 0.3)
        time.sleep(0.5)
        motion.setStiffnesses("Body", 0.0)
        time.sleep(0.5)
