import os
import re
from contextlib import closing
from urllib.parse import urlparse

import psycopg2
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import safe_join

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

CARPETA_FRONTEND = os.path.join(app.root_path, "static")
COLUMNAS_NOTICIA = "id, titulo, contenido, imagen_url, categoria, autor_id, fecha_publicacion, destacado"
CATEGORIAS_NOTICIA = ("Institucional", "Deportes", "Cultura", "Tecnología")
MAX_ENTERO_BD = 2147483647
PATRON_USUARIO = r"[A-Za-z0-9_.-]{3,50}"
PATRON_IMAGEN_LOCAL = r"assets/[A-Za-z0-9_-]+(?:[./][A-Za-z0-9_-]+)*"

def conectar_bd():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

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

def noticia_a_json(fila):
    return {
        "id": fila[0],
        "titulo": fila[1],
        "contenido": fila[2],
        "imagen_url": fila[3],
        "categoria": fila[4],
        "autor_id": fila[5],
        "fecha_publicacion": fila[6].isoformat(),
        "destacado": fila[7]
    }

def imagen_valida(imagen):
    if re.fullmatch(PATRON_IMAGEN_LOCAL, imagen):
        return True

    try:
        partes = urlparse(imagen)
    except ValueError:
        return False
    return partes.scheme in ("http", "https") and bool(partes.netloc)

def validar_noticia(datos):
    if not isinstance(datos, dict):
        return None, "El cuerpo debe ser un JSON valido."

    titulo = datos.get("titulo")
    contenido = datos.get("contenido")
    imagen_url = datos.get("imagen_url")
    categoria = datos.get("categoria")
    autor_id = datos.get("autor_id")

    if not isinstance(titulo, str) or not titulo.strip() or len(titulo.strip()) > 200:
        return None, "El titulo es obligatorio y admite maximo 200 caracteres."

    if not isinstance(contenido, str) or not contenido.strip():
        return None, "El contenido es obligatorio."

    if categoria not in CATEGORIAS_NOTICIA:
        return None, "Selecciona una categoria valida."

    if isinstance(imagen_url, str):
        imagen_url = imagen_url.strip()

    if imagen_url == "":
        imagen_url = None

    if imagen_url is not None and (not isinstance(imagen_url, str) or not imagen_valida(imagen_url)):
        return None, "La imagen debe ser una URL http o https, o una ruta dentro de assets/."

    if autor_id is not None and (type(autor_id) is not int or not 1 <= autor_id <= MAX_ENTERO_BD):
        return None, "El autor_id debe ser un numero entero valido."

    return (titulo.strip(), contenido.strip(), imagen_url, categoria, autor_id), None

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

@app.route("/api/noticias/<int:noticia_id>", methods=["GET"])
def obtener_noticia(noticia_id):
    try:
        with closing(conectar_bd()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {COLUMNAS_NOTICIA} FROM noticias WHERE id = %s",
                    (noticia_id,)
                )
                noticia = cur.fetchone()

        if noticia is None:
            return error_json("La noticia no existe.", 404)

        return jsonify(noticia_a_json(noticia))

    except psycopg2.Error:
        app.logger.exception("Error consultando la noticia")
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
                            (titulo, contenido, imagen_url, categoria, autor_id)
                            VALUES (%s, %s, %s, %s, %s)
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

@app.route("/api/noticias/<int:noticia_id>", methods=["PUT"])
def actualizar_noticia(noticia_id):
    valores, error = validar_noticia(request.get_json(silent=True))
    if error:
        return error_json(error, 400)

    titulo, contenido, imagen_url, categoria, _ = valores

    try:
        with closing(conectar_bd()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""UPDATE noticias
                            SET titulo = %s, contenido = %s, imagen_url = %s, categoria = %s
                            WHERE id = %s
                            RETURNING {COLUMNAS_NOTICIA}""",
                        (titulo, contenido, imagen_url, categoria, noticia_id)
                    )
                    noticia = cur.fetchone()

        if noticia is None:
            return error_json("La noticia no existe.", 404)

        return jsonify(noticia_a_json(noticia))

    except ValueError:
        return error_json("El texto contiene caracteres no validos.", 400)

    except psycopg2.Error:
        app.logger.exception("Error al actualizar la noticia")
        return error_json("No fue posible actualizar la noticia.", 503)

@app.route("/api/noticias/<int:noticia_id>", methods=["DELETE"])
def eliminar_noticia(noticia_id):
    try:
        with closing(conectar_bd()) as conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM noticias WHERE id = %s RETURNING id", (noticia_id,))
                    eliminada = cur.fetchone()

        if eliminada is None:
            return error_json("La noticia no existe.", 404)

        return "", 204

    except psycopg2.Error:
        app.logger.exception("Error al eliminar la noticia")
        return error_json("No fue posible eliminar la noticia.", 503)

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

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def servir_frontend(path):
    if path == "api" or path.startswith("api/"):
        return error_json("Ruta no encontrada.", 404)

    archivo = safe_join(CARPETA_FRONTEND, path) if path else None
    if archivo and os.path.isfile(archivo):
        return send_from_directory(CARPETA_FRONTEND, path)

    if "." in path.rsplit("/", 1)[-1]:
        return "Archivo no encontrado.", 404

    return send_from_directory(CARPETA_FRONTEND, "index.html")
