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
    import socket
    from urllib.parse import urlparse, urlunparse
    
    pool_kwargs = get_pool_kwargs(database='postgres')
    original_host = pool_kwargs.get('host')
    
    # Primero intentar usar DATABASE_URL directamente como DSN (asyncpg puede resolver mejor)
    database_url = getattr(settings, 'DATABASE_URL', None)
    if database_url and not database_url.startswith("${{"):
        parsed = urlparse(database_url)
        original_hostname = parsed.hostname
        
        # Lista de URLs a intentar (con diferentes hostnames)
        urls_to_try = []
        
        # 1. URL original con hostname original
        modified_url_original = urlunparse((
            parsed.scheme,
            parsed.netloc,
            '/postgres',
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        urls_to_try.append(('original', modified_url_original))
        
        # 2. Si el hostname es .railway.internal, intentar con localhost
        if original_hostname and original_hostname.endswith('.railway.internal'):
            # Reemplazar el hostname con localhost pero mantener credenciales
            netloc_parts = parsed.netloc.split('@')
            if len(netloc_parts) == 2:
                # Hay usuario:contraseña@hostname
                user_pass = netloc_parts[0]
                new_netloc = f"{user_pass}@localhost:{parsed.port or 5432}"
            else:
                # Solo hostname:puerto
                new_netloc = f"localhost:{parsed.port or 5432}"
            
            modified_url_localhost = urlunparse((
                parsed.scheme,
                new_netloc,
                '/postgres',
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            urls_to_try.append(('localhost', modified_url_localhost))
        
        # Intentar cada URL
        for url_name, url in urls_to_try:
            try:
                print(f"Intentando conectar usando DATABASE_URL ({url_name})...")
                conn = await asyncpg.connect(url)
                
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
                print(f"  ✗ Falló con DATABASE_URL ({url_name}): {error_msg}")
                continue
    
    # Si DATABASE_URL falla, intentar con parámetros individuales
    hosts_to_try = []
    
    # Intentar resolver el hostname original a IP
    if original_host and original_host.endswith('.railway.internal'):
        try:
            ip = socket.gethostbyname(original_host)
            print(f"Resuelto {original_host} -> {ip}")
            hosts_to_try.append(ip)
        except socket.gaierror:
            print(f"No se pudo resolver {original_host}, intentando alternativas...")
            hosts_to_try.append('localhost')
            hosts_to_try.append('127.0.0.1')
    else:
        hosts_to_try.append(original_host)
    
    if original_host and original_host not in hosts_to_try:
        hosts_to_try.insert(0, original_host)
    
    last_error = None
    for host in hosts_to_try:
        try:
            test_kwargs = pool_kwargs.copy()
            test_kwargs['host'] = host
            print(f"Intentando conectar a: {host}:{test_kwargs.get('port')}")
            
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
            last_error = e
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"  ✗ Falló con {host}: {error_msg}")
            continue
    
    print(f"✗ Error creando base de datos '{db_name}': {last_error}")
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
