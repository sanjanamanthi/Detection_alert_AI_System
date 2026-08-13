# Detection_alert_AI_System

# Real-Time Human Intrusion Detection and Alert System

## Overview
This system monitors outdoor areas (like college grounds) during predefined class hours and automatically detects human presence using YOLO object detection. When humans are detected during monitoring hours, alerts are sent via Telegram.

## Features
- ✅ Real-time human detection using YOLOv8
- ✅ Time-based monitoring (configurable class hours)
- ✅ Live video feed with bounding box visualization
- ✅ Telegram alerts with cooldown period
- ✅ Web-based configuration interface
- ✅ Adjustable confidence threshold
- ✅ Support for webcam or IP camera (RTSP)

## Project Structure
```
intrusion-detection/
│
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── config.json              # Configuration file (auto-generated)
└── templates/
    └── index.html           # Web interface
```

## Installation

### Step 1: Install Python
Make sure you have Python 3.8+ installed:
```bash
python --version
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download YOLO Model
The YOLOv8 model will be automatically downloaded on first run. If you want to download it manually:
```python
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Downloads yolov8n.pt
```

## Setting Up Telegram Bot

### Step 1: Create a Telegram Bot
1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. Follow the instructions to create your bot
4. Copy the **Bot Token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Search for **@userinfobot** on Telegram
2. Start a chat and it will send you your Chat ID
3. Copy the **Chat ID** (format: `123456789`)

**For Group Alerts:**
1. Create a group and add your bot to it
2. Make the bot an admin
3. Send a message in the group
4. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Look for `"chat":{"id":-123456789}` - this is your group Chat ID (negative number)

## Configuration

### Camera Setup

**For Webcam:**
- Default camera source is `0`
- In `app.py`, line 26: `'camera_source': 0`

**For IP Camera (RTSP):**
- Replace camera source with RTSP URL
- Example: `'camera_source': 'rtsp://username:password@192.168.1.100:554/stream'`

### Using the Web Interface

1. **Start the Application:**
```bash
python app.py
```

2. **Open Browser:**
- Navigate to `http://localhost:5000`

3. **Configure Settings:**
- **Class Start Time**: When monitoring should begin (e.g., 09:00)
- **Class End Time**: When monitoring should end (e.g., 17:00)
- **Telegram Bot Token**: Your bot token from BotFather
- **Telegram Chat ID**: Your chat or group ID
- **Confidence Threshold**: Detection confidence (0.1 - 1.0, default: 0.5)
- **Alert Cooldown**: Seconds between alerts (default: 60)

4. **Save Configuration:**
- Click "Save Configuration"

5. **Test Telegram:**
- Click "Test Telegram" to verify connection

6. **Start Monitoring:**
- Click "Start" button
- System will only detect during configured hours

## Usage Guide

### Normal Operation Flow

1. **Start the system:**
   ```bash
   python app.py
   ```

2. **Configure monitoring hours** via web interface

3. **Enter Telegram credentials** and test connection

4. **Click "Start"** to begin monitoring

5. **System behavior:**
   - **Outside class hours**: Monitoring inactive, no detection
   - **During class hours**: Active detection, sends alerts
   - **Human detected**: Red bounding box + Telegram alert
   - **Alert cooldown**: Prevents spam (default: 60 seconds)

### Monitoring Multiple Areas

To monitor multiple areas, run separate instances:

```bash
# Instance 1 - Port 5000
python app.py

# Instance 2 - Port 5001
# Modify app.py: app.run(port=5001)
```

## Troubleshooting

### Camera Not Working
```python
# Test camera connection
import cv2
cap = cv2.VideoCapture(0)  # or RTSP URL
print(cap.isOpened())
cap.release()
```

### YOLO Model Issues
```bash
# Reinstall ultralytics
pip uninstall ultralytics
pip install ultralytics==8.0.226

# Clear cache
rm -rf ~/.cache/torch/hub/ultralytics_yolov8*
```

### Telegram Not Sending
- Verify bot token is correct
- Check chat ID (include negative sign for groups)
- Ensure bot is admin in group
- Test with curl:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### Port Already in Use
```bash
# Change port in app.py (last line):
app.run(host='0.0.0.0', port=5001)
```

## Advanced Configuration

### Using Different YOLO Models

For better accuracy (slower):
```python
# In app.py, line ~41
model = YOLO('yolov8m.pt')  # Medium
model = YOLO('yolov8l.pt')  # Large
model = YOLO('yolov8x.pt')  # Extra large
```

For faster detection (less accurate):
```python
model = YOLO('yolov8n.pt')  # Nano (default)
model = YOLO('yolov8s.pt')  # Small
```

### Adjusting Detection Parameters

In `app.py`, modify:
```python
# Confidence threshold (higher = fewer false positives)
results = model(frame, conf=0.7)  # Default: 0.5

# Alert cooldown (seconds between alerts)
alert_cooldown = 120  # Default: 60
```

### Recording Detections

Add to `detect_humans()` function:
```python
if human_detected:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"detections/detection_{timestamp}.jpg", frame)
```

## System Requirements

- **Minimum:**
  - Python 3.8+
  - 4GB RAM
  - Webcam or IP camera
  - Internet connection (for Telegram)

- **Recommended:**
  - Python 3.10+
  - 8GB RAM
  - GPU with CUDA support (for faster detection)
  - Stable network connection

## Running on Startup (Linux)

Create systemd service:
```bash
sudo nano /etc/systemd/system/intrusion-detection.service
```

Add:
```ini
[Unit]
Description=Intrusion Detection System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/intrusion-detection
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable intrusion-detection
sudo systemctl start intrusion-detection
```

## Security Considerations

1. **Protect Telegram credentials** - Don't commit config.json to git
2. **Use HTTPS** for production deployment
3. **Implement authentication** for web interface in production
4. **Secure camera streams** with proper network configuration
5. **Regular backups** of configuration files

## Performance Optimization

### For Low-End Systems:
```python
# Reduce frame processing rate
time.sleep(0.1)  # Process 10 fps instead of 30

# Use smaller model
model = YOLO('yolov8n.pt')

# Lower resolution
frame = cv2.resize(frame, (640, 480))
```

### For High-End Systems:
```python
# Use GPU acceleration (if CUDA available)
model = YOLO('yolov8x.pt')  # Largest model
model.to('cuda')

# Higher frame rate
time.sleep(0.01)  # ~100 fps
```

## Future Enhancements

- 🔄 Multi-camera support
- 📊 Detection analytics and reports
- 💾 Database integration for logging
- 📧 Email alerts
- 🔐 User authentication
- 📱 Mobile app
- 🎯 Zone-based detection
- 📹 Recording on detection

## Support

For issues or questions:
1. Check troubleshooting section
2. Review logs in console output
3. Test individual components (camera, YOLO, Telegram)
4. Verify configuration settings

## License

This project is for educational and security purposes.

## Credits

- **YOLO**: Ultralytics YOLOv8
- **Framework**: Flask
- **Computer Vision**: OpenCV
- **Alerts**: Telegram Bot API
