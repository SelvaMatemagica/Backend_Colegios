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
from Create_db import createDB_users, createDB_cuestionario_primera_semana, createDB_cuestionario_semanal, createDB_cuestionario_mensual, createDB_cuestionario_1a1, createDB_jobs
from urllib.parse import parse_qs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import base64
import uuid
import boto3
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
        "image": None
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_editar(raw_body: dict) -> dict:
    print(raw_body)
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        "status": None,
        "lastedited": datetime.utcnow(),
        #"rol": None,
        "name": None,
        "phone_number": None,
        "document": None,
        "email": None,
        "password": None,
        #"last_login": None,
        #"authorized": None,
        "image": None,
        "colegio": None,
        "grados_imparte": None,
        "seccion_escolar": None,
        "planeacion": None,
        "familiaridad_selva": None,
        "nivel_certificacion": None,
        "componentes_adquiridos": None,
        "grupo": None
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_cuestionario_primera_semana(raw_body: dict) -> dict:
    print(raw_body)
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        #"id": None,
        "usuario_id": None,
        "usuario_nombre": None,
        "created_at": datetime.utcnow(),

        "p1_lograste_cumplir_objetivos": None,
        "p2_como_evaluas_avance": None,
        "p3_claro_contenido_trabajado": None,
        "p4_emocion_cierras_semana": None,
        "p5_materiales_utilizando_docente": None,
        "p6_materiales_alumnos": None,
        "p7_certificacion_nivel_1": None,
        "p8_certificacion_nivel_2": None,
        "p9_primera_sesion_1a1": None,
        "p10_has_recibido_acompanamiento": None,
        "p11_dudas_sugerencias": None
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_cuestionario_semanal(raw_body: dict) -> dict:
    print(raw_body)
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        #"id": None,
        "usuario_id": None,
        "usuario_nombre": None,
        "semana": None,
        "created_at": datetime.utcnow(),

        "p1_lograste_cumplir_objetivos": None,
        "p2_como_evaluas_avance": None,
        "p3_claro_contenido_trabajado": None,
        "p4_emocion_cierras_semana": None,
        
        "p5_has_recibido_acompanamiento": None,
        "p6_dudas_sugerencias": None
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_cuestionario_mensual(raw_body: dict) -> dict:
    print(raw_body)
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        #"id": None,
        "usuario_id": None,
        "usuario_nombre": None,
        "mes": None,
        "created_at": datetime.utcnow(),

        "p1_tema_avanzaste": None,
        "p2_aprendizaje_destacarias_alumnos": None,
        "p3_dificil_aplicar_metodologia": None,
        "p4_apoyo_util": None,
        "p5_seguro_aplicando_metodologia": None,
        "p6_grupo_participo_evaluacion": None,
        "p7_como_les_fue": None,
        "p8_actitud_peques_iniciar": None,
        "p9_reflexiona_progreso": None
    }

    for key, value in defaults.items():
        body.setdefault(key, value)

    return body


