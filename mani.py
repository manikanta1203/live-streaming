from flask import Flask, Response
import cv2

app = Flask(__name__)

def generate_frames():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for Windows

    if not cap.isOpened():
        print("Cannot open camera")
        cap.release()
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture image")
            cap.release()
            break
        
        # Resize the frame to fit different screen sizes
        height, width, _ = frame.shape
        new_width = 640  # Set a new width
        new_height = int((new_width / width) * height)  # Maintain aspect ratio
        resized_frame = cv2.resize(frame, (new_width, new_height))

        ret, buffer = cv2.imencode('.jpg', resized_frame)
        if not ret:
            print("Failed to encode image")
            continue
        
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
        <!doctype html>
        <html>
        <head>
            <title>Live Video Feed</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5); /* Gradient background */
                }
                .container {
                    text-align: center;
                    border: 2px solid #fff;
                    border-radius: 12px;
                    padding: 20px;
                    background: rgba(255, 255, 255, 0.8); /* Semi-transparent background */
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                }
                h1 {
                    color: #333;
                    font-size: 2em;
                    margin-bottom: 20px;
                }
                img {
                    width: 100%;
                    height: auto;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
                }
                @media (max-width: 600px) {
                    img {
                        width: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Live Video Feed</h1>
                <img src="/video_feed" />
            </div>
        </body>
        </html>
    '''

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Server stopped by user.")
