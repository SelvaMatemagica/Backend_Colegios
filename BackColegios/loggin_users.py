import json
import datetime
import pg8000.native
import hashlib
import smtplib
import os
from typing import Optional, List
from datetime import datetime, date
from dataclasses import dataclass, field, asdict, fields
from connection_db import connection
from Create_db import createDB_users
from urllib.parse import parse_qs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dataclasses import asdict
import base64
html_path = Path(__file__).parent / "email.html"
html = html_path.read_text(encoding="utf-8")


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_user(raw_body: dict) -> dict:
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        "status": None,
        "lastedited": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "rol": None,
        "name": None,
        "phone_number": None,
        "document": None,
        "email": None,
        "password": None,
        "last_login": None,
        "authorized": None,
        "image": None,
        "colegio": None,
        "grados_imparte": None,
        "seccion_escolar": None,
        "planeacion": None,
        "familiaridad_selva": None,
        "componentes_adquiridos": [],
        "grupo": None,
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


def extraer_user_id(body_raw) -> str:
    import json

    # Decodificamos si viene como str
    if isinstance(body_raw, str):
        try:
            body = json.loads(body_raw)
        except Exception:
            raise ValueError("Body es string pero no es JSON válido.")
    elif isinstance(body_raw, dict):
        body = body_raw
    else:
        raise TypeError("Body debe ser dict o JSON string.")

    # Extraemos el valor de unique_id
    raw = body.get("unique_id")
    print("DEBUG — unique_id:", raw)

    if raw is None:
        raise ValueError("Campo 'unique_id' no presente en el body.")

    # Lista de lista: [[UUID]]
    if isinstance(raw, list):
        if raw and isinstance(raw[0], list) and raw[0]:
            return str(raw[0][0])
        elif raw and isinstance(raw[0], (str, UUID)):
            return str(raw[0])
    
    raise ValueError("Formato inesperado de unique_id.")



# Crear clase para obtener columnas a buscar del usuario
@dataclass
class UserIn():
    unique_id: Optional[str] = None
    status: Optional[str] = None
    lastEdited: Optional[datetime] = None
    created_at: Optional[datetime] = None
    rol: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    document: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    last_login: Optional[datetime] = None
    authorized: Optional[bool] = None
    image: Optional[str] = None
    colegio: Optional[str] = None
    grados_imparte: Optional[str] = None
    seccion_escolar: Optional[str] = None
    planeacion: Optional[str] = None
    familiaridad_selva: Optional[str] = None
    componentes_adquiridos: Optional[str] = None
    grupo: Optional[str] = None

class UserOut(UserIn):
    unique_id: str


# Funcion para confirmar existencia en la base de datos
def log_in_user(email):
    conn = connection()
    print("Correo recibido:", email)
    try:
        filas = conn.run(""" SELECT unique_id FROM teachers WHERE email = :email AND authorized = TRUE""", email = email )
        print("Filas:", filas)
        if(filas):
            id = filas[0][0]
            print("id:", id)
            print("longitud", len(filas))
            return len(filas)
        else:
            return 0
        
    finally:
        conn.close()


def serialize_data(data):
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode("utf-8")
        return str(o)  # fallback seguro
    return json.dumps(data, default=default)


# Funcion para listar la informacion de la base de datos
def select_user(body):
    createDB_users()
    print(body)
    body["password"] = hashlib.sha256(body["password"].encode("utf-8")).hexdigest()
    print(body)
    conn = connection()
    try:
        filas = conn.run("""
        SELECT unique_id, status, lastedited AS "lastEdited", created_at, rol, name, phone_number, document,
        email, last_login, authorized, image, colegio, grados_imparte, seccion_escolar, planeacion, familiaridad_selva,
        nivel_certificacion, componentes_adquiridos, grupo FROM teachers WHERE email = :email AND password = :password AND authorized = TRUE;
        """, **body)  # **body desempaqueta el diccionario

        resultados = []
        columnas = [f.name for f in fields(UserOut)]
        for fila in filas:
            fila[0] = str(fila[0])
            fila_dict = dict(zip(columnas, fila))
            resultados.append(UserOut(**fila_dict))

        data = [asdict(r) for r in resultados]

        print("data:", data)

        return serialize_data(data)
        #return data
    finally:
        conn.close()




