from flask import Flask, render_template, request, jsonify
from models import db, Registro, Config
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not Config.query.filter_by(clave='intervalo_segundos').first():
        db.session.add(Config(clave='intervalo_segundos', valor='30'))
        db.session.commit()


@app.route('/')
def index():
    lecturas  = Registro.query.order_by(Registro.timestamp.desc()).limit(50).all()
    intervalo = int(Config.query.filter_by(clave='intervalo_segundos').first().valor)
    return render_template('index.html', lecturas=lecturas, intervalo=intervalo)


@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        temp = data.get('temp')
        hum  = data.get('hum')

        if temp is None or hum is None:
            return jsonify({"error": "Datos inválidos"}), 400

        nueva_lectura = Registro(temperatura=temp, humedad=hum)
        db.session.add(nueva_lectura)
        db.session.commit()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/readings')
def api_readings():
    lecturas = Registro.query.order_by(Registro.timestamp.desc()).all()
    return jsonify([
        {
            "id":          l.id,
            "temperatura": l.temperatura,
            "humedad":     l.humedad,
            "timestamp":   l.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for l in lecturas
    ])


@app.route('/api/config', methods=['GET'])
def get_config():
    cfg      = Config.query.filter_by(clave='intervalo_segundos').first()
    intervalo = int(cfg.valor) if cfg else 30
    return jsonify({"intervalo_segundos": intervalo}), 200


@app.route('/api/config', methods=['POST'])
def set_config():
    try:
        data  = request.get_json()
        nuevo = data.get('intervalo_segundos')

        if nuevo is None or not isinstance(nuevo, int) or nuevo < 5:
            return jsonify({"error": "Valor inválido. Mínimo 5 segundos."}), 400

        cfg = Config.query.filter_by(clave='intervalo_segundos').first()
        if cfg:
            cfg.valor = str(nuevo)
        else:
            db.session.add(Config(clave='intervalo_segundos', valor=str(nuevo)))

        db.session.commit()
        return jsonify({"status": "ok", "intervalo_segundos": nuevo}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)