#!/bin/bash
# Script para crear ramas separadas para cada servicio en Railway
# Cada rama solo tendrá su Dockerfile específico (renombrado a Dockerfile)

set -e

echo "🚀 Configurando ramas para Railway..."

# Verificar que estamos en la rama main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Estás en la rama $CURRENT_BRANCH. Cambiando a main..."
    git checkout main || git checkout master
fi

# 1. Command Side
echo ""
echo "📦 Configurando rama command-side..."
git checkout -b command-side 2>/dev/null || git checkout command-side
# Renombrar Dockerfile.command a Dockerfile
if [ -f "Dockerfile.command" ] && [ ! -f "Dockerfile" ]; then
    mv Dockerfile.command Dockerfile
    echo "✅ Renombrado Dockerfile.command → Dockerfile"
fi
# Eliminar otros Dockerfiles
[ -f "Dockerfile.read" ] && rm Dockerfile.read && echo "🗑️  Eliminado Dockerfile.read"
[ -f "Dockerfile.consumer" ] && rm Dockerfile.consumer && echo "🗑️  Eliminado Dockerfile.consumer"
# Configurar railway.json (apuntar a Dockerfile, no Dockerfile.command)
cp railway.command.json railway.json
# Actualizar railway.json para apuntar a Dockerfile
sed -i 's/Dockerfile\.command/Dockerfile/g' railway.json
git add -A
git commit -m "Configurar rama command-side: solo Dockerfile" || true
echo "💡 Para hacer push: git push -u origin command-side"
echo "   (O configura tus credenciales de Git primero)"

# 2. Read Side
echo ""
echo "📦 Configurando rama read-side..."
git checkout main || git checkout master
git checkout -b read-side 2>/dev/null || git checkout read-side
# Renombrar Dockerfile.read a Dockerfile
if [ -f "Dockerfile.read" ] && [ ! -f "Dockerfile" ]; then
    mv Dockerfile.read Dockerfile
    echo "✅ Renombrado Dockerfile.read → Dockerfile"
fi
# Eliminar otros Dockerfiles
[ -f "Dockerfile.command" ] && rm Dockerfile.command && echo "🗑️  Eliminado Dockerfile.command"
[ -f "Dockerfile.consumer" ] && rm Dockerfile.consumer && echo "🗑️  Eliminado Dockerfile.consumer"
# Configurar railway.json (apuntar a Dockerfile, no Dockerfile.read)
cp railway.read.json railway.json
# Actualizar railway.json para apuntar a Dockerfile
sed -i 's/Dockerfile\.read/Dockerfile/g' railway.json
git add -A
git commit -m "Configurar rama read-side: solo Dockerfile" || true
echo "💡 Para hacer push: git push -u origin read-side"

# 3. Consumer
echo ""
echo "📦 Configurando rama consumer..."
git checkout main || git checkout master
git checkout -b consumer 2>/dev/null || git checkout consumer
# Asegurar que el script corregido run_kafka_consumer.py esté presente
if [ -f "scripts/run_kafka_consumer.py" ]; then
    # Verificar que tiene el fix del PYTHONPATH
    if ! grep -q "sys.path.insert" scripts/run_kafka_consumer.py; then
        echo "⚠️  El script run_kafka_consumer.py no tiene el fix, actualizando..."
        # El script ya debería estar corregido en main, pero por si acaso
        git checkout main -- scripts/run_kafka_consumer.py 2>/dev/null || true
    fi
    echo "✅ Script run_kafka_consumer.py corregido presente"
fi
# Renombrar Dockerfile.consumer a Dockerfile
if [ -f "Dockerfile.consumer" ] && [ ! -f "Dockerfile" ]; then
    mv Dockerfile.consumer Dockerfile
    echo "✅ Renombrado Dockerfile.consumer → Dockerfile"
fi
# Eliminar otros Dockerfiles
[ -f "Dockerfile.command" ] && rm Dockerfile.command && echo "🗑️  Eliminado Dockerfile.command"
[ -f "Dockerfile.read" ] && rm Dockerfile.read && echo "🗑️  Eliminado Dockerfile.read"
# Configurar railway.json (apuntar a Dockerfile, no Dockerfile.consumer)
cp railway.consumer.json railway.json
# Actualizar railway.json para apuntar a Dockerfile
sed -i 's/Dockerfile\.consumer/Dockerfile/g' railway.json
git add -A
git commit -m "Configurar rama consumer: solo Dockerfile + script corregido" || true
echo "💡 Para hacer push: git push -u origin consumer"

# 4. Frontend (ya tiene su Dockerfile en frontend/)
echo ""
echo "📦 Configurando rama frontend..."
git checkout main || git checkout master
git checkout -b frontend 2>/dev/null || git checkout frontend
# Eliminar TODOS los Dockerfiles de la raíz (frontend tiene el suyo en frontend/)
echo "🗑️  Eliminando Dockerfiles de la raíz..."
[ -f "Dockerfile.command" ] && rm Dockerfile.command && echo "   ✓ Eliminado Dockerfile.command"
[ -f "Dockerfile.read" ] && rm Dockerfile.read && echo "   ✓ Eliminado Dockerfile.read"
[ -f "Dockerfile.consumer" ] && rm Dockerfile.consumer && echo "   ✓ Eliminado Dockerfile.consumer"
[ -f "Dockerfile" ] && rm Dockerfile && echo "   ✓ Eliminado Dockerfile de la raíz"
# También eliminar railway.json de la raíz si existe
[ -f "railway.json" ] && rm railway.json && echo "   ✓ Eliminado railway.json de la raíz"
# Verificar que frontend/railway.json existe
if [ -f "frontend/railway.json" ]; then
    echo "✅ frontend/railway.json ya existe"
else
    echo "⚠️  frontend/railway.json no existe, creándolo..."
    cat > frontend/railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
EOF
    git add frontend/railway.json
fi
git add -A
git commit -m "Configurar rama frontend: eliminar Dockerfiles de raíz, solo frontend/Dockerfile" || true
echo "💡 Para hacer push: git push -u origin frontend"

# Volver a main
git checkout main || git checkout master

echo ""
echo "✅ ¡Ramas configuradas localmente!"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Configurar credenciales de Git (si no están configuradas):"
echo "   git config --global credential.helper store"
echo "   # O usar un token de acceso personal de GitHub"
echo ""
echo "2. Hacer push de las ramas:"
echo "   git push -u origin command-side"
echo "   git push -u origin read-side"
echo "   git push -u origin consumer"
echo "   git push -u origin frontend"
echo ""
echo "3. Configurar en Railway UI:"
echo ""
echo "   Command Side:"
echo "   - Settings → Source → Branch: command-side"
echo "   - Root Directory: (vacío)"
echo ""
echo "   Read Side:"
echo "   - Settings → Source → Branch: read-side"
echo "   - Root Directory: (vacío)"
echo ""
echo "   Consumer:"
echo "   - Settings → Source → Branch: consumer"
echo "   - Root Directory: (vacío)"
echo ""
echo "   Frontend:"
echo "   - Settings → Source → Branch: frontend"
echo "   - Root Directory: frontend"
echo ""
