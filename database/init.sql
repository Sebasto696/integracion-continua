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
    categoria VARCHAR(50) NOT NULL DEFAULT 'Institucional',
    autor_id INTEGER REFERENCES usuarios(id),
    fecha_publicacion TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    destacado BOOLEAN NOT NULL DEFAULT FALSE
);

ALTER TABLE noticias ADD COLUMN IF NOT EXISTS categoria VARCHAR(50) NOT NULL DEFAULT 'Institucional';
ALTER TABLE noticias ALTER COLUMN autor_id DROP NOT NULL;

INSERT INTO noticias (titulo, contenido, imagen_url, categoria)
SELECT v.titulo, v.contenido, v.imagen_url, v.categoria
FROM (VALUES
    (1, 'La institución fortalece sus programas de formación para el nuevo semestre', 'La institución anunció nuevas estrategias académicas y de acompañamiento para estudiantes, con el objetivo de fortalecer su proceso de formación y mejorar la experiencia educativa.', 'assets/images/noticias/noticia-1.jpg', 'Institucional'),
    (2, 'Estudiantes se destacan en jornada deportiva institucional', 'La comunidad estudiantil participó en una jornada deportiva que reunió a diferentes equipos en actividades de fútbol, voleibol y baloncesto, promoviendo el bienestar y el trabajo en equipo.', 'assets/images/noticias/noticia-2.jpg', 'Deportes'),
    (3, 'La cultura y el talento estudiantil se toman la institución', 'Durante la semana cultural, estudiantes y docentes participaron en presentaciones artísticas, muestras musicales y actividades que resaltaron la diversidad y el talento de la comunidad.', 'assets/images/noticias/noticia-3.jpg', 'Cultura'),
    (4, 'Nuevas herramientas tecnológicas fortalecen el aprendizaje', 'La institución incorporó nuevas herramientas digitales para apoyar los procesos académicos y facilitar el acceso de los estudiantes a recursos tecnológicos y educativos.', 'assets/images/noticias/noticia-4.jpg', 'Tecnología'),
    (5, 'La comunidad educativa participa en jornada de integración', 'Docentes, estudiantes y colaboradores participaron en una jornada de integración diseñada para fortalecer la convivencia, el sentido de pertenencia y el trabajo colaborativo.', 'assets/images/noticias/noticia-5.jpg', 'Institucional'),
    (6, 'Equipos institucionales avanzan en competencias deportivas', 'Los equipos deportivos de la institución continúan su preparación para las próximas competencias, con entrenamientos enfocados en fortalecer el rendimiento y el espíritu deportivo.', 'assets/images/noticias/noticia-6.jpg', 'Deportes'),
    (7, 'Estudiantes presentan proyectos en la muestra de innovación', 'La muestra de innovación reunió diferentes proyectos desarrollados por estudiantes, quienes presentaron propuestas creativas orientadas a resolver necesidades de su entorno.', 'assets/images/noticias/noticia-7.jpg', 'Cultura')
) AS v(orden, titulo, contenido, imagen_url, categoria)
WHERE NOT EXISTS (SELECT 1 FROM noticias n WHERE n.titulo = v.titulo)
ORDER BY v.orden DESC;
