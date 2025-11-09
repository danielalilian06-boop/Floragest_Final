from flask import Blueprint, request, jsonify
from modules.flores import leer_flores

clientes_bp = Blueprint('clientes', __name__)

DB_CLIENTES = [
    {"id": 1, "nombre": "María López", "telefono": "5551234567", "correo": "maria@gmail.com"}
]
NEXT_CLIENTE_ID = 2

@clientes_bp.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    return jsonify(DB_CLIENTES)

@clientes_bp.route('/api/clientes', methods=['POST'])
def agregar_cliente():
    global NEXT_CLIENTE_ID
    data = request.get_json() or {}
    nuevo = {
        "id": NEXT_CLIENTE_ID,
        "nombre": data.get("nombre", ""),
        "telefono": data.get("telefono", ""),
        "correo": data.get("correo", "")
    }
    DB_CLIENTES.append(nuevo)
    NEXT_CLIENTE_ID += 1
    return jsonify({"mensaje": "Cliente agregado correctamente"}), 201

@clientes_bp.route('/api/venta', methods=['POST'])
def registrar_venta():
    data = request.get_json()
    flores = leer_flores()
    flor = next((f for f in flores if f["id"] == data["flor_id"]), None)
    if flor and flor["stock"] >= data["cantidad"]:
        flor["stock"] -= data["cantidad"]
        total = flor["precio"] * data["cantidad"]
        return jsonify({"mensaje": "Venta registrada", "total": total})
    return jsonify({"mensaje": "Stock insuficiente"}), 400
