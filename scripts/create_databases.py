"""Script para crear las bases de datos si no existen."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from common.utils.db import get_pool_kwargs
import asyncpg


async def create_database_if_not_exists(db_name: str):
    """Crea una base de datos si no existe."""
    pool_kwargs = get_pool_kwargs(database='postgres')
    original_host = pool_kwargs.get('host')
    
    # Lista de hostnames a intentar (útil para Railway)
    hosts_to_try = [original_host]
    if original_host and original_host.endswith('.railway.internal'):
        # En Railway, intentar también con localhost
        hosts_to_try.append('localhost')
        # También intentar con 127.0.0.1
        hosts_to_try.append('127.0.0.1')
    
    last_error = None
    for host in hosts_to_try:
        try:
            # Conectarse a la base de datos 'postgres' (siempre existe)
            test_kwargs = pool_kwargs.copy()
            test_kwargs['host'] = host
            print(f"Intentando conectar a: {host}:{test_kwargs.get('port')}")
            
            conn = await asyncpg.connect(**test_kwargs)
            
            try:
                # Verificar si la base de datos existe
                exists = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1", db_name
                )
                
                if exists:
                    print(f"✓ Base de datos '{db_name}' ya existe")
                    return True
                else:
                    # Crear la base de datos
                    await conn.execute(f'CREATE DATABASE "{db_name}"')
                    print(f"✓ Base de datos '{db_name}' creada exitosamente")
                    return True
            finally:
                await conn.close()
        except Exception as e:
            last_error = e
            print(f"  ✗ Falló con {host}: {e}")
            continue
    
    # Si todos los intentos fallaron
    print(f"✗ Error creando base de datos '{db_name}': {last_error}")
    return False


async def main():
    """Función principal."""
    import os
    
    print("Creando bases de datos...")
    
    # Verificar variables de entorno de Railway
    pghost = os.getenv('PGHOST')
    pgport = os.getenv('PGPORT')
    pguser = os.getenv('PGUSER')
    
    if pghost:
        print(f"Usando variables de Railway:")
        print(f"  PGHOST: {pghost}")
        print(f"  PGPORT: {pgport or 'N/A'}")
        print(f"  PGUSER: {pguser or 'N/A'}")
    else:
        print(f"Usando configuración de settings:")
        print(f"  Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
        print(f"  Usuario: {settings.POSTGRES_USER}")
    
    # Mostrar parámetros que se usarán realmente
    pool_kwargs = get_pool_kwargs(database='postgres')
    print(f"\nParámetros de conexión:")
    print(f"  Host: {pool_kwargs.get('host')}")
    print(f"  Port: {pool_kwargs.get('port')}")
    print(f"  User: {pool_kwargs.get('user')}")
    print()
    
    databases = [
        settings.POSTGRES_DB,
        settings.POSTGRES_EVENT_STORE_DB,
    ]
    
    success = True
    for db_name in databases:
        if not await create_database_if_not_exists(db_name):
            success = False
    
    if success:
        print("\n✓ Todas las bases de datos están listas!")
    else:
        print("\n⚠ Algunas bases de datos tuvieron problemas.")


if __name__ == "__main__":
    asyncio.run(main())
