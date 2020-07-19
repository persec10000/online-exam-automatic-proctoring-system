#!/usr/bin/env python
from flask import Flask, render_template, Response
import io
import cv2
from flask import request
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\John\AppData\Local\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

strID = ocr_core('images/card1.png')
print("Card Info:"+strID)



app = Flask(__name__)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#vc = cv2.VideoCapture('face-demographics-walking-and-pause.mp4')
vc = cv2.VideoCapture('WIN_20200529_10_34_38_Pro.mp4')

n1 = 0
n2 = 0
n0 = 0
n = 2

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',suggestion="Please take ID")


def gen():
    """Video streaming generator function."""
    n1 = 0
    n2 = 0
    n0 = 0
    n=10

    while True:
        read_return_code, frame = vc.read()
        n=n+1
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if(len(faces) == 1 ):
         n1 = n1+1
        elif(len(faces) > 1 ):
         n2 = n2+1
        else:
         n0 = n0+1

        font = cv2.FONT_HERSHEY_SIMPLEX 

        #strStatus = "1:"+str(n1)+" 2:"+str(n2)+" 0:"+str(n0)
        #cv2.putText( frame,strStatus,(50,50), font,1,(0,255,255),2,cv2.LINE_4 )

        #strStatus = "a face:"+str( '%.2f'%(n1/n*100))+"% multi faces:"+str('%.2f'%(n2/n*100))+"% no face:"+str('%.2f'%(n0/n*100)) + "%"
        strStatus = str( '%.1f'%(n1/n*100))+"% of single face"
        cv2.putText( frame,strStatus,(20,50), font,0.5,(0,255,255),2,cv2.LINE_4 )
        strStatus = str('%.1f'%(n2/n*100))+"% of multi faces"         
        cv2.putText( frame,strStatus,(20,80), font,0.5,(0,255,255),2,cv2.LINE_4 )
        strStatus = str('%.2f'%(n0/n*100)) + "% of no face"
        cv2.putText( frame,strStatus,(20,110), font,0.5,(0,255,255),2,cv2.LINE_4 )

        cv2.putText( frame,strID,(0,30), font,0.7,(0,255,0),2,cv2.LINE_4 )
        # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Display
        #cv2.imshow('img', frame)

        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/', methods=['GET', 'POST'])
def server():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Take ID Photo':
            strCardInfo = ocr_core('images/card1.png')
            return render_template('index.html',suggestion='ID Photo is taken! ID info:'+strCardInfo)
        elif request.form['submit_button'] == 'Start Exam':
            return render_template('index.html',suggestion='Exam Started')
        else:
            retstr = "total:"
            retstr = retstr + str(n) + ' none:' + str(n0) + ' 1face:' + str(n1) + ' faces:' + str(n2)
            return render_template('index.html',suggestion= retstr+'Exam Ended & Sent E-Mail'+strID)

    # Otherwise this was a normal GET request
    else:   
        return render_template('index.html',suggestion="Waiting...")
		
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, threaded=True)
