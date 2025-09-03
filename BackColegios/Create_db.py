import json
from urllib.parse import parse_qs
import datetime
import pg8000.native
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict, fields
from connection_db import connection


#Funcion para registrarse en la aplicacion
def createDB_users():
    
    conn = connection()
    #
    # Para el funcionamiento de gen_random_uuid() se debe instalar la extension pgcrypto
    # CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    # SELECT * FROM pg_available_extensions WHERE name = 'pgcrypto';
    # 
    # Esto debe realizarse una unica vez por base de datos

    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS teachers (
            unique_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            status TEXT,
            lastedited TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMPTZ DEFAULT now(),
            rol TEXT,
            name TEXT,
            phone_number TEXT,
            document TEXT,
            email TEXT,
            password TEXT, 
            last_login TIMESTAMP WITH TIME ZONE,
            authorized BOOL NOT NULL DEFAULT FALSE,
            image BYTEA,
            colegio TEXT, 
            grados_imparte TEXT,
            seccion_escolar TEXT,
            planeacion TEXT,
            familiaridad_selva TEXT,
            nivel_certificacion TEXT,
            componentes_adquiridos TEXT [],
            grupo TEXT
        );
    """)
    finally:
        conn.close()