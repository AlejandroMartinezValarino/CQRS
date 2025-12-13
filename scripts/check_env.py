"""Script para verificar variables de entorno de Railway."""
import os

print("="*60)
print("VARIABLES DE ENTORNO RELACIONADAS CON POSTGRESQL")
print("="*60)

# Variables estándar de PostgreSQL
pg_vars = [
    'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE',
    'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 
    'POSTGRES_PASSWORD', 'POSTGRES_DB', 'DATABASE_URL'
]

print("\nVariables de entorno PostgreSQL:")
for var in pg_vars:
    value = os.getenv(var)
    if value:
        # Ocultar contraseñas
        if 'PASSWORD' in var or (var == 'DATABASE_URL' and '@' in value):
            if '@' in value:
                # Ocultar contraseña en DATABASE_URL
                parts = value.split('@')
                if '://' in parts[0]:
                    user_pass = parts[0].split('://')[1]
                    if ':' in user_pass:
                        user = user_pass.split(':')[0]
                        masked = value.replace(user_pass, f"{user}:***")
                        print(f"  {var}: {masked}")
                    else:
                        print(f"  {var}: [oculta]")
                else:
                    print(f"  {var}: [oculta]")
            else:
                print(f"  {var}: [oculta]")
        else:
            print(f"  {var}: {value}")
    else:
        print(f"  {var}: [no configurada]")

# Buscar todas las variables que contengan "POSTGRES" o "PG"
print("\nTodas las variables que contienen 'POSTGRES' o 'PG':")
all_vars = {k: v for k, v in os.environ.items() if 'POSTGRES' in k.upper() or k.startswith('PG')}
for var, value in sorted(all_vars.items()):
    if 'PASSWORD' in var or (var == 'DATABASE_URL' and '@' in value):
        print(f"  {var}: [oculta]")
    else:
        print(f"  {var}: {value}")

# Verificar si estamos en Railway
print("\nInformación del entorno Railway:")
railway_vars = [
    'RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_NAME',
    'RAILWAY_PRIVATE_DOMAIN'
]
for var in railway_vars:
    value = os.getenv(var)
    if value:
        print(f"  {var}: {value}")
    else:
        print(f"  {var}: [no configurada]")

print("\n" + "="*60)
