"""Script para verificar el estado de las bases de datos en Railway."""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from common.utils.db import get_pool_kwargs
import asyncpg


async def check_databases():
    """Verifica el estado de las bases de datos."""
    print("="*60)
    print("VERIFICANDO BASES DE DATOS")
    print("="*60)
    print(f"\nConexión PostgreSQL:")
    print(f"  Host: {settings.POSTGRES_HOST}")
    print(f"  Port: {settings.POSTGRES_PORT}")
    print(f"  User: {settings.POSTGRES_USER}")
    print()
    
    databases_to_check = [
        settings.POSTGRES_DB,
        settings.POSTGRES_EVENT_STORE_DB
    ]
    
    for db_name in databases_to_check:
        print(f"\n📦 Verificando base de datos: {db_name}")
        print("-" * 60)
        
        try:
            # Usar get_pool_kwargs como los servicios
            pool_kwargs = get_pool_kwargs(database=db_name)
            
            # Conectar usando los mismos parámetros que los servicios
            conn = await asyncpg.connect(**pool_kwargs, timeout=10)
            
            try:
                print(f"✅ Conexión exitosa a '{db_name}'")
                
                # Listar tablas
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                
                if tables:
                    print(f"\n📊 Tablas encontradas ({len(tables)}):")
                    for table in tables:
                        # Contar registros
                        try:
                            count = await conn.fetchval(
                                f'SELECT COUNT(*) FROM "{table["table_name"]}"'
                            )
                            print(f"   - {table['table_name']}: {count} registros")
                        except Exception as e:
                            print(f"   - {table['table_name']}: error contando ({str(e)[:50]})")
                else:
                    print("\n⚠️  No se encontraron tablas en esta base de datos")
                    print("   (La base de datos existe pero está vacía)")
                
            finally:
                await conn.close()
                
        except asyncpg.InvalidCatalogNameError:
            print(f"❌ La base de datos '{db_name}' NO existe")
            print(f"   Debe ser creada ejecutando: python scripts/create_databases.py")
        except asyncpg.exceptions.InvalidPasswordError:
            print(f"❌ Error de autenticación para '{db_name}'")
            print(f"   Verifica las credenciales en las variables de entorno")
        except Exception as e:
            print(f"❌ Error conectando a '{db_name}': {type(e).__name__}: {e}")
    
    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETADA")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(check_databases())
    except KeyboardInterrupt:
        print("\n\nVerificación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
