from flask import Flask, render_template, jsonify, request
import serial
import time
from flask_mail import Mail, Message
import threading

app = Flask(__name__)

# Set up the serial connection to the Arduino
arduino = serial.Serial('/dev/cu.usbmodemF412FA636BC02', 9600, timeout=1)
time.sleep(2)  # Give some time for the serial connection to initialize

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'emailu_tau'
app.config['MAIL_PASSWORD'] = 'parola_mail'

mail = Mail(app)

def send_email(subject, recipient, body):
    try:
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        print("Email trimis cu succes!")
    except Exception as e:
        print(f"Error: {e}")

def listen_to_serial():
    while True:
        data = read_arduino()
        if "Flood detected!" in data:
            send_email("Inundatie detectata !!", "destinatar@example.com", "O inundatie a fost sesizata, va rugam sa contactati pompierii")
            print("Inundatie detectata, emailul trimis !!") 

def read_arduino():
    arduino.flush()
    data = arduino.readline().decode('utf-8').strip()
    return data

def toggle_led():
    action = request.form.get("action")
    print("Received action:", action)  # Add this line for debugging
    if action == "on":
        arduino.write(b'A')
    elif action == "off":
        arduino.write(b'S')
    return jsonify(success=True)

def fetch_status():
    temperature = None
    led_status = None
    while True:
        data = read_arduino()
        print("Received data:", data)  # Add this line for debugging
        if ":" in data:
            parts = data.split(":")
            if len(parts) == 2:
                key, value = parts
                if key.strip() == "Temperature":
                    temperature = value.strip()
                elif key.strip() == "LED":
                    led_status = value.strip()
        if temperature is not None and led_status is not None:
            break
    return temperature, led_status


@app.route("/")
def home():
    temperature, led_status = fetch_status()
    return render_template("index.html", temperature=temperature, led_status=led_status)

@app.route("/toggle_led", methods=["POST"])
def toggle_led():
    action = request.form.get("action")
    if action == "on":
        arduino.write(b'A')
    elif action == "off":
        arduino.write(b'S')
    return jsonify(success=True)

@app.route("/get_status")
def get_status():
    temperature, led_status = fetch_status()
    return jsonify(temperature=temperature, led_status=led_status)

if __name__ == "_main_":
    serial_thread = threading.Thread(target=listen_to_serial)
    serial_thread.daemon = True
    serial_thread.start()
    app.run(debug=True)