from flask import Flask, render_template, request, jsonify, Response
import cv2
from ultralytics import YOLO
import threading
import time
from datetime import datetime
import requests
import json

app = Flask(__name__)

# Global variables
camera = None
model = None
monitoring_active = False
detection_thread = None
start_time = "09:00"
end_time = "17:00"
telegram_token = "8571628822:AAH6W1aA10GbhrmQQa-x1QryMlqA3oYJY4w"
telegram_chat_id = "5294443565"
last_alert_time = 0
alert_cooldown = 60  # seconds between alerts

# Configuration
config = {
    'start_time': start_time,
    'end_time': end_time,
    'telegram_token': telegram_token,
    'telegram_chat_id': telegram_chat_id,
    'camera_source': 0,  # 0 for webcam, or RTSP URL for IP camera
    'confidence_threshold': 0.5,
    'alert_cooldown': alert_cooldown
}

def load_yolo_model():
    """Load YOLO model"""
    global model
    try:
        # Using YOLOv8n (nano) for faster detection
        # You can use 'yolov8s.pt', 'yolov8m.pt', etc. for better accuracy
        model = YOLO('yolov8n.pt')
        print("YOLO model loaded successfully")
        return True
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return False

def initialize_camera():
    """Initialize camera"""
    global camera
    try:
        camera = cv2.VideoCapture(config['camera_source'])
        if not camera.isOpened():
            print("Failed to open camera")
            return False
        print("Camera initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

def is_within_monitoring_hours():
    """Check if current time is within monitoring hours"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    start = config['start_time']
    end = config['end_time']
    
    return start <= current_time <= end

def send_telegram_alert(detection_time):
    """Send alert via Telegram"""
    global last_alert_time
    
    # Check cooldown
    current_time = time.time()
    if current_time - last_alert_time < config['alert_cooldown']:
        return
    
    if not config['telegram_token'] or not config['telegram_chat_id']:
        print("Telegram credentials not configured")
        return
    
    try:
        message = f"🚨 *Human Intrusion Detected!*\n\n"
        message += f"📍 Location: College Ground Area\n"
        message += f"⏰ Detection Time: {detection_time}\n"
        message += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"⚠️ Human detected during class hours. Please investigate."
        
        url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
        payload = {
            'chat_id': config['telegram_chat_id'],
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"Alert sent successfully at {detection_time}")
            last_alert_time = current_time
        else:
            print(f"Failed to send alert: {response.status_code}")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

def detect_humans():
    """Main detection loop"""
    global monitoring_active, camera, model
    
    while monitoring_active:
        try:
            if not is_within_monitoring_hours():
                time.sleep(30)  # Check every 30 seconds when outside hours
                continue
            
            ret, frame = camera.read()
            if not ret:
                print("Failed to read frame")
                time.sleep(1)
                continue
            
            # Run YOLO detection
            results = model(frame, conf=config['confidence_threshold'])
            
            human_detected = False
            
            # Process detections
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Check if detected object is a person (class 0 in COCO dataset)
                    if int(box.cls[0]) == 0:  # 0 = person
                        human_detected = True
                        
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        
                        # Add label
                        confidence = float(box.conf[0])
                        label = f"Person {confidence:.2f}"
                        cv2.putText(frame, label, (x1, y1-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Send alert if human detected
            if human_detected:
                detection_time = datetime.now().strftime("%H:%M:%S")
                send_telegram_alert(detection_time)
            
            # Store frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            time.sleep(0.03)  # ~30 FPS
            
        except Exception as e:
            print(f"Error in detection loop: {e}")
            time.sleep(1)

def generate_frames():
    """Generate frames for video streaming"""
    global camera, model
    
    while True:
        try:
            if camera is None or not camera.isOpened():
                time.sleep(1)
                continue
            
            ret, frame = camera.read()
            if not ret:
                continue
            
            # Only run detection during monitoring hours
            if is_within_monitoring_hours() and monitoring_active:
                results = model(frame, conf=config['confidence_threshold'])
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        if int(box.cls[0]) == 0:  # person
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            confidence = float(box.conf[0])
                            label = f"Person {confidence:.2f}"
                            cv2.putText(frame, label, (x1, y1-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Add status overlay
            status = "ACTIVE" if (monitoring_active and is_within_monitoring_hours()) else "INACTIVE"
            color = (0, 255, 0) if status == "ACTIVE" else (0, 0, 255)
            cv2.putText(frame, f"Status: {status}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            current_time = datetime.now().strftime("%H:%M:%S")
            cv2.putText(frame, f"Time: {current_time}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error generating frame: {e}")
            time.sleep(1)

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Handle configuration"""
    global config
    
    if request.method == 'GET':
        return jsonify(config)
    
    elif request.method == 'POST':
        data = request.json
        
        if 'start_time' in data:
            config['start_time'] = data['start_time']
        if 'end_time' in data:
            config['end_time'] = data['end_time']
        if 'telegram_token' in data:
            config['telegram_token'] = data['telegram_token']
        if 'telegram_chat_id' in data:
            config['telegram_chat_id'] = data['telegram_chat_id']
        if 'confidence_threshold' in data:
            config['confidence_threshold'] = float(data['confidence_threshold'])
        if 'alert_cooldown' in data:
            config['alert_cooldown'] = int(data['alert_cooldown'])
        
        # Save config to file
        with open('config.json', 'w') as f:
            json.dump(config, f)
        
        return jsonify({'status': 'success', 'config': config})

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Start monitoring"""
    global monitoring_active, detection_thread
    
    if not monitoring_active:
        monitoring_active = True
        detection_thread = threading.Thread(target=detect_humans, daemon=True)
        detection_thread.start()
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    else:
        return jsonify({'status': 'error', 'message': 'Already monitoring'})

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring"""
    global monitoring_active
    
    monitoring_active = False
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'monitoring_active': monitoring_active,
        'within_hours': is_within_monitoring_hours(),
        'current_time': datetime.now().strftime("%H:%M:%S"),
        'start_time': config['start_time'],
        'end_time': config['end_time']
    })

@app.route('/api/test_telegram', methods=['POST'])
def test_telegram():
    """Test Telegram connection"""
    try:
        if not config['telegram_token'] or not config['telegram_chat_id']:
            return jsonify({'status': 'error', 'message': 'Telegram credentials not configured'})
        
        message = "🔔 Test Alert\n\nThis is a test message from the Intrusion Detection System."
        url = f"https://api.telegram.org/bot{config['telegram_token']}/sendMessage"
        payload = {
            'chat_id': config['telegram_chat_id'],
            'text': message
        }
        
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Test alert sent successfully'})
        else:
            return jsonify({'status': 'error', 'message': f'Failed: {response.status_code}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Load config from file if exists
    try:
        with open('config.json', 'r') as f:
            saved_config = json.load(f)
            config.update(saved_config)
    except FileNotFoundError:
        pass
    
    # Initialize system
    print("Initializing system...")
    if load_yolo_model() and initialize_camera():
        print("System initialized successfully")
        print(f"Starting server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        print("Failed to initialize system")