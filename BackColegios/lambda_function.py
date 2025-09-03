import json
from urllib.parse import parse_qs
import datetime
import pg8000.native
import uuid
import boto3
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict, fields
from connection_db import connection
from Create_db import createDB_users
from loggin_users import log_in_user, insertar_user, editar_user, autorizar_user, mandar_correo_recovery, Change_password, select_user

# Funcion principal para activar la api
def lambda_handler(event, context):
    # Obtiene los datos de quien lo llama
    path = event.get("path", "")
    method = event.get("httpMethod", "")
    raw_body = event.get("body")

    # Verifica si obtuvo o no obtuvo informacion
    if raw_body is not None:
        body = json.loads(raw_body.strip())
    else:
        body = {}
    
    # obtiene la ruta desde el ultimo / que se encuentra
    ruta = event.get("resource")  # "/editar_usuario/{id}"


    # Endpoint para loggear a un usuario
    if ruta == "/loggin" and method == "POST":
        if body:
            body = json.loads(event.get("body"))
            data = select_user(body)
            print("data serialize")
            print(data)
            if data:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps(data, default=lambda o: o.isoformat() if isinstance(o, datetime) else o)
                }
            else:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps(0)
                }
    


    # Endpoint para registrar nuevos usuarios a la plataforma
    elif ruta == "/loggin/register" and method == "POST":
        if body:
            body = json.loads(event.get("body"))
            print("imprimiendo body antes de")
            resultados = insertar_user(body)
            print("imprimiendo resultados", resultados)
            if resultados: 
                print("imprimiendo resultados", resultados)
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps(resultados)
                }
            else:
                print("imprimiendo resultados", resultados)
                return {
                    "statusCode": 404,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps("No existe")
                }
           

    elif ruta == "/Auth/{usuario_id}" and method == "GET":
        id_usuario = event["pathParameters"]["usuario_id"]
        try:
            autorizar_user(id_usuario)
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS, PUT",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": str(e)})
            }

        return {
            "statusCode": 202,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, PUT",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps("Datos editados correctamente")
        }


    # Endpoint para registrar nuevos usuarios a la plataforma
    elif ruta == "/Reset_Password" and method == "POST":
        if body:
            body = json.loads(event.get("body"))
            resultados = mandar_correo_recovery(body)
            print(resultados)
            if resultados:
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps(resultados)
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps("Datos no insertados")
                }


    elif ruta == "/Reset_Password/Change_Password" and method == "POST":
        if body:
            body = json.loads(event.get("body"))
            print(body)
            if Change_password(body):
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Headers": "Content-Type,Authorization",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",

                    },
                    "body": json.dumps("Datos insertados correctamente")
                }
            else:
                return {
                    "statusCode": 404,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps("Datos no insertados")
                }

    # Endpoint para loggear a un usuario
    elif ruta == "/GetUser" and method == "POST":
        try:
            if body:
                body = json.loads(event.get("body"))
                data = select_user(body)
                print(data)
                if data:
                    response_body = [asdict(c) for c in data]
                    status = 201
                else:
                    response_body = 0
                    status = 404
            else:
                response_body = {"error": "Missing body"}
                status = 400

            return {
                "statusCode": status,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps(response_body, default=lambda o: o.isoformat() if isinstance(o, datetime) else o)
            }

        except Exception as e:
            print("Error:", str(e))
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps({"error": str(e)})
            }



    # Retorna si no se llama a ningun endpoint
    else:
        return {
            "statusCode": 404,
             "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },   
            "body": "Endpoint no reconocido"
        }
