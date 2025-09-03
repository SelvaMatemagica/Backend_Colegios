import pg8000.native

# Conexion con la base de datos
def connection_users():
    return pg8000.native.Connection(
        host="db-aws-instace.cr6acsua6egs.us-east-2.rds.amazonaws.com",
        database="aws_database",
        user="postgres",
        password="Selva.2025",
        port=5432
    )

#Funcion para registrarse en la aplicacion
def createDB_users():
    conn = connection_users()
    try:
        conn.run("""    CREATE TABLE IF NOT EXISTS conexiones_activas (
                        connection_id TEXT PRIMARY KEY,
                        user_id UUID NOT NULL,
                        status TEXT,
                        last_seen TIMESTAMP NOT NULL DEFAULT NOW(),
                        FOREIGN KEY (user_id) REFERENCES teachers(unique_id) ON DELETE CASCADE
                    );
        """)

    finally:
        conn.close()