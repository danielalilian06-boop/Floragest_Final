from flask import Flask, render_template, request, jsonify, session, redirect
import json, os, datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_flora"
DB_USERS = "database/users.json"
DB_FLORES = "database/flores.json"

# --- FUNCIONES AUXILIARES ---
def cargar_datos(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r") as f:
        return json.load(f)

def guardar_datos(ruta, datos):
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=4)

# --- RUTAS GENERALES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- API REGISTRO / LOGIN ---
@app.route("/api/registro", methods=["POST"])
def api_registro():
    data = request.get_json()
    usuarios = cargar_datos(DB_USERS)

    if any(u["username"] == data["username"] for u in usuarios):
        return jsonify({"mensaje": "El usuario ya existe"}), 400

    usuarios.append({
        "username": data["username"],
        "password": data["password"],
        "tipo": data["tipo"]
    })
    guardar_datos(DB_USERS, usuarios)
    return jsonify({"mensaje": "Registro exitoso"}), 200

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    usuarios = cargar_datos(DB_USERS)

    for u in usuarios:
        if u["username"] == data["username"] and u["password"] == data["password"]:
            session["usuario"] = u["username"]
            session["tipo"] = u["tipo"]
            destino = "/panel_admin" if u["tipo"] == "admin" else "/panel_cliente"
            return jsonify({"mensaje": f"Bienvenido {u['username']}", "destino": destino}), 200

    return jsonify({"mensaje": "Usuario o contraseña incorrectos"}), 401

# --- PANEL ADMIN ---
@app.route("/panel_admin")
def panel_admin():
    if session.get("tipo") != "admin":
        return redirect("/")
    flores = cargar_datos(DB_FLORES)
    return render_template("panel_admin.html", flores=flores, usuario=session.get("usuario"))

@app.route("/api/flores", methods=["POST"])
def agregar_flor():
    if session.get("tipo") != "admin":
        return jsonify({"mensaje": "No autorizado"}), 403
    data = request.get_json()
    flores = cargar_datos(DB_FLORES)
    flores.append(data)
    guardar_datos(DB_FLORES, flores)
    return jsonify({"mensaje": "Flor agregada exitosamente"}), 200

# --- PANEL CLIENTE ---
@app.route("/panel_cliente")
def panel_cliente():
    if session.get("tipo") != "cliente":
        return redirect("/")
    flores = cargar_datos(DB_FLORES)

    recomendaciones = {
        "Primavera": ["Rosa roja", "Tulipán", "Lirio"],
        "Verano": ["Girasol", "Hibisco", "Orquídea"],
        "Otoño": ["Crisantemo", "Dalia", "Clavel"]
    }

    return render_template(
        "panel_cliente.html",
        usuario=session.get("usuario"),
        flores=flores,
        recomendaciones=recomendaciones
    )


@app.route("/carrito")
def carrito():
    if session.get("tipo") != "cliente":
        return redirect("/")
    return render_template("carrito.html", usuario=session.get("usuario"))

@app.route("/soporte")
def soporte():
    if session.get("tipo") != "cliente":
        return redirect("/")
    return render_template("soporte.html", usuario=session.get("usuario"))

@app.route("/api/compra", methods=["POST"])
def procesar_compra():
    data = request.get_json()
    usuario = session.get("usuario")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ticket = {
        "usuario": usuario,
        "fecha": fecha,
        "items": data["carrito"],
        "direccion": data["direccion"],
        "pago": data["pago"]
    }
    return jsonify({
        "mensaje": "Compra realizada con éxito",
        "ticket": ticket
    }), 200

if __name__ == "__main__":
    os.makedirs("database", exist_ok=True)
    if not os.path.exists(DB_USERS):
        guardar_datos(DB_USERS, [])
    if not os.path.exists(DB_FLORES):
        flores_demo = [
            {"nombre": "Rosa roja", "precio": 25},
            {"nombre": "Tulipán", "precio": 30},
            {"nombre": "Girasol", "precio": 20},
            {"nombre": "Lirio", "precio": 28}
        ]
        guardar_datos(DB_FLORES, flores_demo)
    app.run(debug=True)

@app.route("/api/flores/<nombre>", methods=["DELETE"])
def eliminar_flor(nombre):
    if session.get("tipo") != "admin":
        return jsonify({"mensaje": "No autorizado"}), 403

    flores = cargar_datos(DB_FLORES)
    nuevas_flores = [f for f in flores if f["nombre"] != nombre]

    if len(nuevas_flores) == len(flores):
        return jsonify({"mensaje": "Flor no encontrada"}), 404

    guardar_datos(DB_FLORES, nuevas_flores)
    return jsonify({"mensaje": f'Flor "{nombre}" eliminada correctamente'}), 200

