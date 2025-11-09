from flask import Blueprint, jsonify
from modules.flores import leer_flores

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/api/reportes/inventario')
def inventario():
    flores = leer_flores()
    for f in flores:
        f["precio_estacional"] = round(f["precio"] * 1.10, 2)
    return jsonify(flores)
