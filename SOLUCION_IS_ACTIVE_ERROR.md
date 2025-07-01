# 🚨 Error: "no such column: declarations_declaration.is_active"

## Problema Identificado
El error ocurre porque el modelo `Declaration` fue actualizado para incluir nuevos campos (`is_active`, `title`, `deleted_at`), pero las migraciones de Django no se han aplicado a la base de datos.

## Error en el Frontend
```
Error listando declaraciones: no such column: declarations_declaration.is_active
```

## Causa Raíz
- ✅ El modelo `Declaration` tiene el campo `is_active` 
- ✅ El código backend usa `queryset.filter(is_active=True)`
- ❌ La base de datos no tiene la columna `is_active`
- ❌ Las migraciones no se han aplicado

## Solución Rápida

### Opción 1: Script Automático (Recomendado)
```bash
# Ejecutar el script de reparación rápida
quick_fix.bat
```

### Opción 2: Comandos Manuales
```bash
# 1. Iniciar servicios
npm run docker:up

# 2. Aplicar migraciones
npm run backend:migrate

# 3. Verificar
curl http://localhost:8000/health/
```

### Opción 3: Desde el backend directamente
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

## Archivos Involucrados

### ✅ Migración Creada
- `backend/apps/declarations/migrations/0002_update_declaration_model.py`

### ✅ Scripts de Reparación
- `quick_fix.bat` - Solución rápida
- `fix_backend.ps1` - Solución completa con verificaciones
- `fix_backend_simple.bat` - Solución step-by-step

### 📝 Archivos del Problema
- `backend/apps/declarations/models.py` - Modelo con campos nuevos
- `backend/apps/declarations/views.py` - ViewSet que usa `is_active`
- `frontend/src/services/declarationService.ts` - Servicio que llama al API

## Campos Agregados en la Migración

1. **`title`** - Título descriptivo de la declaración
2. **`is_active`** - Para soft delete (eliminar sin borrar de DB)
3. **`deleted_at`** - Fecha de eliminación lógica

## Cambios en Constraints

- **ELIMINADO**: `unique_together = [('user', 'fiscal_year')]`
- **AGREGADO**: Índices para mejor performance
- **PERMITE**: Múltiples declaraciones por año fiscal

## Verificación Post-Solución

1. **Backend Health**: `http://localhost:8000/health/`
2. **API Declaraciones**: `http://localhost:8000/api/v1/declarations/`
3. **Frontend Dashboard**: `http://localhost:3000/dashboard`

## Comando de Verificación Completa
```bash
# Verificar todo el sistema
npm run verify:sprint2
```

## En caso de persistir el error

1. **Reset completo de Docker**:
   ```bash
   npm run docker:clean
   npm run setup
   ```

2. **Verificar logs**:
   ```bash
   npm run logs:backend
   ```

3. **Aplicar migración manualmente**:
   ```bash
   cd backend
   python manage.py showmigrations
   python manage.py migrate --verbosity=2
   ```

## Prevención Futura

- Siempre ejecutar `npm run backend:migrate` después de cambios en modelos
- Usar `npm run backend:makemigrations` antes de hacer commits
- Verificar con `npm run health` antes de desplegar cambios

---

**📝 Nota**: Este problema es común en desarrollo cuando se actualizan modelos de Django sin aplicar las migraciones correspondientes.
