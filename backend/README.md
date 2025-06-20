# AccountIA Backend

Este directorio contiene la API backend de AccountIA construida con Django.

## Estructura

- `config/` - Configuración del proyecto Django
- `apps/` - Aplicaciones Django modulares
- `core/` - Utilidades centrales (Celery, cache, etc.)
- `static/` - Archivos estáticos
- `media/` - Archivos subidos por usuarios
- `templates/` - Plantillas HTML
- `fixtures/` - Datos iniciales

## Apps Principales

### authentication
Manejo de usuarios y autenticación con Firebase

### users  
Gestión de perfiles de usuario

### declarations
Lógica de declaraciones de renta

### documents
Gestión de documentos y archivos

### ai_core
Integración con IA y servicios de análisis

### payments
Procesamiento de pagos

## Comandos Útiles

```bash
# Crear nueva app
python manage.py startapp nueva_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test

# Shell interactivo
python manage.py shell
```