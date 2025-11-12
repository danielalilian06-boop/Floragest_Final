# app.py
from flask import Flask, render_template, request, jsonify, session, redirect
import json, os, datetime, random, re

app = Flask(__name__)
app.secret_key = "clave_secreta_flora"
DB_USERS = "database/users.json"
DB_FLORES = "database/flores.json"

# --- FUNCIONES AUXILIARES ---
def cargar_datos(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- RESPUESTAS SIMULADAS (IA MOCK) ---
RESPONSES_GENERIC = [
    "Las flores tienen ciclos de floración influenciados por la temperatura y la cantidad de luz; por eso algunas se ven más en cierta temporada.",
    "Muchas flores aparecen en una temporada específica porque las condiciones (temperatura, humedad y luz) favorecen su desarrollo y polinización.",
    "Además de la estación, la disponibilidad comercial y la tradición local también influyen en qué flores vemos más en cada época."
]

# Mapa por palabra clave -> respuestas específicas (varias alternativas)
RESPONSES_KEYWORD = {
    "girasol": [
        "Los girasoles son típicos del verano por su preferencia a días largos y luz intensa; además su estructura aprovecha bien la luz solar.",
        "En verano los girasoles reciben más horas de sol, lo que favorece su tamaño y color brillante.",
        "Son resistentes al calor y producen muchas flores cuando la radiación es alta, por eso se asocian al verano."
    ],
    "rosa": [
        "Las rosas pueden florecer en varias temporadas, pero muchas variedades comerciales tienen picos en primavera y otoño.",
        "La rosa es muy cultivada y existen variedades de temporada extendida gracias a la selección y los invernaderos.",
        "Para arreglos, la rosa roja suele usarse todo el año, pero su temporada natural tiene picos en climas templados."
    ],
    "tulipán": [
        "Los tulipanes son típicos de primavera porque requieren un periodo frío previo para romper la latencia y florecer al subir las temperaturas.",
        "Necesitan veranos relativamente fríos y un invierno para estacionalizar sus bulbos, por eso florecen en primavera.",
        "Los tulipanes se plantan en otoño para que pasen el invierno bajo el suelo y broten en primavera."
    ],
    "lirio": [
        "Los lirios suelen florecer en primavera y verano, dependiendo de la variedad; prefieren suelos bien drenados y clima templado.",
        "Algunas especies de lirio tienen picos en primavera, mientras que otras en pleno verano; la variedad determina la temporada."
    ],
    "girasoles": [],  # por si usan plural
    "verano": [
        "En verano predominan plantas que toleran calor y sequía relativa; su fisiología favorece flores grandes y vistosas.",
        "Los comerciantes también aprovechan la demanda estival para ofrecer especies como girasoles y hibiscos."
    ],
    "primavera": [
        "La primavera trae temperaturas suaves y lluvias moderadas, condiciones ideales para muchas bulbosas y floraciones masivas.",
        "Es la temporada con más diversidad floral en regiones templadas, por eso muchas flores aparecen en primavera."
    ]
}

def generar_respuestas_simuladas(pregunta):
    """
    Devuelve un objeto con:
      - respuesta: la principal (string)
      - alternativas: lista de strings (otras variantes)
    La función intenta detectar palabras clave y devolver respuestas específicas,
    junto con respuestas genéricas si no hay coincidencias.
    """
    texto = pregunta.lower()
    # limpiar signos
    texto_limpio = re.sub(r"[^\wáéíóúñ ]", " ", texto)

    # buscar keywords en la pregunta
    encontrados = []
    for key in RESPONSES_KEYWORD.keys():
        # match palabra completa o plural simple
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, texto_limpio):
            encontrados.append(key)

    alternativas = []
    # si hay coincidencias, agrega sus respuestas
    if encontrados:
        for k in encontrados:
            # evita listas vacías
            opciones = RESPONSES_KEYWORD.get(k, [])
            if opciones:
                # tomar hasta 2 variaciones por keyword
                sample = random.sample(opciones, min(2, len(opciones)))
                alternativas.extend(sample)
    # si no encontró keywords específicas, añade varias genéricas
    if not alternativas:
        alternativas = random.sample(RESPONSES_GENERIC, min(3, len(RESPONSES_GENERIC)))
    else:
        # siempre añadir una o dos genéricas para completitud
        gen = random.sample(RESPONSES_GENERIC, min(2, len(RESPONSES_GENERIC)))
        alternativas.extend(gen)

    # deduplicar manteniendo orden
    seen = set()
    alternativas_final = []
    for a in alternativas:
        if a not in seen:
            alternativas_final.append(a)
            seen.add(a)

    # elegir la respuesta principal como la primera alternativa
    respuesta_principal = alternativas_final[0] if alternativas_final else "Lo siento, no tengo información sobre eso."

    return {"respuesta": respuesta_principal, "alternativas": alternativas_final}

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

# --- ENDPOINT IA (SIMULADA) ---
@app.route("/api/ia_flores", methods=["POST"])
def ia_flores():
    data = request.get_json() or {}
    pregunta = (data.get("pregunta") or "").strip()
    print("IA SIM: pregunta recibida:", pregunta)
    if not pregunta:
        return jsonify({"respuesta": "💬 Por favor escribe una pregunta sobre flores o temporadas.", "alternativas": []}), 400

    # Generar respuestas simuladas (principal + alternativas)
    contenido = generar_respuestas_simuladas(pregunta)

    # Devolvemos un JSON con 'respuesta' y 'alternativas'
    return jsonify(contenido), 200

# --- ELIMINAR FLOR ---
@app.route("/api/flores/<nombre>", methods=["DELETE"])
def eliminar_flor(nombre):
    if session.get("tipo") != "admin":
        return jsonify({"mensaje": "No autorizado"}), 403
    flores = cargar_datos(DB_FLORES)
    nuevas_flores = [f for f in flores if f["nombre"] != nombre]
    if len(nuevas_flores) == len(flores):
        return jsonify({"mensaje": "Flor no encontrada"}), 404
    guardar_datos(DB_FLORES, nuevas_flores)
    return jsonify({"mensaje": f'Flor \"{nombre}\" eliminada correctamente'}), 200

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    os.makedirs("database", exist_ok=True)
    if not os.path.exists(DB_USERS):
        guardar_datos(DB_USERS, [])
    if not os.path.exists(DB_FLORES):
        flores_demo = [
            {"nombre": "Rosa roja", "precio": 25, "estacion": "Primavera"},
            {"nombre": "Tulipán", "precio": 30, "estacion": "Primavera"},
            {"nombre": "Girasol", "precio": 20, "estacion": "Verano"},
            {"nombre": "Lirio", "precio": 28, "estacion": "Primavera"}
        ]
        guardar_datos(DB_FLORES, flores_demo)
    app.run(debug=True)
