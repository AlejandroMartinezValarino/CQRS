#!/bin/bash
# Script para crear ramas separadas para cada servicio en Railway

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
git push -u origin command-side 2>/dev/null || echo "⚠️  Rama command-side ya existe en remoto"

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
git push -u origin read-side 2>/dev/null || echo "⚠️  Rama read-side ya existe en remoto"

# 3. Consumer
echo ""
echo "📦 Configurando rama consumer..."
git checkout main || git checkout master
git checkout -b consumer 2>/dev/null || git checkout consumer
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
git commit -m "Configurar rama consumer: solo Dockerfile" || true
git push -u origin consumer 2>/dev/null || echo "⚠️  Rama consumer ya existe en remoto"

# 4. Frontend (ya tiene su Dockerfile en frontend/)
echo ""
echo "📦 Configurando rama frontend..."
git checkout main || git checkout master
git checkout -b frontend 2>/dev/null || git checkout frontend
# Eliminar Dockerfiles de la raíz (frontend tiene el suyo en frontend/)
[ -f "Dockerfile.command" ] && rm Dockerfile.command && echo "🗑️  Eliminado Dockerfile.command"
[ -f "Dockerfile.read" ] && rm Dockerfile.read && echo "🗑️  Eliminado Dockerfile.read"
[ -f "Dockerfile.consumer" ] && rm Dockerfile.consumer && echo "🗑️  Eliminado Dockerfile.consumer"
[ -f "Dockerfile" ] && rm Dockerfile && echo "🗑️  Eliminado Dockerfile de la raíz"
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
# Eliminar railway.json de la raíz si existe (frontend usa frontend/railway.json)
[ -f "railway.json" ] && rm railway.json && echo "🗑️  Eliminado railway.json de la raíz"
git add -A
git commit -m "Configurar rama frontend: solo frontend/Dockerfile" || true
git push -u origin frontend 2>/dev/null || echo "⚠️  Rama frontend ya existe en remoto"

# Volver a main
git checkout main || git checkout master

echo ""
echo "✅ ¡Ramas configuradas!"
echo ""
echo "📋 Próximos pasos en Railway:"
echo ""
echo "1. Command Side:"
echo "   - Settings → Source → Branch: command-side"
echo "   - Root Directory: (vacío)"
echo ""
echo "2. Read Side:"
echo "   - Settings → Source → Branch: read-side"
echo "   - Root Directory: (vacío)"
echo ""
echo "3. Consumer:"
echo "   - Settings → Source → Branch: consumer"
echo "   - Root Directory: (vacío)"
echo ""
echo "4. Frontend:"
echo "   - Settings → Source → Branch: frontend"
echo "   - Root Directory: frontend"
echo ""
