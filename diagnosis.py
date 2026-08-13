#!/usr/bin/env python3
"""
System Diagnostic Script for Intrusion Detection System
Run this to check if all dependencies and hardware are working correctly
"""

import sys
import os

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_python_version():
    print_section("Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.8 or higher required")
        return False

def check_opencv():
    print_section("OpenCV")
    try:
        import cv2
        print(f"✓ OpenCV installed: {cv2.__version__}")
        return True
    except ImportError:
        print("✗ OpenCV not installed")
        print("Install with: pip install opencv-python")
        return False

def check_flask():
    print_section("Flask")
    try:
        import flask
        print(f"✓ Flask installed: {flask.__version__}")
        return True
    except ImportError:
        print("✗ Flask not installed")
        print("Install with: pip install flask")
        return False

def check_ultralytics():
    print_section("Ultralytics YOLO")
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics installed")
        
        # Try to load model
        print("Attempting to load YOLOv8 model...")
        try:
            model = YOLO('yolov8n.pt')
            print("✓ YOLOv8 model loaded successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            return False
    except ImportError:
        print("✗ Ultralytics not installed")
        print("Install with: pip install ultralytics")
        return False

def check_requests():
    print_section("Requests Library")
    try:
        import requests
        print(f"✓ Requests installed: {requests.__version__}")
        return True
    except ImportError:
        print("✗ Requests not installed")
        print("Install with: pip install requests")
        return False

def check_camera():
    print_section("Camera Test")
    try:
        import cv2
        print("Testing camera (source 0)...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("✗ Cannot open camera (source 0)")
            print("\nTroubleshooting:")
            print("  - Check if camera is connected")
            print("  - Try different camera sources (1, 2, etc.)")
            print("  - Check camera permissions")
            return False
        
        ret, frame = cap.read()
        if not ret:
            print("✗ Camera opened but cannot read frames")
            cap.release()
            return False
        
        height, width = frame.shape[:2]
        print(f"✓ Camera working: {width}x{height}")
        cap.release()
        return True
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def check_templates():
    print_section("Template Files")
    if os.path.exists('templates'):
        print("✓ templates/ directory exists")
        if os.path.exists('templates/index.html'):
            print("✓ templates/index.html exists")
            return True
        else:
            print("✗ templates/index.html not found")
            print("Create templates/index.html from the provided code")
            return False
    else:
        print("✗ templates/ directory not found")
        print("Create a 'templates' folder and add index.html")
        return False

def check_config():
    print_section("Configuration")
    if os.path.exists('config.json'):
        print("✓ config.json exists")
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
            print(f"  Start time: {config.get('start_time', 'Not set')}")
            print(f"  End time: {config.get('end_time', 'Not set')}")
            print(f"  Camera source: {config.get('camera_source', 'Not set')}")
            return True
        except Exception as e:
            print(f"✗ Error reading config.json: {e}")
            return False
    else:
        print("⚠ config.json not found (will be auto-created)")
        return True

def test_telegram():
    print_section("Telegram Configuration (Optional)")
    try:
        import json
        if not os.path.exists('config.json'):
            print("⚠ config.json not found - skip Telegram test")
            return True
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        token = config.get('telegram_token', '')
        chat_id = config.get('telegram_chat_id', '')
        
        if not token or not chat_id:
            print("⚠ Telegram credentials not configured")
            print("You can configure this later via web interface")
            return True
        
        print(f"Token: {token[:10]}...")
        print(f"Chat ID: {chat_id}")
        
        import requests
        print("Testing Telegram connection...")
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"✓ Telegram bot connected: @{data['result']['username']}")
                return True
        
        print("✗ Telegram connection failed")
        print("Check your bot token")
        return False
        
    except Exception as e:
        print(f"⚠ Telegram test skipped: {e}")
        return True

def run_diagnostics():
    print("\n" + "#"*60)
    print("#  INTRUSION DETECTION SYSTEM - DIAGNOSTIC TOOL")
    print("#"*60)
    
    results = {
        'Python Version': check_python_version(),
        'Flask': check_flask(),
        'OpenCV': check_opencv(),
        'Requests': check_requests(),
        'Ultralytics YOLO': check_ultralytics(),
        'Camera': check_camera(),
        'Template Files': check_templates(),
        'Configuration': check_config(),
        'Telegram': test_telegram()
    }
    
    print_section("Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}\n")
    
    for test, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {test}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print("✓ All checks passed! System ready to run.")
        print("\nStart the system with: python app.py")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        print("\nQuick fix commands:")
        print("  pip install -r requirements.txt")
        print("  mkdir templates")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        run_diagnostics()
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()