from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import axess
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = "une_clé_secrète_tres_forte_à_changer_en_prod"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
CORS(app, supports_credentials=True)

# Dictionnaire temporaire pour stocker les sessions utilisateur
axess_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        # Connexion à Axess
        axess_instance = axess.Axess(data['username'], data['password'])
        infos = axess_instance.getInformations()

        # Création d'un ID de session unique
        user_id = str(uuid.uuid4())
        axess_sessions[user_id] = axess_instance

        # Stocke l'ID de session dans la session Flask (cookie)
        session['user_id'] = user_id

        return jsonify({"success": True, "infos": infos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def get_user_session():
    """Récupère la session Axess associée à l'utilisateur courant"""
    user_id = session.get('user_id')
    if not user_id or user_id not in axess_sessions:
        return None
    return axess_sessions[user_id]

@app.route('/grades', methods=['GET'])
def grades():
    user_session = get_user_session()
    if not user_session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401
    return jsonify(user_session.getGrades())

@app.route('/homework', methods=['GET'])
def homework():
    user_session = get_user_session()
    if not user_session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    return jsonify(user_session.getHomeworks(tomorrow))

@app.route('/planner', methods=['GET'])
def planner():
    user_session = get_user_session()
    if not user_session:
        return jsonify({"success": False, "error": "Non authentifié"}), 401
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%d/%m/%Y')
    return jsonify(user_session.getPlanner(tomorrow))

@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.get('user_id')
    if user_id and user_id in axess_sessions:
        del axess_sessions[user_id]
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
