from flask import Flask, render_template, request, jsonify
from models import db, Registro
import os

app = Flask(__name__)

# Configuración de SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Crear las tablas la primera vez
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    lecturas = Registro.query.order_by(Registro.timestamp.desc()).limit(50).all()
    return render_template('index.html', lecturas=lecturas)

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        temp = data.get('temp')
        hum = data.get('hum')
        
        if temp is None or hum is None:
            return jsonify({"error": "Datos inválidos"}), 400
            
        nueva_lectura = Registro(temperatura=temp, humedad=hum)
        db.session.add(nueva_lectura)
        db.session.commit()
        
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)