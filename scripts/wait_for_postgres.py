"""Script para esperar a que PostgreSQL esté disponible."""
import asyncio
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
import asyncpg
import socket


async def wait_for_postgres(max_attempts=30, delay=2):
    """
    Espera hasta que PostgreSQL esté disponible.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Segundos entre intentos
    """
    database_url = getattr(settings, 'DATABASE_URL', None) or os.getenv('DATABASE_URL')
    postgres_host = settings.POSTGRES_HOST
    postgres_port = settings.POSTGRES_PORT
    
    print("="*60)
    print("ESPERANDO A QUE POSTGRESQL ESTÉ DISPONIBLE")
    print("="*60)
    print(f"Host: {postgres_host}:{postgres_port}")
    print(f"Intentos máximos: {max_attempts}")
    print(f"Delay entre intentos: {delay}s")
    print()
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Primero intentar resolver el DNS
            print(f"[{attempt}/{max_attempts}] Intentando resolver DNS para {postgres_host}...")
            try:
                socket.getaddrinfo(postgres_host, postgres_port, socket.AF_UNSPEC, socket.SOCK_STREAM)
                print(f"  ✓ DNS resuelto exitosamente")
            except socket.gaierror as e:
                print(f"  ✗ No se pudo resolver DNS: {e}")
                if attempt < max_attempts:
                    print(f"  Esperando {delay}s antes de reintentar...")
                    await asyncio.sleep(delay)
                continue
            
            # Si el DNS se resuelve, intentar conectar a PostgreSQL
            print(f"[{attempt}/{max_attempts}] Intentando conectar a PostgreSQL...")
            
            if database_url and not database_url.startswith("${{"):
                # Usar DATABASE_URL
                conn = await asyncpg.connect(database_url, timeout=5)
            else:
                # Usar parámetros individuales
                conn = await asyncpg.connect(
                    host=postgres_host,
                    port=postgres_port,
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database='postgres',  # Base de datos por defecto
                    timeout=5
                )
            
            # Verificar que la conexión funciona
            version = await conn.fetchval('SELECT version()')
            await conn.close()
            
            print(f"  ✓ Conexión exitosa!")
            print(f"  PostgreSQL version: {version[:50]}...")
            print()
            print("="*60)
            print("✓ POSTGRESQL ESTÁ LISTO")
            print("="*60)
            return True
            
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 80:
                error_msg = error_msg[:80] + "..."
            print(f"  ✗ Error: {error_msg}")
            
            if attempt < max_attempts:
                print(f"  Esperando {delay}s antes de reintentar...")
                await asyncio.sleep(delay)
            else:
                print()
                print("="*60)
                print("✗ NO SE PUDO CONECTAR A POSTGRESQL")
                print("="*60)
                print()
                print("Diagnóstico:")
                print(f"  - Host: {postgres_host}")
                print(f"  - Port: {postgres_port}")
                print(f"  - DATABASE_URL configurado: {bool(database_url)}")
                print()
                print("Posibles causas:")
                print("  1. El servicio PostgreSQL no está en ejecución")
                print("  2. La red privada de Railway aún no está lista")
                print("  3. El hostname no se puede resolver (problema de DNS)")
                print("  4. Las credenciales son incorrectas")
                print()
                print("Sugerencias:")
                print("  - Verifica que el servicio PostgreSQL esté desplegado")
                print("  - Verifica que ambos servicios estén en el mismo proyecto")
                print("  - Intenta redesplegar el servicio")
                print("  - Contacta al soporte de Railway si el problema persiste")
                return False
    
    return False


if __name__ == "__main__":
    result = asyncio.run(wait_for_postgres())
    sys.exit(0 if result else 1)
