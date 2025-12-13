#!/bin/bash
# Script para actualizar la rama frontend con los últimos cambios de main

set -e

echo "🔄 Actualizando rama frontend con cambios de main..."

# Verificar que estamos en la rama correcta o cambiar a main primero
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    echo "⚠️  Estás en la rama $CURRENT_BRANCH. Cambiando a main primero..."
    git checkout main || git checkout master
fi

# Asegurar que main está actualizado
echo "📥 Actualizando main desde remoto..."
git pull origin main || git pull origin master || echo "⚠️  No se pudo hacer pull, continuando..."

# Cambiar a rama frontend
echo ""
echo "🌿 Cambiando a rama frontend..."
git checkout frontend 2>/dev/null || {
    echo "⚠️  La rama frontend no existe, creándola..."
    git checkout -b frontend
}

# Hacer merge de main a frontend
echo ""
echo "🔀 Haciendo merge de main a frontend..."
git merge main || git merge master || {
    echo "⚠️  Hay conflictos. Resuélvelos manualmente y luego:"
    echo "   git add ."
    echo "   git commit -m 'Merge main into frontend'"
    exit 1
}

# Asegurar que los cambios del frontend están presentes
echo ""
echo "✅ Verificando cambios del frontend..."

# Verificar que .gitignore existe y tiene contenido
if [ -f "frontend/.gitignore" ] && [ -s "frontend/.gitignore" ]; then
    echo "✅ frontend/.gitignore existe y tiene contenido"
else
    echo "⚠️  frontend/.gitignore no existe o está vacío"
fi

# Verificar que Dockerfile tiene npm install
if grep -q "npm install" frontend/Dockerfile; then
    echo "✅ frontend/Dockerfile usa npm install"
else
    echo "⚠️  frontend/Dockerfile no usa npm install"
fi

echo ""
echo "✅ Rama frontend actualizada!"
echo ""
echo "💡 Para hacer push:"
echo "   git push origin frontend"
echo ""
