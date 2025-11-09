from flask import Blueprint, request, jsonify, session, redirect, render_template
import json, os

usuarios_bp = Blueprint('usuarios', __name__)
DB_PATH = os.path.join('database', 'users.json')

# Función para leer la base de datos JSON
def leer_usuarios():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Guardar usuarios
def guardar_usuarios(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# API: registro de usuario
@usuarios_bp.route('/api/registro', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    usuarios = leer_usuarios()

    # Validación simple
    if not data.get('usuario') or not data.get('password'):
        return jsonify({'mensaje': 'Usuario y contraseña son requeridos'}), 400

    # Evitar duplicados
    if any(u['usuario'] == data['usuario'] for u in usuarios):
        return jsonify({'mensaje': 'El usuario ya existe'}), 400

    nuevo = {
        'usuario': data['usuario'],
        'password': data['password'],
        'rol': data.get('rol', 'cliente')
    }
    usuarios.append(nuevo)
    guardar_usuarios(usuarios)
    return jsonify({'mensaje': 'Registro exitoso'}), 201

# API: inicio de sesión
@usuarios_bp.route('/api/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    usuarios = leer_usuarios()

    for u in usuarios:
        if u['usuario'] == data['usuario'] and u['password'] == data['password']:
            session['usuario'] = u['usuario']
            session['rol'] = u['rol']
            if u['rol'] == 'admin':
                return jsonify({'redirect': '/panel_admin'})
            else:
                return jsonify({'redirect': '/panel_cliente'})

    return jsonify({'mensaje': 'Credenciales incorrectas'}), 401