def mandar_correo_authorized(body, unique_id):

    remitente = os.environ.get("EMAIL")
    host = os.environ.get("HOST")
    password = os.environ.get("PASSWORD")
    destinatario = body.get("email")
    asunto = "Autorización de usuario"

    user_id = unique_id
    print("user_id parte de envio del correo:", user_id)
    url_personalizada = f"https://main.d2hg3pwdwpmma4.amplifyapp.com/auth_confirmar.html?id={user_id}"

    if not all([remitente, host, password, destinatario]):
        raise ValueError("Faltan datos obligatorios para enviar el correo")

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autenticación</title>
    <style>
        body {
        margin: 0;
        padding: 0;
        background-color: #193310;
        font-family: 'Segoe UI', sans-serif;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        }

        .card {
        max-width: 600px;
        padding: 40px 30px;
        background-color: #174D1A;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
        text-align: center;
        }

        h1 {
        margin-bottom: 20px;
        font-size: 28px;
        color: #ffffff;
        }

        p {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 30px;
        color: #ffffff;
        }

        .auth-button {
        background-color: #4a6cf7;
        color: #ffffff;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        }

        .auth-button:hover {
        background-color: #375bd2;
        }
    </style>
    </head>

    <body>
    <div class="card">
        <h1>Autentica Tu Cuenta Ahora.</h1>
        <p>Haz clic para autenticarte y asegurar tu acceso. Con solo un clic podrás validar tu cuenta y proteger tu sesión de forma segura. Nos importa tu privacidad y tu comodidad, así que hemos diseñado el proceso para que sea ágil, confiable y sin complicaciones. Al autenticarte, garantizamos una experiencia personalizada y protegida en todo momento.</p>
        
        <a href="{{enlace_personalizado}}" id="auth_link" class="auth-button">Redireccionar</a>
    </div>
    </body>

    </html>
    """

    html = html_template.replace("{{enlace_personalizado}}", url_personalizada)
    print("html:", html)
    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.attach(MIMEText(html, "html"))
    print("msg:", msg)
    try:
        with smtplib.SMTP(host, 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.sendmail(remitente, destinatario, msg.as_string())
        return True
    except Exception as e:
        print("Error al enviar el correo:", repr(e))
        return False


def mandar_correo_recovery(body):

    data = log_in_user(body.get("email"))
    print("data:", data)
    if data == 0:
        return 2
    remitente = os.environ.get("EMAIL")
    host = os.environ.get("HOST")
    password = os.environ.get("PASSWORD")
    destinatario = body.get("email")
    asunto = "Autorización de usuario"

    url_personalizada = f"https://main.d2hg3pwdwpmma4.amplifyapp.com/reset_password.html?email={destinatario}"

    if not all([remitente, host, password, destinatario]):
        raise ValueError("Faltan datos obligatorios para enviar el correo")

    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autenticación</title>
    <style>
        body {
        margin: 0;
        padding: 0;
        background-color: #101933;
        font-family: 'Segoe UI', sans-serif;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        }

        .card {
        max-width: 600px;
        padding: 40px 30px;
        background-color: #174D1A;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
        text-align: center;
        }

        h1 {
        margin-bottom: 20px;
        font-size: 28px;
        color: #ffffff;
        }

        p {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 30px;
        color: #ffffff;
        }

        .auth-button {
        background-color: #4a6cf7;
        color: #fff;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        }

        .auth-button:hover {
        background-color: #375bd2;
        }
    </style>
    </head>

    <body>
    <div class="card">
        <h1>Actualiza tu contraseña.</h1>
        <p>Haz clic para redireccionarte para que puedas llenar el formulario para que actualices tu contraseña correctamente .</p>
        
        <a href="{{enlace_personalizado}}" id="auth_link" class="auth-button">Redireccionar</a>
    </div>
    </body>

    </html>
    """

    html = html_template.replace("{{enlace_personalizado}}", url_personalizada)

    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.attach(MIMEText(html, "html"))
    
    try:
        with smtplib.SMTP(host, 587) as server:
            server.starttls()
            server.login(remitente, password)
            server.sendmail(remitente, destinatario, msg.as_string())
        return 1
    except Exception as e:
        print("Error al enviar el correo:", repr(e))
        return 0



# Funcion para insertar informacion en la base de datos
def insertar_user(body):
    createDB_users()
    
    conn = connection()
    if conn:
        print("Conexión exitosa")
    else:
        print("No se pudo conectar")
        return 0  # Evita seguir si no hay conexión

    try: 
        long = log_in_user(body["email"])
        print("longitud:", long)
        if long > 0:
            return 2

        body = preparar_body_para_sql_user(body)
        body["password"] = hashlib.sha256(body["password"].encode("utf-8")).hexdigest()
        body["rol"] = body["tipoUsuario"]
        body["status"] = "activo"
        print("Claves recibidas:", list(body.keys()))

        row = conn.run("""
            INSERT INTO teachers (
                status, lastedited, rol, name, phone_number, document,
                email, password, last_login, image, colegio
            )
            VALUES (
                :status, :lastedited, :rol, :name, :phone_number, :document,
                :email, :password, :last_login, :image, :colegio
            )
            RETURNING unique_id
            """,
            **body
        )

        print("Resultado de INSERT:", row)

        if row and row[0][0]:
            envio = mandar_correo_authorized(body, row[0][0])
            print("Correo enviado:", envio)
            if envio:
                return 1
            else:
                return 0
        else:
            print("No se insertó ningún registro.")
            return 0

    except Exception as e:
        print("Error atrapado en insertar_user:", repr(e))
        return 0

    finally:
        conn.close()


    


def editar_user(id_usuario, body):

    id_usuario = body.pop("id")               # lo sacamos y eliminamos de body

    conn = connection()
    if conn: print("Conexión exitosa")
    else: print("No se pudo conectar")
    
    body = preparar_body_para_sql_user(body)
    print("Claves recibidas:", list(body.keys()))
    #body["businessunit"] = body.pop("businessUnit", "")

    try:
        conn.run("""
            UPDATE teachers
            SET status        = COALESCE(:status, status),
                lastedited    = COALESCE(:lastedited, lastedited),
                rol           = COALESCE(:rol, rol),
                name          = COALESCE(:name, name),
                phone_number  = COALESCE(:phone_number, phone_number),
                document      = COALESCE(:document, document),
                email         = COALESCE(:email, email),
                password      = COALESCE(:password, password),
                last_login    = COALESCE(:last_login, last_login),
                image         = COALESCE(:image, image)
            WHERE unique_id = :unique_id;
            """,
        unique_id=id_usuario,
        **body
        )
    except Exception as e:
        print("Error al actualizar usuario:", repr(e))
        raise  # o convierte en return con error 500
    finally:
        conn.close()


def Change_password(body):

    email = body.pop("email") 
    conn = connection()
    if conn: print("Conexión exitosa")
    else: print("No se pudo conectar")

    body["password"] = hashlib.sha256(body["password"].encode("utf-8")).hexdigest()
    print("Claves recibidas:", list(body.keys()))
    try:
        conn.run("""
            UPDATE teachers
            SET 
                lastedited    = NOW(),
                password      = COALESCE(:password, password)
            WHERE email = :email;
            """,
        email=email,
        **body
        )
    except Exception as e:
        print("Error al actualizar usuario:", repr(e))
        raise  # o convierte en return con error 500
        return False
    finally:
        conn.close()
        return True


def autorizar_user(unique_id: str):

    conn = connection()
    try:
        conn.run(
            """UPDATE teachers SET authorized = TRUE WHERE unique_id = :unique_id;""",
            unique_id=unique_id
        )
    except Exception as e:
        print("Error al actualizar usuario:", repr(e))
        raise
    finally:
        conn.close()

