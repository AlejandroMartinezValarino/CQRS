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
    import asyncio
    from urllib.parse import urlparse, urlunparse
    
    pool_kwargs = get_pool_kwargs(database='postgres')
    
    # Si get_pool_kwargs retornó una DSN, usarla directamente
    if 'dsn' in pool_kwargs:
        dsn = pool_kwargs['dsn']
        parsed = urlparse(dsn)
        original_hostname = parsed.hostname
        
        # Lista de hostnames a intentar (según Railway docs, también se puede usar "postgres")
        hostnames_to_try = []
        if original_hostname and original_hostname.endswith('.railway.internal'):
            # Intentar primero con el hostname simplificado (ej: postgres.railway.internal -> postgres)
            service_name = original_hostname.replace('.railway.internal', '')
            hostnames_to_try.append(service_name)  # "postgres" primero
        hostnames_to_try.append(original_hostname)  # "postgres.railway.internal" después
        
        # Intentar con cada hostname
        for hostname in hostnames_to_try:
            # Modificar la DSN para apuntar a la base de datos 'postgres' y cambiar hostname
            netloc_parts = parsed.netloc.split('@')
            if len(netloc_parts) == 2:
                # Hay usuario:contraseña@hostname:puerto
                user_pass = netloc_parts[0]
                port_part = netloc_parts[1].split(':')
                if len(port_part) == 2:
                    new_netloc = f"{user_pass}@{hostname}:{port_part[1]}"
                else:
                    new_netloc = f"{user_pass}@{hostname}:{parsed.port or 5432}"
            else:
                # Solo hostname:puerto
                port_part = parsed.netloc.split(':')
                if len(port_part) == 2:
                    new_netloc = f"{hostname}:{port_part[1]}"
                else:
                    new_netloc = f"{hostname}:{parsed.port or 5432}"
            
            modified_dsn = urlunparse((
                parsed.scheme,
                new_netloc,
                '/postgres',  # Conectar a la BD 'postgres' para crear otras BDs
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            # Intentar múltiples veces con retry (la red privada puede tardar)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if attempt > 0:
                        wait_time = 2 ** attempt  # Exponential backoff: 2, 4 segundos
                        print(f"Reintentando en {wait_time} segundos... (intento {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    
                    print(f"Intentando conectar usando DSN con hostname '{hostname}'...")
                    # Usar solo la DSN, sin otros parámetros del pool
                    conn = await asyncpg.connect(modified_dsn)
                    
                    try:
                        exists = await conn.fetchval(
                            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
                        )
                        
                        if exists:
                            print(f"✓ Base de datos '{db_name}' ya existe")
                            return True
                        else:
                            await conn.execute(f'CREATE DATABASE "{db_name}"')
                            print(f"✓ Base de datos '{db_name}' creada exitosamente")
                            return True
                    finally:
                        await conn.close()
                except Exception as e:
                    error_msg = str(e)
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    print(f"  ✗ Falló con hostname '{hostname}' (intento {attempt + 1}/{max_retries}): {error_msg}")
                    if attempt == max_retries - 1:
                        # Último intento de este hostname falló, probar siguiente hostname
                        break
                    # Continuar con el siguiente intento
    
    # Fallback: intentar con DATABASE_URL directamente o RAILWAY_PRIVATE_DOMAIN
    import os
    database_url = getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')
    
    # Si DATABASE_URL tiene templates no resueltos, intentar construir usando RAILWAY_PRIVATE_DOMAIN
    if database_url and database_url.startswith("${{"):
        print("⚠ DATABASE_URL contiene templates no resueltos, intentando construir URL...")
        railway_private_domain = os.getenv('RAILWAY_PRIVATE_DOMAIN')
        pguser = os.getenv('PGUSER') or getattr(settings, 'POSTGRES_USER', 'postgres')
        pgpassword = os.getenv('PGPASSWORD') or getattr(settings, 'POSTGRES_PASSWORD', '')
        pgdatabase = 'postgres'  # Para crear bases de datos, necesitamos conectar a 'postgres'
        
        print(f"  RAILWAY_PRIVATE_DOMAIN: {railway_private_domain or 'No disponible'}")
        
        # Construir usando RAILWAY_PRIVATE_DOMAIN si está disponible
        if railway_private_domain:
            print(f"  Construyendo URL usando RAILWAY_PRIVATE_DOMAIN: {railway_private_domain}")
            database_url = f"postgresql://{pguser}:{pgpassword}@{railway_private_domain}:5432/{pgdatabase}"
        else:
            print("  ⚠ RAILWAY_PRIVATE_DOMAIN no está disponible")
            print("  ⚠ Necesitas configurar DATABASE_URL manualmente en Railway")
            database_url = None
    
    if database_url and not database_url.startswith("${{"):
        parsed = urlparse(database_url)
        original_hostname = parsed.hostname
        
        # Lista de hostnames a intentar (según Railway docs, también se puede usar "postgres")
        hostnames_to_try = []
        if original_hostname and original_hostname.endswith('.railway.internal'):
            # Intentar con el hostname simplificado (ej: postgres.railway.internal -> postgres)
            service_name = original_hostname.replace('.railway.internal', '')
            hostnames_to_try.append(service_name)  # "postgres"
        hostnames_to_try.append(original_hostname)  # "postgres.railway.internal"
        
        for hostname in hostnames_to_try:
            try:
                # Reemplazar el hostname en la URL
                netloc_parts = parsed.netloc.split('@')
                if len(netloc_parts) == 2:
                    # Hay usuario:contraseña@hostname:puerto
                    user_pass = netloc_parts[0]
                    port_part = netloc_parts[1].split(':')
                    if len(port_part) == 2:
                        new_netloc = f"{user_pass}@{hostname}:{port_part[1]}"
                    else:
                        new_netloc = f"{user_pass}@{hostname}:{parsed.port or 5432}"
                else:
                    # Solo hostname:puerto
                    port_part = parsed.netloc.split(':')
                    if len(port_part) == 2:
                        new_netloc = f"{hostname}:{port_part[1]}"
                    else:
                        new_netloc = f"{hostname}:{parsed.port or 5432}"
                
                modified_url = urlunparse((
                    parsed.scheme,
                    new_netloc,
                    '/postgres',
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                
                print(f"Intentando conectar usando DATABASE_URL con hostname '{hostname}'...")
                conn = await asyncpg.connect(modified_url)
                
                try:
                    exists = await conn.fetchval(
                        "SELECT 1 FROM pg_database WHERE datname = $1", db_name
                    )
                    
                    if exists:
                        print(f"✓ Base de datos '{db_name}' ya existe")
                        return True
                    else:
                        await conn.execute(f'CREATE DATABASE "{db_name}"')
                        print(f"✓ Base de datos '{db_name}' creada exitosamente")
                        return True
                finally:
                    await conn.close()
            except Exception as e:
                error_msg = str(e)
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                print(f"  ✗ Falló con hostname '{hostname}': {error_msg}")
                continue
    
    # Último fallback: usar parámetros individuales si están disponibles
    if 'host' in pool_kwargs and pool_kwargs['host']:
        try:
            print(f"Intentando conectar usando parámetros individuales...")
            # Remover 'dsn' si existe para usar parámetros individuales
            test_kwargs = {k: v for k, v in pool_kwargs.items() if k != 'dsn' and not k.startswith('_')}
            conn = await asyncpg.connect(**test_kwargs)
            
            try:
                exists = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1", db_name
                )
                
                if exists:
                    print(f"✓ Base de datos '{db_name}' ya existe")
                    return True
                else:
                    await conn.execute(f'CREATE DATABASE "{db_name}"')
                    print(f"✓ Base de datos '{db_name}' creada exitosamente")
                    return True
            finally:
                await conn.close()
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"  ✗ Falló con parámetros individuales: {error_msg}")
    
    print(f"✗ Error creando base de datos '{db_name}': No se pudo conectar")
    print(f"\n⚠ Sugerencia: Verifica en Railway que el servicio PostgreSQL esté correctamente conectado")
    print(f"   y que esté en la misma red privada que este servicio.")
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
    if 'dsn' in pool_kwargs:
        # Ocultar contraseña en DSN
        dsn = pool_kwargs['dsn']
        if '@' in dsn:
            parts = dsn.split('@')
            if '://' in parts[0]:
                user_pass = parts[0].split('://')[1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    masked = dsn.replace(user_pass, f"{user}:***")
                    print(f"  DSN: {masked}")
                else:
                    print(f"  DSN: [configurada]")
            else:
                print(f"  DSN: [configurada]")
        else:
            print(f"  DSN: {dsn}")
    else:
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
