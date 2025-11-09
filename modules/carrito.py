from flask import Blueprint, request, jsonify, session

carrito_bp = Blueprint('carrito', __name__)

@carrito_bp.route('/api/carrito', methods=['GET'])
def obtener_carrito():
    return jsonify(session.get("carrito", []))

@carrito_bp.route('/api/carrito', methods=['POST'])
def agregar_al_carrito():
    item = request.get_json()
    carrito = session.get("carrito", [])
    carrito.append(item)
    session["carrito"] = carrito
    return jsonify({"mensaje": "Producto agregado al carrito"})

@carrito_bp.route('/api/carrito', methods=['DELETE'])
def vaciar_carrito():
    session["carrito"] = []
    return jsonify({"mensaje": "Carrito vaciado"})
