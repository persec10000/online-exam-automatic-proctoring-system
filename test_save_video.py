import numpy as np
import cv2

cap = cv2.VideoCapture("WIN_20200530_17_23_48_Pro.mp4")
videosize = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# Define the codec and create VideoWriter object
#fourcc = cv2.cv.CV_FOURCC(*'DIVX')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
#out = cv2.VideoWriter('output.mp4', -1, 20.0, (640,480))
out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc('X','V','I','D'), 20.0, videosize)

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
#cap.release()
out.release()
cv2.destroyAllWindows()