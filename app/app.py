import os
import re
from contextlib import closing

import psycopg2
from psycopg2.errors import UniqueViolation
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ["FLASK_SECRET_KEY"]


def conectar_bd():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


@app.route("/api/usuarios", methods=["GET", "POST"])
def api_usuarios():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        nombre = str(data.get("nombre_completo", "")).strip()
        usuario = str(data.get("nombre_usuario", "")).strip()

        if not nombre or not usuario or len(nombre) > 120:
            return jsonify({"error": "Verifica los datos ingresados."}), 400

        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", usuario):
            return jsonify({
                "error": "El usuario debe tener entre 3 y 50 caracteres alfanumericos, puntos, guiones o guiones bajos."
            }), 400

        try:
            with closing(conectar_bd()) as conn:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO usuarios
                               (nombre_completo, nombre_usuario)
                               VALUES (%s, %s)
                               RETURNING id, nombre_completo, nombre_usuario""",
                            (nombre, usuario),
                        )
                        nuevo = cur.fetchone()

            return jsonify({
                "id": nuevo[0],
                "nombre_completo": nuevo[1],
                "nombre_usuario": nuevo[2],
                "mensaje": "Usuario registrado correctamente.",
            }), 201

        except UniqueViolation:
            return jsonify({"error": "Ese nombre de usuario ya existe."}), 409

        except psycopg2.Error:
            app.logger.exception("Error al guardar el usuario")
            return jsonify({"error": "No fue posible conectar con la base de datos."}), 503

    try:
        with closing(conectar_bd()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre_completo, nombre_usuario FROM usuarios ORDER BY id"
                )
                filas = cur.fetchall()

        usuarios = [
            {"id": fila[0], "nombre_completo": fila[1], "nombre_usuario": fila[2]}
            for fila in filas
        ]
        return jsonify(usuarios), 200

    except psycopg2.Error:
        app.logger.exception("Error consultando usuarios")
        return jsonify({"error": "No fue posible consultar la base de datos."}), 503


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_angular(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")