"""Script para crear las bases de datos si no existen."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
import asyncpg


async def create_database_if_not_exists(db_name: str):
    """Crea una base de datos si no existe."""
    try:
        # Conectarse a la base de datos 'postgres' (siempre existe)
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database='postgres'  # Conectarse a la BD por defecto
        )
        
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
    print("Creando bases de datos...")
    print(f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"Usuario: {settings.POSTGRES_USER}")
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
