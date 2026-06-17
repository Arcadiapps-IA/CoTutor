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
- co_tutor/moodle/cli.py: CLI interactivo para pedir URL/usuario/contraseña y guardar config localmente
- tests/test_moodle_client.py: pruebas unitarias básicas (mocked)

Instalación
1) Instala dependencias del repo (si usas el requirements añadido en la raíz):
   python -m pip install -r requirements.txt

2) Opcional: copia co_tutor/moodle/.env.example a co_tutor/moodle/.env y rellena
   las variables (NO subir .env al repositorio).

Configuración y autenticación
Hay dos modos de autenticación soportados:

1) Token de servicio (recomendado para integraciones servidor-servidor)
   - Crea o usa un token de servicio en Moodle con los permisos necesarios y
     colócalo en la variable de entorno MOODLE_TOKEN o en .env.
   - El cliente leerá MOODLE_URL y MOODLE_TOKEN automáticamente.

2) Usuario y contraseña (autenticación en nombre del usuario)
   - La aplicación puede pedir al usuario su URL de Moodle, usuario y
     contraseña y luego llamar a MoodleClient.authenticate_with_credentials(username, password, service="moodle_mobile_app")
   - Esto intenta obtener un token mediante /login/token.php para el service
     especificado (por defecto 'moodle_mobile_app'). El token resultante se usa
     para las llamadas posteriores y tendrá los mismos permisos que el usuario.
   - Nota: el servicio indicado (por ejemplo 'moodle_mobile_app') debe estar
     habilitado en la instancia de Moodle y permitir creación de tokens.

Uso básico
from co_tutor.moodle import MoodleClient, get_courses
client = MoodleClient()  # lee MOODLE_URL y MOODLE_TOKEN / .env
# O autenticar con credenciales de usuario:
# client = MoodleClient(base_url="https://moodle.example.org")
# client.authenticate_with_credentials(username, password)
courses = get_courses(client)

CLI interactivo
Puedes usar la utilidad de línea de comandos incluida para solicitar la URL,
usuario y contraseña de forma interactiva y guardar la configuración localmente:

Ejecutar directamente como módulo:

  python -m co_tutor.moodle.cli

Argumentos opcionales:
  --base-url URL     Moodle base URL
  --username USER    Usuario
  --service SERVICE  Service shortname (por defecto: moodle_mobile_app)
  --no-save-username No guardar el username en la configuración local

El comando solicitará la contraseña por prompt de forma segura y almacenará el
base_url y el token devuelto en co_tutor/moodle/.moodle_config.json (git-ignored).

Seguridad
- Nunca guardes credenciales o tokens en el repositorio.
- Para CI/producción utiliza GitHub Secrets (MOODLE_TOKEN, MOODLE_URL) o un
  sistema de gestión de secretos.

Limitaciones y futuras mejoras
- Manejo de paginación y grandes volúmenes de datos.
- Soporte para subir envíos (mod_assign_submit_for_marking o similar) y para
  sincronización de usuarios/inscripciones.
- Validación y modelos (pydantic) para respuestas de Moodle.
- Integración con pruebas de integración en un entorno acceso-restricted.
