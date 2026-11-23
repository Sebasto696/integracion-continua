CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS noticias (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    imagen_url TEXT,
    autor_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_publicacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    destacado BOOLEAN NOT NULL DEFAULT FALSE
);
