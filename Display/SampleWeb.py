#endoding=utf-8
from flask import Flask, render_template, Response
from managers import CameraManager
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    frameStation = CameraManager()
    while True:
        frame = frameStation.getFrame()
        if frame:
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame.getvalue() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)