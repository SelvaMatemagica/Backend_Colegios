import json
from urllib.parse import parse_qs, unquote
import datetime
import pg8000.native
import uuid
from typing import Optional, List
from datetime import datetime, date
from dataclasses import dataclass, field, asdict, fields
from connection_db import connection
from Create_db import createDB_users
from loggin_users import insertar_user, editar_user, autorizar_user, Change_password, select_user, insertar_cuestionario_primera_semana, insertar_cuestionario_semanal, insertar_cuestionario_mensual, insertar_cuestionario_1a1, enviar_mensajes, detener_envio, usuarios_de_colegio_especifico

import boto3

sqs = boto3.client("sqs")
QUEUE_URL = "https://sqs.us-east-2.amazonaws.com/376572378022/send-messages-queue"

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
            data = log_in_user(body)
            print(data)
            if data:
                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    },
                    "body": json.dumps(str(data))
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
            if insertar_user(body):
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
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
            if mandar_correo_recovery(body):
                return {
                    "statusCode": 201,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
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

    # Endpoint para obtener a un usuario
    elif ruta == "/users/{user_id}" and method == "GET":
        print("entro")
        try:
            id_usuario = event["pathParameters"]["user_id"]

            if id_usuario:
                print("id usuario")
                print(id_usuario)
                data = select_user(id_usuario)
                print(data)
                if data:
                    response_body = asdict(data)   # solo un objeto
                    status = 201
                    print("ya casi")
                    print(response_body)
                else:
                    response_body = 0
                    status = 404
            else:
                response_body = {"error": "Missing user id"}
                status = 400

            print("ya")
            return {
                "statusCode": status,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
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
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
                },
                "body": json.dumps({"error": str(e)})
            }

        

    # Endpoint para modificar a un usuario
    elif ruta == "/users/{user_id}" and method == "PUT":
        try:
            if body:
                body = json.loads(event.get("body"))
                id_usuario = event["pathParameters"]["user_id"]
                data = editar_user(body, id_usuario)
                if data:
                    response_body = {"message": "datos actualizados correctamente", "data": data}
                    status = 201
                else:
                    response_body = {"error": "Usuario no encontrado", "data": None}
                    status = 404
            else:
                response_body = {"error": "Missing body", "data": None}
                status = 400

            print("response body: ", response_body)
            print("response body2: ", json.dumps(response_body, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)))
            return {
                "statusCode": status,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "PUT,OPTIONS"
                },
                "body": json.dumps(response_body, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
            }
        except Exception as e:
            print("Error:", str(e))
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "PUT,OPTIONS"
                },
                "body": json.dumps({"error": str(e)})
            }


    # Endpoint para obtener usuarios de un colegio
    elif ruta == "/users/colegio/{colegio}" and method == "GET":
        try:
            colegio = event["pathParameters"]["colegio"]
            colegio = unquote(colegio)  # 🔹 Decodifica %20 → espacio
            if colegio:
                data = usuarios_de_colegio_especifico(colegio)
                if data:
                    response_body = {"message": "Usuarios de colegio", "data": data}
                    status = 200
                else:
                    response_body = {"error": "Usuarios no encontrados", "data": None}
                    status = 404
            else:
                response_body = {"error": "Faltó colegio", "data": None}
                status = 400

            print("response body: ", response_body)
            print("response body2: ", json.dumps(response_body, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)))
            return {
                "statusCode": status,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
                },
                "body": json.dumps(response_body, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
            }
        except Exception as e:
            print("Error:", str(e))
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "GET,OPTIONS"
                },
                "body": json.dumps({"error": str(e)})
            }


    # Endpoint para registrar resultados de cuestionario
    elif ruta == "/cuestionario/primera_semana" and method == "POST":
        try:
            if body:
                data = insertar_cuestionario_primera_semana(body)
                if data:
                    return {
                        "statusCode": 201,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization",
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


    # Endpoint para registrar resultados de cuestionario
    elif ruta == "/cuestionario/semanal" and method == "POST":
        try:
            if body:
                data = insertar_cuestionario_semanal(body)
                if data:
                    return {
                        "statusCode": 201,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization",
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


    # Endpoint para registrar resultados de cuestionario
    elif ruta == "/cuestionario/mensual" and method == "POST":
        try:
            if body:
                data = insertar_cuestionario_mensual(body)
                if data:
                    return {
                        "statusCode": 201,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization",
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


    # Endpoint para registrar resultados de cuestionario
    elif ruta == "/cuestionario/1a1" and method == "POST":
        try:
            if body:
                data = insertar_cuestionario_1a1(body)
                if data:
                    return {
                        "statusCode": 201,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Methods": "POST, OPTIONS",
                            "Access-Control-Allow-Headers": "Content-Type, Authorization",
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



    # 🚀 Nuevo endpoint: enviar mensajes
    elif ruta == "/enviar-mensajes" and method == "POST":
        print("body")
        print(body)
        usuarios = body

        #print("usuarios")
        #print(usuarios)

        data = enviar_mensajes(body)

        if data:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": json.dumps({
                    "status": "Mensajes encolados",
                    "total": len(usuarios)
                })
            }

        else:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": json.dumps({
                    "status": "Error al enviar mensajes",
                    "total": 0
                })
            }


    # 🚀 Nuevo endpoint: enviar mensajes
    elif ruta == "/detener-envio" and method == "POST":
        #print("body")
        #print(body)
        #usuarios = body

        #print("usuarios")
        #print(usuarios)

        #data = enviar_mensajes(body)
        data = detener_envio()

        if data:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": json.dumps({
                    "status": "Último envío de mensajes detenído"
                })
            }

        else:
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                },
                "body": json.dumps({
                    "status": "Error al detener el envío de mensajes"
                })
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
