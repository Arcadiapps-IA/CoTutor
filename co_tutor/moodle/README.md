# Moodle integration README

Este módulo proporciona un cliente ligero para acceder a la API REST de Moodle
desde CoTutor. Está pensado para uso inicial (listar cursos, obtener usuarios de
un curso, listar tareas y obtener calificaciones). No sube envíos en esta
versión.

Archivos añadidos
- co_tutor/moodle/client.py: MoodleClient (llamadas REST, obtención de token mediante credenciales, manejo básico de reintentos)
- co_tutor/moodle/services.py: funciones utilitarias get_courses, get_course_users, get_assignments, get_grades
- co_tutor/moodle/config_example.yml: ejemplo de configuración YAML
- co_tutor/moodle/.env.example: ejemplo de archivo .env
- co_tutor/moodle/README.md: documentación de uso
- co_tutor/moodle/.moodle_config.json: (NO committed) ejemplo de fichero de configuración local (se crea al conectar)
- co_tutor/moodle/api.py: Flask blueprint que expone endpoints para conectar/consultar/desconectar
- co_tutor/moodle/config_store.py: helpers para persistir la configuración localmente
- tests/test_moodle_client.py: pruebas unitarias básicas (mocked)

Instalación
1) Instala dependencias del repo (si usas el requirements añadido en la raíz):
   python -m pip install -r requirements.txt

2) Opcional: copia co_tutor/moodle/.env.example a co_tutor/moodle/.env y rellena
   las variables (NO subir .env al repositorio).

Endpoints HTTP
Este paquete incluye una Flask Blueprint que expone tres endpoints bajo /moodle:

- POST /moodle/connect
  Body JSON: {"base_url": "https://moodle.example.org", "username": "user", "password": "pass", "service": "moodle_mobile_app"}
  Acción: obtiene un token con las credenciales y guarda (en local) base_url, username y token. NOTA: guarda el token en un fichero local que está gitignored.

- GET /moodle/config
  Devuelve la configuración guardada (ocultando parcialmente el token).

- POST /moodle/disconnect
  Elimina la configuración local guardada.

Integración en tu aplicación web (Flask)
Registra la blueprint en tu Flask app:

from flask import Flask
from co_tutor.moodle.api import bp as moodle_bp

app = Flask(__name__)
app.register_blueprint(moodle_bp)

Consideraciones de seguridad
- Estos endpoints manejan credenciales; protege el acceso a ellos mediante autenticación/autorization en tu app y utiliza HTTPS.
- El token se almacena localmente en co_tutor/moodle/.moodle_config.json y el fichero está incluido en .gitignore para evitar subirlo al repositorio.
- Para despliegues/CI, prefiere GitHub Secrets y tokens de servicio en lugar de almacenar credenciales de usuarios.

Siguientes pasos
- Integrar protección (auth) para los endpoints en la app principal.
- Añadir tests para la blueprint (usar pytest + flask test client y mocking de MoodleClient).
