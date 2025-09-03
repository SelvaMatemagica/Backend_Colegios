import json
from urllib.parse import parse_qs
import datetime
import pg8000.native
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass, field, asdict, fields

# Conexion con la base de datos
def connection():
    return pg8000.native.Connection(
        host="db-aws-instace.cr6acsua6egs.us-east-2.rds.amazonaws.com",
        port=5432,
        database="aws_database",
        user="postgres",
        password="Selva.2025",
        )