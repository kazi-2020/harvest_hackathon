from flask import Flask, render_template, Response, jsonify
import cv2
import serial
import time
from datetime import datetime
import os

app = Flask(__name__)

# Initialize variables
camera = cv2.VideoCapture(0)
arduino = serial.Serial('COM3', 9600, timeout=1)  # Change COM3 to your Arduino port
time.sleep(2)  # Wait for Arduino connection to establish

# Create directories for storing images
os.makedirs('static/accepted', exist_ok=True)
os.makedirs('static/rejected', exist_ok=True)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def process_arduino_data():
    if arduino.in_waiting:
        try:
            data = arduino.readline().decode('utf-8').strip().split(',')
            if len(data) == 3:
                return {
                    'ir_value': int(data[0]),
                    'joystick_x': int(data[1]),
                    'button_state': int(data[2])
                }
        except:
            pass
    return None

@app.route('/')
def index():
    accepted_images = os.listdir('static/accepted')
    rejected_images = os.listdir('static/rejected')
    return render_template('index.html', 
                         accepted_images=accepted_images,
                         rejected_images=rejected_images)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    success, frame = camera.read()
    if success:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = process_arduino_data()
        
        if data:
            if data['joystick_x'] > 800:  # Joystick moved right
                arduino.write(b'S')  # Trigger servo
                filepath = f'static/accepted/img_{timestamp}.jpg'
                category = 'accepted'
            else:  # Joystick moved left or neutral
                filepath = f'static/rejected/img_{timestamp}.jpg'
                category = 'rejected'
                
            cv2.imwrite(filepath, frame)
            return jsonify({'status': 'success', 'category': category})
    
    return jsonify({'status': 'error'})

@app.route('/check_ir')
def check_ir():
    data = process_arduino_data()
    if data and data['ir_value'] == 1:
        arduino.write(b'R')  # Trigger relay
        return jsonify({'triggered': True})
    return jsonify({'triggered': False})

if __name__ == '__main__':
    app.run(debug=True)