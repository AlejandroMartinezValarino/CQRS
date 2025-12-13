#!/usr/bin/env python3
"""Script de diagnóstico para Railway."""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    """Función principal de diagnóstico."""
    print("=" * 60)
    print("DIAGNÓSTICO DE RAILWAY")
    print("=" * 60)
    print()
    
    # 1. Verificar variables de entorno
    print("📋 Variables de entorno:")
    env_vars = [
        "PGHOST", "PGPORT", "PGUSER", "PGDATABASE",
        "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_DB",
        "DATABASE_URL", "RAILWAY_PRIVATE_DOMAIN", "RAILWAY_ENVIRONMENT"
    ]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Ocultar contraseñas
            if "PASSWORD" in var or "PGPASSWORD" in var:
                print(f"  {var}: ***")
            elif "DATABASE_URL" in var and "@" in str(value):
                masked = value.split("@")[0].split("://")[0] + "://***@" + value.split("@")[1]
                print(f"  {var}: {masked}")
            else:
                print(f"  {var}: {value}")
    print()
    
    # 2. Verificar settings
    print("⚙️  Configuración de Settings:")
    try:
        from config.settings import settings
        print(f"  POSTGRES_HOST: {settings.POSTGRES_HOST}")
        print(f"  POSTGRES_PORT: {settings.POSTGRES_PORT}")
        print(f"  POSTGRES_USER: {settings.POSTGRES_USER}")
        print(f"  POSTGRES_DB: {settings.POSTGRES_DB}")
        print(f"  POSTGRES_EVENT_STORE_DB: {settings.POSTGRES_EVENT_STORE_DB}")
        print("  ✓ Settings cargados correctamente")
    except Exception as e:
        print(f"  ✗ Error cargando settings: {e}")
        return
    print()
    
    # 3. Verificar get_pool_kwargs
    print("🔧 Verificando get_pool_kwargs:")
    try:
        from common.utils.db import get_pool_kwargs
        pool_kwargs = get_pool_kwargs(database='postgres')
        print(f"  Parámetros generados:")
        for key, value in pool_kwargs.items():
            if key == 'dsn' and '@' in str(value):
                parts = value.split('@')
                user_pass = parts[0].split('://')[1]
                user = user_pass.split(':')[0]
                masked = value.replace(user_pass, f"{user}:***")
                print(f"    {key}: {masked}")
            elif 'password' in key.lower():
                print(f"    {key}: ***")
            else:
                print(f"    {key}: {value}")
        print("  ✓ get_pool_kwargs funciona correctamente")
    except Exception as e:
        print(f"  ✗ Error en get_pool_kwargs: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 4. Intentar conexión a PostgreSQL
    print("🔌 Intentando conectar a PostgreSQL:")
    try:
        import asyncpg
        from common.utils.db import get_pool_kwargs
        
        # Intentar con get_pool_kwargs
        pool_kwargs = get_pool_kwargs(database='postgres')
        print(f"  Intentando conectar con get_pool_kwargs...")
        conn = await asyncpg.connect(**pool_kwargs)
        
        # Verificar versión
        version = await conn.fetchval("SELECT version()")
        print(f"  ✓ Conexión exitosa!")
        print(f"  PostgreSQL: {version.split(',')[0]}")
        
        # Listar bases de datos
        databases = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false")
        print(f"  Bases de datos existentes:")
        for db in databases:
            print(f"    - {db['datname']}")
        
        await conn.close()
    except Exception as e:
        print(f"  ✗ Error conectando: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # 5. Verificar tablas en bases de datos
    print("📊 Verificando tablas:")
    for db_name in [settings.POSTGRES_DB, settings.POSTGRES_EVENT_STORE_DB]:
        print(f"  Base de datos: {db_name}")
        try:
            pool_kwargs = get_pool_kwargs(database=db_name)
            conn = await asyncpg.connect(**pool_kwargs)
            
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            if tables:
                print(f"    Tablas encontradas:")
                for table in tables:
                    # Contar registros
                    try:
                        count = await conn.fetchval(f'SELECT COUNT(*) FROM {table["table_name"]}')
                        print(f"      - {table['table_name']}: {count} registros")
                    except Exception as e:
                        print(f"      - {table['table_name']}: Error contando registros ({e})")
            else:
                print(f"    ⚠️  No se encontraron tablas")
            
            await conn.close()
        except Exception as e:
            print(f"    ✗ Error: {e}")
    print()
    
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
