"""Script para ejecutar migraciones SQL usando psql."""
import subprocess
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings


def run_migration(db_name: str, migration_file: Path):
    """Ejecuta una migración SQL usando psql."""
    try:
        # Usar psql con conexión TCP/IP usando el usuario de settings
        # Leer usuario desde settings
        import os
        from config.settings import settings
        
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        
        # Usar PGPASSWORD para evitar prompt
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        cmd = [
            "psql",
            "-h", "localhost",  # Forzar conexión TCP/IP
            "-U", user,
            "-d", db_name,
            "-f", str(migration_file.absolute())
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            env=env
        )
        
        if result.returncode == 0:
            print(f"✓ Migración {migration_file.name} ejecutada en {db_name}")
        else:
            # Si hay errores, mostrarlos pero continuar
            if "already exists" in result.stderr.lower() or "already exists" in result.stdout.lower():
                print(f"⚠ Tablas ya existen en {db_name} (esto es normal si ya ejecutaste las migraciones)")
            else:
                print(f"✗ Error ejecutando {migration_file.name} en {db_name}")
                print(f"  Error: {result.stderr}")
                return False
        return True
    except Exception as e:
        print(f"✗ Error ejecutando {migration_file.name} en {db_name}: {e}")
        return False


def main():
    """Función principal."""
    migrations_dir = Path(__file__).parent / "migrations"
    
    migrations = [
        (settings.POSTGRES_EVENT_STORE_DB, migrations_dir / "001_create_event_store.sql"),
        (settings.POSTGRES_DB, migrations_dir / "002_create_read_model.sql"),
    ]
    
    print("Ejecutando migraciones...")
    print(f"Usuario: {settings.POSTGRES_USER}")
    print(f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print()
    
    success = True
    for db_name, migration_file in migrations:
        if migration_file.exists():
            if not run_migration(db_name, migration_file):
                success = False
        else:
            print(f"⚠ Archivo no encontrado: {migration_file}")
            success = False
    
    if success:
        print("\n✓ Migraciones completadas!")
    else:
        print("\n⚠ Algunas migraciones tuvieron problemas. Revisa los mensajes arriba.")
        print("\nAlternativa: Ejecuta las migraciones manualmente con:")
        print(f"  export PGPASSWORD={settings.POSTGRES_PASSWORD}")
        print(f"  psql -h localhost -U {settings.POSTGRES_USER} -d {settings.POSTGRES_EVENT_STORE_DB} -f scripts/migrations/001_create_event_store.sql")
        print(f"  psql -h localhost -U {settings.POSTGRES_USER} -d {settings.POSTGRES_DB} -f scripts/migrations/002_create_read_model.sql")
        print(f"  unset PGPASSWORD")


if __name__ == "__main__":
    main()

