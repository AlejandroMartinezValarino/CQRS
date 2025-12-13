"""Script de depuración completo del sistema."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from common.utils.db import get_pool_kwargs
import asyncpg


async def check_database(db_name: str, expected_tables: list, optional_tables: list = None):
    """Verifica el estado de una base de datos."""
    if optional_tables is None:
        optional_tables = []
    
    print(f"\n{'='*60}")
    print(f"Verificando base de datos: {db_name}")
    print(f"{'='*60}")
    
    try:
        pool_kwargs = get_pool_kwargs(database=db_name)
        print(f"Conectando a: {pool_kwargs.get('host')}:{pool_kwargs.get('port')}")
        conn = await asyncpg.connect(**pool_kwargs)
        
        try:
            # Verificar tablas
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            print(f"\n✓ Conexión exitosa")
            print(f"✓ Tablas encontradas: {len(tables)}")
            
            if tables:
                print("\nTablas:")
                for table in tables:
                    table_name = table['table_name']
                    try:
                        count = await conn.fetchval(f'SELECT COUNT(*) FROM {table_name}')
                        print(f"  - {table_name}: {count} registros")
                    except Exception as e:
                        print(f"  - {table_name}: ERROR al contar ({e})")
                
                # Verificar tablas esperadas
                found_tables = {t['table_name'] for t in tables}
                missing_tables = set(expected_tables) - found_tables
                missing_optional = set(optional_tables) - found_tables
                
                if missing_tables:
                    print(f"\n⚠ Tablas requeridas faltantes: {', '.join(missing_tables)}")
                else:
                    print(f"\n✓ Todas las tablas requeridas están presentes")
                
                if missing_optional:
                    print(f"ℹ Tablas opcionales faltantes: {', '.join(missing_optional)}")
            else:
                print("\n⚠ No se encontraron tablas (las migraciones pueden no haberse ejecutado)")
                print(f"  Tablas esperadas: {', '.join(expected_tables)}")
            
            return True
        finally:
            await conn.close()
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"✗ La base de datos '{db_name}' no existe")
        return False
    except asyncpg.exceptions.InvalidPasswordError:
        print(f"✗ Error de autenticación")
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        return False


async def check_database_exists(db_name: str):
    """Verifica si una base de datos existe."""
    try:
        pool_kwargs = get_pool_kwargs(database='postgres')
        conn = await asyncpg.connect(**pool_kwargs)
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )
            return exists is not None
        finally:
            await conn.close()
    except Exception:
        return False


async def main():
    """Función principal."""
    print("="*60)
    print("DIAGNÓSTICO DEL SISTEMA CQRS")
    print("="*60)
    print(f"\nConfiguración:")
    print(f"  Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f"  Usuario: {settings.POSTGRES_USER}")
    database_url = getattr(settings, 'DATABASE_URL', None)
    if database_url:
        # Ocultar contraseña
        if '@' in database_url:
            parts = database_url.split('@')
            if '://' in parts[0]:
                user_pass = parts[0].split('://')[1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked = database_url.replace(user_pass, f"{user}:***")
                    print(f"  DATABASE_URL: {masked}")
                else:
                    print(f"  DATABASE_URL: Configurada (oculta)")
            else:
                print(f"  DATABASE_URL: Configurada (oculta)")
        else:
            print(f"  DATABASE_URL: Configurada")
    else:
        print(f"  DATABASE_URL: No configurada (usando variables individuales)")
    
    databases = [
        (settings.POSTGRES_DB, "Read Model", [
            "anime_clicks",
            "anime_views", 
            "anime_ratings",
            "anime_stats",
            "processed_events",
            "dead_letter_queue"
        ], [
            "animes"  # Tabla opcional (se crea con load_mal_to_postgres.py)
        ]),
        (settings.POSTGRES_EVENT_STORE_DB, "Event Store", [
            "event_store"
        ], []),
    ]
    
    all_ok = True
    for db_info in databases:
        if len(db_info) == 3:
            db_name, description, expected_tables = db_info
            optional_tables = []
        else:
            db_name, description, expected_tables, optional_tables = db_info
        
        print(f"\n{description}:")
        exists = await check_database_exists(db_name)
        if exists:
            print(f"✓ Base de datos '{db_name}' existe")
            if not await check_database(db_name, expected_tables, optional_tables):
                all_ok = False
        else:
            print(f"✗ Base de datos '{db_name}' NO existe")
            all_ok = False
    
    print(f"\n{'='*60}")
    if all_ok:
        print("✓ Todas las verificaciones pasaron")
        print("\nRecomendaciones:")
        print("  - Si los servicios siguen dando 502, revisa los logs de Railway")
        print("  - Verifica que los servicios estén escuchando en el puerto correcto (Railway usa PORT)")
        print("  - Verifica la configuración de dominios en Railway")
    else:
        print("✗ Algunas verificaciones fallaron")
        print("\nRecomendaciones:")
        print("  - Ejecuta: python scripts/create_databases.py")
        print("  - Ejecuta: python scripts/run_migrations.py")
        print("  - Verifica las variables de entorno en Railway")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