# Funcion que sirve para inicializar los valores
def preparar_body_para_sql_cuestionario_1a1(raw_body: dict) -> dict:
    print(raw_body)
    
    # copia el valor mandado de body
    body = raw_body.copy()
    # formatea la información para que no haya errores al insertar o modificar
    defaults = {
        #"id": None,
        "usuario_id": None,
        "usuario_nombre": None,
        "created_at": datetime.utcnow(),

        "p1_numero_sesion": None,
        "p2_mes_sesion": None,
        "p3_fecha_hora_sesion": None,
        "p4_estatus_sesion": None,
        "p5_nueva_fecha": None,
        "p6_primera_sesion": None,
        "p7_titulo_sesion": None,
        "p8_consultor": None,
        "p9_comentario_consultor": None,
        "p10_actitud_docente": None,
        "p11_valoracion_general_sesion": None
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


def serialize_data(data):
    def default(o):
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode("utf-8")
        return str(o)  # fallback seguro
    return json.dumps(data, default=default)


# Funcion para listar la informacion de la base de datos
def select_user(id_usuario):
    print("aaaaaaa")
    #createDB_users()
    conn = connection()
    print("antes de buscar en db")
    print("id_usuario:", id_usuario, type(id_usuario))
    try:
        filas = conn.run("""
        SELECT unique_id, status, lastedited AS "lastEdited", created_at, rol, name, phone_number, document,
        email, password, last_login, authorized, image FROM teachers WHERE unique_id = :unique_id;
        """, unique_id=id_usuario)  # **body desempaqueta el diccionario

        if not filas:
            return None

        print("despues de buscar en db")

        #resultados = []
        columnas = [f.name for f in fields(UserOut)]
        #for fila in filas:

        fila = list(filas[0])
        fila[0] = str(fila[0])
        fila_dict = dict(zip(columnas, fila))
        #resultados.append(UserOut(**fila_dict))

        resultado = UserOut(**fila_dict)

        return resultado
    finally:
        conn.close()



# Funcion para listar la informacion de la base de datos
def usuarios_de_colegio_especifico(colegio):
    print("aaaaaaa")
    #createDB_users()
    conn = connection()
    print("antes de buscar en db")
    print("colegio:", colegio, type(colegio))
    try:
        filas = conn.run("""
        SELECT unique_id, status, lastedited AS "lastEdited", created_at, rol, name, phone_number, document,
        email, password, last_login, authorized, image, colegio, grados_imparte, seccion_escolar, planeacion, familiaridad_selva,
        nivel_certificacion, componentes_adquiridos, grupo FROM teachers 
        WHERE colegio = :colegio
            AND rol = 'Docente'
            AND authorized = TRUE 
            AND status != 'eliminado';
        """, colegio=colegio)

        print("despues de buscar en db")
        print("filas:", filas)

        if not filas:
            return None

        

        resultados = []
        columnas = [f.name for f in fields(UserOut)]

        for fila in filas:
            fila[0] = str(fila[0])
            fila_dict = dict(zip(columnas, fila))
            resultados.append(UserOut(**fila_dict))

        print("resultados:", resultados)

        data = [asdict(r) for r in resultados]

        print("data:", data)

        return serialize_data(data)
    except Exception as e:
        print("Error al buscar usuarios por colegio:", repr(e))
        raise  # o convierte en return con error 500
        return False
    finally:
        conn.close()



# Funcion para insertar informacion en la base de datos
def insertar_user(body):

    createDB_users()
    
    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")
    
    body = preparar_body_para_sql_user(body)
    body["password"] = hashlib.sha256(body["password"].encode("utf-8")).hexdigest()
    body["rol"] = "Usuario Base"
    print("Claves recibidas:", list(body.keys()))
    try:
        row = conn.run("""
            INSERT INTO users ( status, lastedited, rol, name, phone_number, document, email, password, last_login, image )
            VALUES   ( :status, :lastedited, :rol, :name, :phone_number, :document, :email, :password, :last_login, image )
            RETURNING unique_id
            """,
            **body
        )
        if(row):
            print(row)
            if mandar_correo_authorized(body, row[0][0]):
                return True
            else:
                return False
        else:
            return False
    finally:
        conn.close()

    


def editar_user(body, id_usuario):

    #id_usuario = body.pop("id")               # lo sacamos y eliminamos de body

    conn = connection()
    if conn: print("Conexión exitosa")
    else: print("No se pudo conectar")
    
    body = preparar_body_para_sql_editar(body)
    print("1")

    if body["password"]:
        body["password"] = hashlib.sha256(body["password"].encode("utf-8")).hexdigest()
    else:
        body["password"] = None
    print("2")

    # Procesar foto (si viene en base64)
    if "image" in body and body["image"]:
        body["image"] = base64.b64decode(body["image"])
    else:
        body["image"] = None
    print("3")

    
    print("4")
        

    print("Claves recibidas:", list(body.keys()))
    #body["businessunit"] = body.pop("businessUnit", "")
    print("5")
    print("body antes de entrar a tabla")
    print(body)

    try:
        filas = conn.run("""
            UPDATE teachers
            SET status                  = :status,
                lastedited              = :lastedited,
                name                    = :name,
                phone_number            = :phone_number,
                document                = :document,
                email                   = COALESCE(:email, email),
                password                = COALESCE(:password, password),
                image                   = :image,
                colegio                 = :colegio,
                grados_imparte          = :grados_imparte,
                seccion_escolar         = :seccion_escolar,
                planeacion              = :planeacion,
                familiaridad_selva      = :familiaridad_selva,
                nivel_certificacion     = :nivel_certificacion,
                componentes_adquiridos  = :componentes_adquiridos,
                grupo                   = :grupo
            WHERE unique_id = :unique_id
            RETURNING unique_id, status, lastedited AS "lastEdited", created_at, rol, name, phone_number, document,
            email, password, last_login, authorized, image, colegio, grados_imparte, seccion_escolar, planeacion,
            familiaridad_selva, nivel_certificacion, componentes_adquiridos, grupo;
            """,
        unique_id=id_usuario,
        **body
        )
        print("6")

        resultados = []
        columnas = [f.name for f in fields(UserOut)]
        for fila in filas:
            fila[0] = str(fila[0])
            fila_dict = dict(zip(columnas, fila))
            resultados.append(UserOut(**fila_dict))

        data = [asdict(r) for r in resultados]

        print("data:", data)

        return serialize_data(data)


        #return body
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
            UPDATE users
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
            """UPDATE users SET authorized = TRUE WHERE unique_id = :unique_id;""",
            unique_id=unique_id
        )
    except Exception as e:
        print("Error al actualizar usuario:", repr(e))
        raise
    finally:
        conn.close()


