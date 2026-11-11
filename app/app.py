import os
import re
from contextlib import closing

import psycopg2
from psycopg2.errors import UniqueViolation
from flask import Flask, flash, redirect, render_template, request

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

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

        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", usuario):
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
