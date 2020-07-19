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
print("Card Info1:<"+strID +">")

strID = ocr_core('images/card_a.png')
print("Card Infoa:<"+strID +">")
strID = ocr_core('images/card_b.png')
print("Card Infob:<"+strID +">")
strID = ocr_core('images/card_c.png')
print("Card Infoc:<"+strID +">")
strID = ocr_core('images/card_d.png')
print("Card Infod:<"+strID +">")


app = Flask(__name__)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#vc = cv2.VideoCapture('face-demographics-walking-and-pause.mp4')
vc = cv2.VideoCapture('WIN_20200530_17_23_48_Pro.mp4')



@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',suggestion="Please take ID")


def gen():
    """Video streaming generator function."""
    gen.n1 = 0
    gen.n2 = 0
    gen.n0 = 0
    gen.n = 0

    while True:
        read_return_code, frame = vc.read()
        gen.n+=1
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if(len(faces) == 1 ):
         gen.n1 +=1
        elif(len(faces) > 1 ):
         gen.n2 +=1
        else:
         gen.n0 +=1

        font = cv2.FONT_HERSHEY_SIMPLEX 

        #strStatus = "1:"+str(n1)+" 2:"+str(n2)+" 0:"+str(n0)
        #cv2.putText( frame,strStatus,(50,50), font,1,(0,255,255),2,cv2.LINE_4 )

        #strStatus = "a face:"+str( '%.2f'%(n1/n*100))+"% multi faces:"+str('%.2f'%(n2/n*100))+"% no face:"+str('%.2f'%(n0/n*100)) + "%"
        strStatus = str( '%.1f'%(gen.n1/gen.n*100))+"% of single face"
        cv2.putText( frame,strStatus,(20,50), font,0.5,(0,255,255),2,cv2.LINE_4 )
        strStatus = str('%.1f'%(gen.n2/gen.n*100))+"% of multi faces"         
        cv2.putText( frame,strStatus,(20,80), font,0.5,(0,255,255),2,cv2.LINE_4 )
        strStatus = str('%.2f'%(gen.n0/gen.n*100)) + "% of no face"
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

gen.n1 = 0
gen.n2 = 0
gen.n0 = 0
gen.n = 0

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
            # save ID photo from video
            ret,frameId = vc.read() 
            server.currentframe += 1
            fname = './images/frame' + str(server.currentframe) + '.jpg'
            cv2.imwrite(fname, frameId) 
            strCardInfo = " "+ocr_core(fname)+" "
            #strCardInfo = ocr_core('images/card1.png')
            return render_template('index.html',suggestion='ID is taken!'+strCardInfo)
        elif request.form['submit_button'] == 'Start Exam':
            return render_template('index.html',suggestion='Exam Started')
        else:
            retstr = "total frames:"
            retstr = retstr + str(gen.n) + ' no face:' + str(gen.n0) + ' 1face:' + str(gen.n1) + ' faces:' + str(gen.n2)
            return render_template('index.html',suggestion= retstr+'Exam Ended & Sent E-Mail'+strID)

    # Otherwise this was a normal GET request
    else:   
        return render_template('index.html',suggestion="Waiting...")

server.currentframe = 0		

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, threaded=True)
