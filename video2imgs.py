import cv2
import os
path2videos = 'D:/oumnique/videos_inv'
path2frames = 'D:/oumnique/frames_inv'


for finger in range(5):
    os.chdir(path2videos)
    vidcap = cv2.VideoCapture(str(finger) + '.mp4') #(str(finger+1) + '.mp4') IF NUMERATION OF FINGER VIDEOS IS 1 TO 5
    success,image = vidcap.read()
    path2frames_singlefin = os.path.join(path2frames, str(finger))
    os.mkdir(path2frames_singlefin)
    os.chdir(path2frames_singlefin)
    count = 0
    while success:
        cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file      
        success,image = vidcap.read()
        print('Read a new frame: ', success)
        count += 1