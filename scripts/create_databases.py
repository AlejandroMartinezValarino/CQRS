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
    try:
        # Conectarse a la base de datos 'postgres' (siempre existe)
        pool_kwargs = get_pool_kwargs(database='postgres')
        conn = await asyncpg.connect(**pool_kwargs)
        
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
        print(f"✗ Error creando base de datos '{db_name}': {e}")
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
