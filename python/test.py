from flask import Flask, request, jsonify
from flask_cors import CORS
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
reader = SimpleMFRC522()

app = Flask(__name__)
CORS(app)

@app.route('/write-chip', methods=['POST'])
def write_chip_endpoint():
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username ist erforderlich'}), 400
        
        # Kombiniere user und password mit einem Trennzeichen
        data = f"{username}"
        
        print("Warte auf RFID-Chip...")
        reader.write(data)
        
        return jsonify({
            'success': True,
            'message': 'Chip wurde erfolgreich beschrieben'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)