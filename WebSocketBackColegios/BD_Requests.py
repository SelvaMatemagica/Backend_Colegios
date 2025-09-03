import pg8000.native
from conection_db import connection_users, createDB_users
import re
from datetime import datetime
import hashlib
import os
import base64

def safe_json_value(val):
    if isinstance(val, bytes):
        return base64.b64encode(val).decode('utf-8')
    if isinstance(val, datetime):
        return val.isoformat()
    return val

def normalizar_telefono(tel):
    return "+" + str(tel).strip().replace(" ", "").replace("-", "")

    

def get_users_from_db():
    createDB_users()
    conn = connection_users()
    if conn is None:
        return []
    else:
        print("Conexión exitosa")
        rows = conn.run(""" SELECT unique_id, name, rol, status, colegio, 
                                  email, phone_number, image, last_login, planeacion, familiaridad_selva, nivel_certificacion, componentes_adquiridos, grupo, document
                            FROM teachers WHERE authorized = TRUE AND status != 'eliminado'""")
        conn.close()

    return [
        {
            "id": str(r[0]), 
            "name": safe_json_value(r[1]), 
            "role": safe_json_value(r[2]),
            "isActive": safe_json_value(r[3]),
            "school": safe_json_value(r[4]),
            "email": safe_json_value(r[5]),
            "phone": safe_json_value(r[6]),
            "avatar": safe_json_value(r[7]),
            "lastLogin": safe_json_value(r[8]),
            "planning": safe_json_value(r[9]),
            "selvaFamiliarity": safe_json_value(r[10]),
            "certificationLevel": safe_json_value(r[11]),
            "acquiredComponents": safe_json_value(r[12]),
            "group": safe_json_value(r[13]),
            "document": safe_json_value(r[14])
        } 
        for r in rows
    ]

def get_a_user_from_db(user_id):
    createDB_users()
    print("id del usuario", user_id)
    conn = connection_users()
    if conn is None:
        return []
    else:
        print("Conexión exitosa")
        rows = conn.run(""" SELECT unique_id, status, lastedited AS "lastEdited", created_at, rol, name, phone_number, document,
        email, password, last_login, authorized, image, colegio, grados_imparte, seccion_escolar, planeacion, familiaridad_selva,
        nivel_certificacion, componentes_adquiridos, grupo FROM teachers WHERE unique_id = :user_id""", user_id=user_id)
        conn.close()

    return [
        {
            "id": str(r[0]), 
            "status": safe_json_value(r[1]),
            "lastEdited": safe_json_value(r[2]),
            "created_at": safe_json_value(r[3]),
            "rol": safe_json_value(r[4]),
            "name": safe_json_value(r[5]),
            "phone_number": safe_json_value(r[6]),
            "document": safe_json_value(r[7]),
            "email": safe_json_value(r[8]),
            "password": '',
            "last_login": safe_json_value(r[10]),
            "authorized": safe_json_value(r[11]),
            "image": safe_json_value(r[12]),
            "colegio": safe_json_value(r[13]),
            "grados_imparte": safe_json_value(r[14]),
            "seccion_escolar": safe_json_value(r[15]),
            "planeacion": safe_json_value(r[16]),
            "familiaridad_selva": safe_json_value(r[17]),
            "nivel_certificacion": safe_json_value(r[18]),
            "componentes_adquiridos": safe_json_value(r[19]),
            "grupo": safe_json_value(r[20])
        } 
        for r in rows
    ]

def delete_connection_from_db(conection_db):
    conn = connection_users()
    if conn is None:
        return []
    else:
        rows = conn.run("DELETE FROM conexiones_activas WHERE connection_id = :connection_id", connection_id=conection_db)
        #print("Eliminacion exitosa")
        #conn.run("DELETE FROM conexiones_activas WHERE last_seen < NOW() - INTERVAL '10 minutes';")
        #print("Eliminacion 2 exitosa")
        conn.close()

