import os
import re
from contextlib import closing
from urllib.parse import urlparse

import psycopg2
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from flask import Flask, flash, jsonify, redirect, render_template, request

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

COLUMNAS_NOTICIA = "id, titulo, contenido, imagen_url, autor_id, fecha_publicacion, destacado"
MAX_ENTERO_BD = 2147483647
PATRON_USUARIO = r"[A-Za-z0-9_.-]{3,50}"

def conectar_bd():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre_completo", "").strip()
        usuario = request.form.get("nombre_usuario", "").strip()

        if not nombre or not usuario or len(nombre) > 120:
            flash("Verifica los datos ingresados.", "error")
            return redirect("/")

        if not re.fullmatch(PATRON_USUARIO, usuario):
            flash("El usuario debe tener entre 3 y 50 caracteres alfanumericos, puntos, guiones o guiones bajos.", "error")
            return redirect("/")

        try:
            with closing(conectar_bd()) as conn:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """INSERT INTO usuarios
                               (nombre_completo, nombre_usuario)
                               VALUES (%s, %s)""",
                            (nombre, usuario)
                        )
            flash("Usuario registrado correctamente.", "success")

        except UniqueViolation:
            flash("Ese nombre de usuario ya existe.", "error")

        except psycopg2.Error:
            app.logger.exception("Error al guardar el usuario")
            flash("No fue posible conectar con la base de datos.", "error")

        return redirect("/")

    try:
        with closing(conectar_bd()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre_completo, nombre_usuario FROM usuarios ORDER BY id"
                )
                usuarios = cur.fetchall()

        return render_template("index.html", usuarios=usuarios)

    except psycopg2.Error:
        app.logger.exception("Error consultando usuarios")
        return "No fue posible consultar la base de datos.", 503

def noticia_a_json(fila):
    return {
        "id": fila[0],
        "titulo": fila[1],
        "contenido": fila[2],
        "imagen_url": fila[3],
        "autor_id": fila[4],
        "fecha_publicacion": fila[5].isoformat(),
        "destacado": fila[6]
    }

def error_json(mensaje, estado):
    return jsonify(error=mensaje), estado

def usuario_a_json(fila):
    return {
        "id": fila[0],
        "nombre_completo": fila[1],
        "nombre_usuario": fila[2]
    }

def validar_usuario(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo debe ser un JSON valido."

    nombre = datos.get("nombre_completo")
    usuario = datos.get("nombre_usuario")

    if not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 120:
        return None, "El nombre completo es obligatorio y admite maximo 120 caracteres."

    if not isinstance(usuario, str) or not re.fullmatch(PATRON_USUARIO, usuario.strip()):
        return None, "El usuario debe tener entre 3 y 50 caracteres alfanumericos, puntos, guiones o guiones bajos."

    return (nombre.strip(), usuario.strip()), None

@app.route("/api/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        with closing(conectar_bd()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre_completo, nombre_usuario FROM usuarios ORDER BY id"
                )
                usuarios = cur.fetchall()

        return jsonify([usuario_a_json(fila) for fila in usuarios])

    except psycopg2.Error:
        app.logger.exception("Error consultando usuarios")
        return error_json("No fue posible consultar la base de datos.", 503)

@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    valores, error = validar_usuario(request.get_json(silent=True))
    if error:
        return error_json(error, 400)

    try:
        with closing(conectar_bd()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO usuarios
                           (nombre_completo, nombre_usuario)
                           VALUES (%s, %s)
                           RETURNING id, nombre_completo, nombre_usuario""",
                        valores
                    )
                    usuario = cur.fetchone()

        return jsonify(usuario_a_json(usuario)), 201

    except UniqueViolation:
        return error_json("Ese nombre de usuario ya existe.", 409)

    except ValueError:
        return error_json("El texto contiene caracteres no validos.", 400)

    except psycopg2.Error:
        app.logger.exception("Error al guardar el usuario")
        return error_json("No fue posible guardar el usuario.", 503)

def url_valida(url):
    try:
        partes = urlparse(url)
    except ValueError:
        return False
    return partes.scheme in ("http", "https") and bool(partes.netloc)

def validar_noticia(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo debe ser un JSON valido."

    titulo = datos.get("titulo")
    contenido = datos.get("contenido")
    imagen_url = datos.get("imagen_url")
    autor_id = datos.get("autor_id")

    if not isinstance(titulo, str) or not titulo.strip() or len(titulo.strip()) > 200:
        return None, "El titulo es obligatorio y admite maximo 200 caracteres."

    if not isinstance(contenido, str) or not contenido.strip():
        return None, "El contenido es obligatorio."

    if imagen_url == "":
        imagen_url = None

    if imagen_url is not None and (not isinstance(imagen_url, str) or not url_valida(imagen_url)):
        return None, "La imagen debe ser una URL http o https."

    if type(autor_id) is not int or not 1 <= autor_id <= MAX_ENTERO_BD:
        return None, "El autor_id debe ser un numero entero valido."

    return (titulo.strip(), contenido.strip(), imagen_url, autor_id), None

@app.route("/api/noticias", methods=["GET"])
def listar_noticias():
    try:
        with closing(conectar_bd()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {COLUMNAS_NOTICIA} FROM noticias ORDER BY fecha_publicacion DESC, id DESC"
                )
                noticias = cur.fetchall()

        return jsonify([noticia_a_json(fila) for fila in noticias])

    except psycopg2.Error:
        app.logger.exception("Error consultando noticias")
        return error_json("No fue posible consultar la base de datos.", 503)

@app.route("/api/noticias", methods=["POST"])
def crear_noticia():
    valores, error = validar_noticia(request.get_json(silent=True))
    if error:
        return error_json(error, 400)

    try:
        with closing(conectar_bd()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""INSERT INTO noticias
                            (titulo, contenido, imagen_url, autor_id)
                            VALUES (%s, %s, %s, %s)
                            RETURNING {COLUMNAS_NOTICIA}""",
                        valores
                    )
                    noticia = cur.fetchone()

        return jsonify(noticia_a_json(noticia)), 201

    except ForeignKeyViolation:
        return error_json("El autor indicado no existe.", 400)

    except ValueError:
        return error_json("El texto contiene caracteres no validos.", 400)

    except psycopg2.Error:
        app.logger.exception("Error al guardar la noticia")
        return error_json("No fue posible guardar la noticia.", 503)

@app.route("/api/noticias/<int:noticia_id>/destacado", methods=["PATCH"])
def cambiar_destacado(noticia_id):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not isinstance(datos.get("destacado"), bool):
        return error_json("El campo destacado debe ser true o false.", 400)

    try:
        with closing(conectar_bd()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""UPDATE noticias SET destacado = %s
                            WHERE id = %s
                            RETURNING {COLUMNAS_NOTICIA}""",
                        (datos["destacado"], noticia_id)
                    )
                    noticia = cur.fetchone()

        if noticia is None:
            return error_json("La noticia no existe.", 404)

        return jsonify(noticia_a_json(noticia))

    except psycopg2.Error:
        app.logger.exception("Error al actualizar la noticia")
        return error_json("No fue posible actualizar la noticia.", 503)
