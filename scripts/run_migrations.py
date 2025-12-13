"""Script para ejecutar migraciones SQL usando asyncpg."""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from common.utils.db import get_pool_kwargs
import asyncpg


async def run_migration(db_name: str, migration_file: Path):
    """Ejecuta una migración SQL usando asyncpg."""
    try:
        pool_kwargs = get_pool_kwargs(database=db_name)
        conn = await asyncpg.connect(**pool_kwargs)
        
        try:
            sql_content = migration_file.read_text()
            await conn.execute(sql_content)
            print(f"✓ Migración {migration_file.name} ejecutada en {db_name}")
            return True
        except asyncpg.exceptions.DuplicateTableError:
            print(f"⚠ Tablas ya existen en {db_name} (esto es normal si ya ejecutaste las migraciones)")
            return True
        except asyncpg.exceptions.DuplicateObjectError as e:
            if "already exists" in str(e).lower():
                print(f"⚠ Objetos ya existen en {db_name} (esto es normal si ya ejecutaste las migraciones)")
                return True
            raise
        except asyncpg.exceptions.PostgresSyntaxError as e:
            print(f"✗ Error de sintaxis en {migration_file.name}: {e}")
            return False
        finally:
            await conn.close()
    except asyncpg.exceptions.InvalidPasswordError:
        print(f"✗ Error de autenticación para {db_name}")
        return False
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"✗ Base de datos {db_name} no existe")
        return False
    except Exception as e:
        print(f"✗ Error ejecutando {migration_file.name} en {db_name}: {e}")
        return False


async def main():
    """Función principal."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    migrations = [
        (settings.POSTGRES_EVENT_STORE_DB, migrations_dir / "001_create_event_store.sql"),
        (settings.POSTGRES_DB, migrations_dir / "002_create_read_model.sql"),
        (settings.POSTGRES_DB, migrations_dir / "003_add_event_processing_tracking.sql"),
        (settings.POSTGRES_DB, migrations_dir / "004_create_dead_letter_queue.sql"),
        (settings.POSTGRES_DB, migrations_dir / "005_add_indexes.sql"),
    ]
    
    print("Ejecutando migraciones...")
    print(f"Usuario: {settings.POSTGRES_USER}")
    print(f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print()
    
    success = True
    for db_name, migration_file in migrations:
        if migration_file.exists():
            if not await run_migration(db_name, migration_file):
                success = False
        else:
            print(f"⚠ Archivo no encontrado: {migration_file}")
            success = False
    
    if success:
        print("\n✓ Migraciones completadas!")
    else:
        print("\n⚠ Algunas migraciones tuvieron problemas. Revisa los mensajes arriba.")


if __name__ == "__main__":
    asyncio.run(main())

