from flask import Flask, render_template, request
import serial

app = Flask(__name__)
arduino = serial.Serial('COM3', 9600)  # Conectează-te la Arduino prin portul serial

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control_led():
    command = request.form['command']
    arduino.write(command.encode())  # Trimite comanda către Arduino
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)