def insertar_cuestionario_primera_semana(body):

    createDB_cuestionario_primera_semana()

    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    body = preparar_body_para_sql_cuestionario_primera_semana(body)
    print("Claves recibidas:", list(body.keys()))
    try:
        row = conn.run("""
            INSERT INTO cuestionario_primera_semana (usuario_id, usuario_nombre, created_at, p1_lograste_cumplir_objetivos, p2_como_evaluas_avance, p3_claro_contenido_trabajado, p4_emocion_cierras_semana, p5_materiales_utilizando_docente, p6_materiales_alumnos, p7_certificacion_nivel_1, p8_certificacion_nivel_2, p9_primera_sesion_1a1, p10_has_recibido_acompanamiento, p11_dudas_sugerencias)
            VALUES   (:usuario_id, :usuario_nombre, :created_at, :p1_lograste_cumplir_objetivos, :p2_como_evaluas_avance, :p3_claro_contenido_trabajado, :p4_emocion_cierras_semana, :p5_materiales_utilizando_docente, :p6_materiales_alumnos, :p7_certificacion_nivel_1, :p8_certificacion_nivel_2, :p9_primera_sesion_1a1, :p10_has_recibido_acompanamiento, :p11_dudas_sugerencias)
            RETURNING id
            """,
            **body
        )
        if(row):
            return True
        else:
            return False
    except Exception as e:
        print("Error al insertar cuestionario primera semana:", repr(e))
        raise
        return False
    finally:
        conn.close()


def insertar_cuestionario_semanal(body):

    createDB_cuestionario_semanal()

    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    body = preparar_body_para_sql_cuestionario_semanal(body)
    print("Claves recibidas:", list(body.keys()))
    try:
        row = conn.run("""
            INSERT INTO cuestionario_semanal (usuario_id, usuario_nombre, semana, created_at, p1_lograste_cumplir_objetivos, p2_como_evaluas_avance, p3_claro_contenido_trabajado, p4_emocion_cierras_semana, p5_has_recibido_acompanamiento, p6_dudas_sugerencias)
            VALUES   (:usuario_id, :usuario_nombre, :semana, :created_at, :p1_lograste_cumplir_objetivos, :p2_como_evaluas_avance, :p3_claro_contenido_trabajado, :p4_emocion_cierras_semana, :p5_has_recibido_acompanamiento, :p6_dudas_sugerencias)
            RETURNING id
            """,
            **body
        )
        if(row):
            return True
        else:
            return False
    except Exception as e:
        print("Error al insertar cuestionario semanal:", repr(e))
        raise
        return False
    finally:
        conn.close()


