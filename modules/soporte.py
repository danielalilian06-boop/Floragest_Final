from flask import Blueprint, jsonify

soporte_bp = Blueprint('soporte', __name__)

@soporte_bp.route('/api/soporte')
def soporte_info():
    return jsonify({"correo": "soporte@floragest.com", "telefono": "55-5555-5555"})
