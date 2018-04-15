from naoqi import ALProxy
import Image
import time
import vision_definitions
import math

PORT = 9559
IP = "nao.local"

#Say Introduction
tts = ALProxy("ALTextToSpeech", IP, PORT)
tts.say("Hello, I'm Robby and this is my presentation.")

#Stand up and move
tts = ALProxy("ALTextToSpeech", IP, PORT)
postureProxy = ALProxy("ALRobotPosture", IP, 9559)
tts.say("I can stand up and walk.")
motion = ALProxy("ALMotion", IP, PORT)
motion.stiffnessInterpolation("Body", 1.0, 1.0)
postureProxy.goToPosture("StandInit", 0.5)
id = motion.post.moveTo(0.5, 0, 0)
motion.wait(id, 0)

#Move back
tts.say("Now, I'm finished walking. Now I will walk back to my original position.")
motion.post.moveTo(0.0, 0, math.pi)
motion.post.moveTo(0.5, 0, 0)
motion.post.moveTo(0.0, 0, math.pi)

#Demonstrate weight sensors
tts.say("I have sensors for measuring weight on my feet.")
time.sleep(1)
memoryProxy = ALProxy("ALMemory", IP, PORT)
LFsrFL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontLeft/Sensor/Value")
LFsrFR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/FrontRight/Sensor/Value")
LFsrBL = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearLeft/Sensor/Value")
LFsrBR = memoryProxy.getData("Device/SubDeviceList/LFoot/FSR/RearRight/Sensor/Value")
weightRF = LFsrFL + LFsrFR + LFsrBR + LFsrBL
tts.say("My left foot sensors measured about %.1f kilograms" %  (weightRF))
time.sleep(1)

#Demonstrate integrated camera
tts.say("I can also take pictures. Please smile now.")
camProxy = ALProxy("ALVideoDevice", IP, PORT)
resolution = vision_definitions.kQQVGA
colorSpace = vision_definitions.kYUVColorSpace
fps = 20
resolution = 2
colorSpace = 11
nameId = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)
naoImage = camProxy.getImageRemote(nameId)
camProxy.unsubscribe(nameId)
imageWidth = naoImage[0]
imageHeight = naoImage[1]
array = naoImage[6]
im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
im.save("camImage.png", "PNG")
im.show()
tts.say("Done. You can now see the picture on your computer.")
time.sleep(1)

#Demonstrate movement of different joints
tts.say("I can also move different joints. Now I will move my head..")
motion.setAngles("HeadYaw", 0.4, 0.05)
motion.changeAngles("HeadYaw", 0.4, 0.05)
time.sleep(1)
motion.setAngles("HeadYaw", -0.4, 0.1)
motion.changeAngles("HeadYaw",-0.4, 0.1)

#Finish presentation in sitting position
tts.say("Now the presentation is finished and I will sit down again and relax.")
postureProxy.goToPosture("Sit", 0.5)
motion.stiffnessInterpolation("Body", 0.0, 0.5)





