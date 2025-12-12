# Configuración de Dominios en Railway

## Dominio: alejandrotech.eu

### Recomendación de Subdominios

```
api.alejandrotech.eu          → Command Side API (puerto 8000)
graphql.alejandrotech.eu      → Read Side GraphQL (puerto 8001)
app.alejandrotech.eu          → Frontend
```

O alternativamente:

```
cqrs-api.alejandrotech.eu     → Command Side API
cqrs-graphql.alejandrotech.eu → Read Side GraphQL
cqrs.alejandrotech.eu         → Frontend
```

## Pasos para Configurar Dominios en Railway

### 1. Configurar DNS en tu proveedor de dominio

Ve a tu proveedor de DNS (donde gestionas alejandrotech.eu) y crea estos registros CNAME:

```
api.alejandrotech.eu     CNAME  →  [tu-proyecto-command].up.railway.app
graphql.alejandrotech.eu CNAME  →  [tu-proyecto-read].up.railway.app
app.alejandrotech.eu     CNAME  →  [tu-proyecto-frontend].up.railway.app
```

### 2. Configurar en Railway - Command Side

1. Ve al servicio **Command Side**
2. Settings → **Networking**
3. Haz clic en **"Generate Domain"** o **"Custom Domain"**
4. Ingresa: `api.alejandrotech.eu`
5. Railway te dará un registro CNAME - úsalo en tu DNS
6. Espera a que Railway verifique el dominio (puede tardar unos minutos)

### 3. Configurar en Railway - Read Side

1. Ve al servicio **Read Side**
2. Settings → **Networking**
3. Ingresa: `graphql.alejandrotech.eu`
4. Configura el CNAME en tu DNS

### 4. Configurar en Railway - Frontend

1. Ve al servicio **Frontend**
2. Settings → **Networking**
3. Ingresa: `app.alejandrotech.eu`
4. Configura el CNAME en tu DNS

### 5. Actualizar Variables de Entorno del Frontend

Una vez que los dominios estén configurados, actualiza las variables del Frontend:

```
VITE_API_URL=https://api.alejandrotech.eu
VITE_GRAPHQL_URL=https://graphql.alejandrotech.eu/graphql
```

**Importante:** Después de cambiar estas variables, necesitas **reconstruir** el servicio Frontend porque Vite necesita estas variables en tiempo de build.

## Verificación

Una vez configurado, verifica:

- ✅ `https://api.alejandrotech.eu/health` → Debe responder
- ✅ `https://graphql.alejandrotech.eu/health` → Debe responder
- ✅ `https://app.alejandrotech.eu` → Debe cargar el frontend

## Notas

- Railway proporciona SSL automáticamente para dominios personalizados
- Los cambios de DNS pueden tardar hasta 48 horas (normalmente menos)
- Puedes verificar el estado del dominio en Railway → Settings → Networking
