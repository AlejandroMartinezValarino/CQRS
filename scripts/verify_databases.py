"""Script para verificar el estado de las bases de datos."""
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
    
    databases_to_check = [
        settings.POSTGRES_DB,
        settings.POSTGRES_EVENT_STORE_DB
    ]
    
    for db_name in databases_to_check:
        print(f"\n📦 Verificando base de datos: {db_name}")
        print("-" * 60)
        
        try:
            # Conectar a la base de datos
            pool_kwargs = get_pool_kwargs(database=db_name)
            pool = await asyncpg.create_pool(**pool_kwargs, min_size=1, max_size=2)
            
            try:
                # Verificar existencia de la base de datos
                exists = await pool.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1", 
                    db_name
                )
                
                if exists:
                    print(f"✅ Base de datos '{db_name}' existe")
                else:
                    print(f"❌ Base de datos '{db_name}' NO existe")
                    continue
                
                # Listar tablas
                tables = await pool.fetch("""
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
                            count = await pool.fetchval(
                                f'SELECT COUNT(*) FROM "{table["table_name"]}"'
                            )
                            print(f"   - {table['table_name']}: {count} registros")
                        except Exception as e:
                            print(f"   - {table['table_name']}: error contando ({str(e)[:50]})")
                else:
                    print("\n⚠️  No se encontraron tablas en esta base de datos")
                
            finally:
                await pool.close()
                
        except Exception as e:
            print(f"❌ Error verificando '{db_name}': {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETADA")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(check_databases())
