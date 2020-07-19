#!/usr/bin/env python
from flask import Flask, render_template, Response
import io
import cv2
import re
from flask import request
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

def numbers(s):
    return [int(match) for match in re.findall(r"\d+", s)]

def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\John\AppData\Local\Tesseract-OCR\tesseract.exe'
    text = pytesseract.image_to_string(Image.open(filename))  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text

strID=" "
#strID = ocr_core('images/card1.png')
print("Card Info1:<"+strID +">")

#strID = ocr_core('images/card_a.png')
print("Card Infoa:<"+strID +">")
#strID = ocr_core('images/card_b.png')
print("Card Infob:<"+strID +">")
#strID = ocr_core('images/card_c.png')
print("Card Infoc:<"+strID +">")
#strID = ocr_core('images/card_d.png')
print("Card Infod:<"+strID +">")


app = Flask(__name__)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#vc = cv2.VideoCapture('face-demographics-walking-and-pause.mp4')
vc = cv2.VideoCapture('WIN_20200530_17_23_48_Pro.mp4')
videosize = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
size = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
outEnv=cv2.VideoWriter('./videos/out_env.mp4', cv2.VideoWriter_fourcc('X','V','I','D'), 20.0, videosize)
outExam=cv2.VideoWriter('./videos/out_exam.mp4', cv2.VideoWriter_fourcc('X','V','I','D'), 20.0, videosize)

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
    gen.env = 0
    while True:
        if(gen.start ==100):
            if(gen.n>10):
                outExam.release()
            break

        read_return_code, frame = vc.read()
        
        font = cv2.FONT_HERSHEY_SIMPLEX 
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # take environment video
        if gen.start==30:
            gen.env+=1
            if(gen.env<100):
                strStatus = str('%.2f'%(gen.env/100*100)) + "% of environment video is recorded."
                cv2.putText( frame,strStatus,(20,110), font,0.5,(255,0,0),2,cv2.LINE_4 )
                outEnv.write(frame)
            if(gen.env>100):
                outEnv.release()
                gen.start==0
                #gen.env=0


        if(gen.start==1):            

            gen.n+=1
            if(len(faces) == 1 ):
             gen.n1 +=1
            elif(len(faces) > 1 ):
             gen.n2 +=1
            else:
             gen.n0 +=1
            

            #if(gen.n<50):
            #outEnv.write(frame)
            #else:
            #outEnv.release()


            #strStatus = "1:"+str(n1)+" 2:"+str(n2)+" 0:"+str(n0)
            #cv2.putText( frame,strStatus,(50,50), font,1,(0,255,255),2,cv2.LINE_4 )

            #strStatus = "a face:"+str( '%.2f'%(n1/n*100))+"% multi faces:"+str('%.2f'%(n2/n*100))+"% no face:"+str('%.2f'%(n0/n*100)) + "%"
            strStatus = str( '%.1f'%(gen.n1/gen.n*100))+"% of single face"
            cv2.putText( frame,strStatus,(20,50), font,0.5,(0,255,255),2,cv2.LINE_4 )
            strStatus = str('%.1f'%(gen.n2/gen.n*100))+"% of multi faces"         
            cv2.putText( frame,strStatus,(20,80), font,0.5,(0,255,255),2,cv2.LINE_4 )
            strStatus = str('%.2f'%(gen.n0/gen.n*100)) + "% of no face"
            cv2.putText( frame,strStatus,(20,110), font,0.5,(0,255,255),2,cv2.LINE_4 )

            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Display
            #cv2.imshow('img', frame)
            
            # record exam video
            outExam.write(frame)
            
        #cv2.putText( frame,strID,(0,30), font,0.7,(0,255,0),2,cv2.LINE_4 )

        encode_return_code, image_buffer = cv2.imencode('.jpg', frame)
        io_buf = io.BytesIO(image_buffer)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + io_buf.read() + b'\r\n')

gen.n1 = 0
gen.n2 = 0
gen.n0 = 0
gen.n = 0
gen.start=0
gen.env = 0

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
        if request.form['submit_button'] == 'Take Student Photo':
            # save ID photo from video
            gen.start=0
            ret,frameId = vc.read() 
            server.currentframe += 1
            fname = './images/MyPhoto' + str(server.currentframe) + '.jpg'
            cv2.imwrite(fname, frameId) 
            return render_template('index.html',suggestion='Student Photo is taken!')            
        elif request.form['submit_button'] == 'Take ID Photo': 
            # save ID photo from video
            gen.start=0
            ret,frameId = vc.read() 
            server.currentframe += 1
            fname = './images/MyID' + str(server.currentframe) + '.jpg'
            cv2.imwrite(fname, frameId) 
            strCardInfo = " "+ocr_core(fname)+" "
            nCardNums = numbers(strCardInfo)
            strCarNum = " "
            for nCarNum in nCardNums:
                if nCarNum > 1000 :
                    strCarNum = str(nCarNum)


            # save Card Info to local txt file
            text_file = open("my ID info.txt", "w")
            text_file.write(strCardInfo)
            text_file.close()

            text_file2 = open("my ID number.txt", "w")
            text_file2.write(strCarNum)
            text_file2.close()
            #strCardInfo = ocr_core('images/card1.png')
            return render_template('index.html',suggestion='ID is taken! ID:'+strCarNum+' All info:'+strCardInfo)
        elif request.form['submit_button'] == 'Take Environment Video': 
            gen.start=30
            gen.env=0
            return render_template('index.html',suggestion='Environment video is recording!')
        elif request.form['submit_button'] == 'Start Exam':
            gen.n1 = 0
            gen.n2 = 0
            gen.n0 = 0
            gen.n = 0
            gen.start=1
            return render_template('index.html',suggestion='Exam Started')
        elif request.form['submit_button'] == 'End Exam & Send email':    
            #outEnv.release()
            #vc.release()
            retstr = " "
            if(gen.n>10):
                retstr = "total frames:"
                retstr = retstr + str(gen.n) + ' no face:' + str(gen.n0) + ' 1face:' + str(gen.n1) + ' faces:' + str(gen.n2)
                outExam.release()
                gen.start=100
            return render_template('index.html',suggestion= retstr+'Exam Ended & Sent E-Mail'+strID)
        else:
            return render_template('index.html',suggestion='...')

    # Otherwise this was a normal GET request
    else:   
        return render_template('index.html',suggestion="Waiting...")

server.currentframe = 0		

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, threaded=True)