def get_active_connections():
    conn = connection_users()
    if conn is None:
        return []
    else:
        #conn.run("UPDATE conexiones_activas SET status = 'Inactivo' WHERE last_seen < NOW() - INTERVAL '10 minutes';")
        #print("Cambio de estatus realizado")
        rows = conn.run("SELECT connection_id, user_id, status, last_seen FROM conexiones_activas WHERE status = 'Activo';")
        conn.close()

    return [
        {
            "connection_id": str(r[0]),
            "user_id": r[1],
            "status": r[2],
            "last_seen": r[3]
        }
        for r in rows
    ]


def registerConnectionDB(connection_id, user_id):
    conn = connection_users()  # ← tu función para obtener conexión pg8000
    if conn is None:
        raise Exception("No se pudo establecer conexión con la base de datos")

    query = """
        INSERT INTO conexiones_activas (connection_id, user_id, status)
        VALUES (:connection_id, :user_id, 'Activo')
        ON CONFLICT (connection_id) DO UPDATE
        SET last_seen = NOW();
    """
    params = {
        "connection_id": connection_id,
        "user_id": user_id
    }
    conn.run(query, **params)
    conn.close()

def build_user_params(user):
    
    password = "Selva.2025"
    passhash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    params = {
        "rol": user["role"],
        "name": user["name"],
        "phone_number": normalizar_telefono(user["phone"]),
        "document": user["document"],
        "email": user["email"],
        "password": passhash,
        "authorized": True,
        "image": user["avatar"],
        "colegio": user["school"],
        "grados_imparte": '',
        "seccion_escolar": '',
        "planeacion": user["planning"],
        "familiaridad_selva": user["selvaFamiliarity"],
        "nivel_certificacion": user["certificationLevel"],
        "componentes_adquiridos": user["acquiredComponents"],
        "grupo": user["group"]
    }
    return params

def insertUsersDB(user):
    conn = connection_users()  # ← tu función para obtener conexión pg8000
    print(user)
    if conn is None:
        raise Exception("No se pudo establecer conexión con la base de datos") 
    
    query = """
        INSERT INTO teachers ( status, lastedited, created_at, rol, name, phone_number, document, email, password,
                               last_login, authorized, image, colegio, grados_imparte, seccion_escolar, planeacion,
                               familiaridad_selva, nivel_certificacion, componentes_adquiridos, grupo )
        VALUES ( 'activo', NOW(), NOW(), :rol, :name, :phone_number, :document, :email, 
                 :password,  NOW(), :authorized, :image, :colegio, :grados_imparte, :seccion_escolar, 
                 :planeacion, :familiaridad_selva, :nivel_certificacion, :componentes_adquiridos, :grupo )
        ON CONFLICT (phone_number) DO UPDATE
        SET lastedited = NOW(), status = 'activo', 
            authorized = EXCLUDED.authorized, phone_number = EXCLUDED.phone_number, document = EXCLUDED.document, 
            email = EXCLUDED.email, password = EXCLUDED.password, image = EXCLUDED.image, colegio = EXCLUDED.colegio, 
            grados_imparte = EXCLUDED.grados_imparte, seccion_escolar = EXCLUDED.seccion_escolar, 
            planeacion = EXCLUDED.planeacion, familiaridad_selva = EXCLUDED.familiaridad_selva, 
            nivel_certificacion = EXCLUDED.nivel_certificacion, componentes_adquiridos = EXCLUDED.componentes_adquiridos, 
            grupo = EXCLUDED.grupo;
    """
    for usuario in user:
        params = build_user_params(usuario)
        expected_keys = re.findall(r":(\w+)", query)
        missing = [key for key in expected_keys if key not in params]
        if missing:
            raise ValueError(f"Faltan parámetros requeridos: {missing}")
        print("llaves esperadas: ",expected_keys)
        print(f"[DB] Ejecutando registro de conexión: {params}")
        print("params =", params)
        print("keys =", list(params.keys()))

        conn.run(query, **params)


def updateUserData(user_id, role, status):
    conn = connection_users()
    if conn is None:
        raise Exception("No se pudo establecer conexión con la base de datos")

    query = """
        UPDATE teachers
        SET rol = COALESCE(NULLIF(TRIM(:role), ''), rol),
            status = COALESCE(NULLIF(TRIM(:status), ''), status)
        WHERE unique_id = :user_id;
    """

    params = {
        "role": role,
        "user_id": user_id,
        "status": status

    }

    conn.run(query, **params)
    




