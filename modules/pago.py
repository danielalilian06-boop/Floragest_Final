from flask import Blueprint, request, jsonify

pago_bp = Blueprint('pago', __name__)

@pago_bp.route('/api/pago', methods=['POST'])
def procesar_pago():
    data = request.get_json()
    metodo = data.get("metodo", "")
    if metodo not in ["tarjeta", "efectivo", "transferencia"]:
        return jsonify({"mensaje": "Método de pago no válido"}), 400
    return jsonify({"mensaje": f"Pago con {metodo} procesado exitosamente"})
