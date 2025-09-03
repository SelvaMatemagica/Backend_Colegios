import boto3
import json
import logging
from botocore.config import Config
from BD_Requests import (
    get_users_from_db,
    registerConnectionDB,
    get_active_connections,
    delete_connection_from_db,
    updateUserData,
    insertUsersDB,
    get_a_user_from_db
)

# Configuración global del cliente WebSocket
ENDPOINT_URL = "https://q1muavkbp5.execute-api.us-east-2.amazonaws.com/WebSocketBackColegios" 
CONFIG = Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 2})
client = boto3.client('apigatewaymanagementapi', endpoint_url=ENDPOINT_URL, config=CONFIG)



def broadcast_to_all(payload):
    """Envía el payload a todas las conexiones activas."""
    connections = get_active_connections()
    for conn in connections:
        try:
            client.post_to_connection(
                ConnectionId=conn['connection_id'],
                Data=json.dumps(payload).encode("utf-8")
            )
        except client.exceptions.GoneException:
            print(f"❌ Cliente desconectado: {conn['connection_id']}")




def build_response(status_code, message):
    return {
        "statusCode": status_code,
        "body": json.dumps({ "message": message }),
        "headers": { "Content-Type": "application/json" }
    }



def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    route_key = event['requestContext']['routeKey']
    print(f"🔌 Cliente conectado: {connection_id}, Ruta: {route_key}")



    if route_key == '$connect':
        return build_response(200, "Connected")



    if route_key == '$disconnect':
        delete_connection_from_db(connection_id)
        return build_response(200, "Disconnected")


    try:
        body = json.loads(event.get('body', '{}'))
        data = body.get('data', {})
        user_id = data.get('user_id')
        if user_id:
            registerConnectionDB(connection_id, user_id)



        if route_key == 'getusers':
            user_id = data.get('user_id')



        if route_key == 'get_a_user': 
            if not user_id :
                return build_response(400, "Missing user_id")
            print(f"🛠️ Obteniendo datos del usuario con el id: {user_id}") 
            usuario = get_a_user_from_db(user_id)
            print(f"🛠️ Usuario obtenido: {usuario}")
            payload = {"type": "get_a_user_Response", "data": usuario}
            broadcast_to_all(payload)
            return build_response(200, "User taken and broadcasted")



        if route_key == 'updateRole':
            if not user_id :
                return build_response(400, "Missing user_id")
            role = data.get('role')
            if role:
                print(f"🛠️ Actualizando rol: User ID: {user_id}, Role: {role}")
                updateUserData(user_id, role, "")
            if not role:
                return build_response(400, "Missing status")
                



        if route_key == 'deleteUsers': 
            if not user_id :
                return build_response(400, "Missing user_id")
            status = data.get('status')
            if status:
                print(f"🛠️ Actualizando status: User ID: {user_id}, status {status}")
                updateUserData(user_id, "", status)
            if not status:
                return build_response(400, "Missing status")
            



        if route_key == 'insertUsers':
            print("conectado al backend")
            user = data.get('users')
            print(f"🛠️ Insertando usuarios: {user}") 
            if not user:
                return build_response(400, "Missing users")
            try:
                insertUsersDB(user)
            except Exception as e:
                print(f"[ERROR] Falló insertUsers: {e}")
                return build_response(500, f"Error al insertar usuarios: {str(e)}")


        usuarios = get_users_from_db()
        print(f"🛠️ Usuarios obtenidos: {usuarios}")
        payload = {"type": "getusersResponse", "data": usuarios}
        broadcast_to_all(payload)
        return build_response(200, "Users inserted and broadcasted")


    except Exception as e:
        logging.error(f"❗ Error en Lambda: {str(e)}")
        return build_response(500, "Internal Server Error")