def insertar_cuestionario_mensual(body):

    createDB_cuestionario_mensual()

    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    body = preparar_body_para_sql_cuestionario_mensual(body)
    print("Claves recibidas:", list(body.keys()))
    try:
        row = conn.run("""
            INSERT INTO cuestionario_mensual (usuario_id, usuario_nombre, mes, created_at, p1_tema_avanzaste, p2_aprendizaje_destacarias_alumnos, p3_dificil_aplicar_metodologia, p4_apoyo_util, p5_seguro_aplicando_metodologia, p6_grupo_participo_evaluacion, p7_como_les_fue, p8_actitud_peques_iniciar, p9_reflexiona_progreso)
            VALUES   (:usuario_id, :usuario_nombre, :mes, :created_at, :p1_tema_avanzaste, :p2_aprendizaje_destacarias_alumnos, :p3_dificil_aplicar_metodologia, :p4_apoyo_util, :p5_seguro_aplicando_metodologia, :p6_grupo_participo_evaluacion, :p7_como_les_fue, :p8_actitud_peques_iniciar, :p9_reflexiona_progreso)
            RETURNING id
            """,
            **body
        )
        if(row):
            return True
        else:
            return False
    except Exception as e:
        print("Error al insertar cuestionario mensual:", repr(e))
        raise
        return False
    finally:
        conn.close()


def insertar_cuestionario_1a1(body):

    createDB_cuestionario_1a1()

    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    body = preparar_body_para_sql_cuestionario_1a1(body)
    print("Claves recibidas:", list(body.keys()))
    try:
        row = conn.run("""
            INSERT INTO cuestionario_1a1 (usuario_id, usuario_nombre, created_at, p1_numero_sesion, p2_mes_sesion, p3_fecha_hora_sesion, p4_estatus_sesion, p5_nueva_fecha, p6_primera_sesion, p7_titulo_sesion, p8_consultor, p9_comentario_consultor, p10_actitud_docente, p11_valoracion_general_sesion)
            VALUES   (:usuario_id, :usuario_nombre, :created_at, :p1_numero_sesion, :p2_mes_sesion, :p3_fecha_hora_sesion, :p4_estatus_sesion, :p5_nueva_fecha, :p6_primera_sesion, :p7_titulo_sesion, :p8_consultor, :p9_comentario_consultor, :p10_actitud_docente, :p11_valoracion_general_sesion)
            RETURNING id
            """,
            **body
        )
        if(row):
            return True
        else:
            return False
    except Exception as e:
        print("Error al insertar cuestionario primera sesion:", repr(e))
        raise
        return False
    finally:
        conn.close()


def enviar_mensajes(body):

    sqs = boto3.client("sqs")
    QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/376572378022/send-messages-queue"

    usuarios = body

    delay_time = 5

    print("usuarios")
    print(usuarios)

    # Crear job_id único
    job_id = str(uuid.uuid4())

    # Crear tabla jobs si no existe
    createDB_jobs()

    # Registrar el job en la DB como activo
    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    payload_job = {
        "job_id": job_id,
        "status": "active"
    }

    try:
        row = conn.run("""
            INSERT INTO jobs (job_id, status)
            VALUES   (:job_id, :status)
            RETURNING job_id
            """,
            **payload_job
        )
        #if(row):
            #return True
        #else:
            #return False
    except Exception as e:
        print("Error al insertar cuestionario primera sesion:", repr(e))
        raise
        return False
    finally:
        conn.close()

    
    # Enviar un mensaje a SQS por cada usuario
    for idx, user in enumerate(usuarios):
        payload = {
            "idx": idx,
            "usuario": user,
            "job_id": job_id
        }
        print("payload")
        print(payload)
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload),
            DelaySeconds=idx * delay_time   # escalonar cada usuario
        )

    return 1


def detener_envio():

    conn = connection()
    if conn: print("Conexión exitosa")
    else:    print("No se pudo conectar")

    try:
        rows = conn.run("""
            SELECT job_id, status, created_at
            FROM jobs
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
            """
        )
        print("si corrio select")

        if not rows:
            print("No hay jobs activos")
            return False
        else:
            print(rows)

        row = rows[0]

        print("row")
        print(row)

        # Actualizar estado a stopped
        conn.run("""
            UPDATE jobs SET status = 'stopped' WHERE job_id = :job_id
        """, **{"job_id": row[0]})

        return True

    except Exception as e:
        print(f"Error al detener job: {e}")
        raise
        return False
    finally:
        conn.close()
