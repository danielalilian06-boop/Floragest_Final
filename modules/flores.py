from flask import Blueprint, jsonify
import json, os

flores_bp = Blueprint('flores', __name__)
DB_PATH = "database/flores.json"

def leer_flores():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, 'r') as f:
        return json.load(f)

@flores_bp.route('/api/flores')
def obtener_flores():
    return jsonify(leer_flores())
