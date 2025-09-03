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
        CREATE TABLE IF NOT EXISTS teachers-resources-progress (
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


def createDB_cuestionario_primera_semana():
    conn = connection()
    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS cuestionario_primera_semana (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT,
            usuario_nombre TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),

            p1_lograste_cumplir_objetivos TEXT,
            p2_como_evaluas_avance TEXT,
            p3_claro_contenido_trabajado TEXT,
            p4_emocion_cierras_semana TEXT,
            p5_materiales_utilizando_docente TEXT [],
            p6_materiales_alumnos TEXT [],
            p7_certificacion_nivel_1 TEXT,
            p8_certificacion_nivel_2 TEXT,
            p9_primera_sesion_1a1 TEXT,
            p10_has_recibido_acompanamiento TEXT,
            p11_dudas_sugerencias TEXT
        );
    """)
    finally:
        conn.close()


def createDB_cuestionario_semanal():
    conn = connection()
    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS cuestionario_semanal (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT,
            usuario_nombre TEXT,
            semana INT,
            created_at TIMESTAMPTZ DEFAULT now(),

            p1_lograste_cumplir_objetivos TEXT,
            p2_como_evaluas_avance TEXT,
            p3_claro_contenido_trabajado TEXT,
            p4_emocion_cierras_semana TEXT,
            
            p5_has_recibido_acompanamiento TEXT,
            p6_dudas_sugerencias TEXT
        );
    """)
    finally:
        conn.close()


def createDB_cuestionario_mensual():
    conn = connection()
    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS cuestionario_mensual (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT,
            usuario_nombre TEXT,
            mes INT,
            created_at TIMESTAMPTZ DEFAULT now(),

            p1_tema_avanzaste TEXT,
            p2_aprendizaje_destacarias_alumnos TEXT,
            p3_dificil_aplicar_metodologia TEXT [],
            p4_apoyo_util TEXT [],
            p5_seguro_aplicando_metodologia TEXT,
            p6_grupo_participo_evaluacion TEXT,
            p7_como_les_fue TEXT,
            p8_actitud_peques_iniciar TEXT,
            p9_reflexiona_progreso TEXT
        );
    """)
    finally:
        conn.close()


def createDB_cuestionario_1a1():
    conn = connection()
    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS cuestionario_1a1 (
            id SERIAL PRIMARY KEY,
            usuario_id TEXT,
            usuario_nombre TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),

            p1_numero_sesion TEXT,
            p2_mes_sesion TEXT,
            p3_fecha_hora_sesion TEXT,
            p4_estatus_sesion TEXT,
            p5_nueva_fecha TEXT,
            p6_primera_sesion TEXT,
            p7_titulo_sesion TEXT,
            p8_consultor TEXT,
            p9_comentario_consultor TEXT,
            p10_actitud_docente TEXT,
            p11_valoracion_general_sesion TEXT
        );
    """)
    finally:
        conn.close()



def createDB_jobs():
    conn = connection()
    try:
        conn.run("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id VARCHAR PRIMARY KEY,
            status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'stopped')),
            created_at TIMESTAMP DEFAULT now()
        );
    """)
    finally:
        conn.close()