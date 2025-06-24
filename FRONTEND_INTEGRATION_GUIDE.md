# 🚀 GUÍA DE INTEGRACIÓN FRONTEND-BACKEND - AccountIA Sprint 2

## ✅ CAMBIOS APLICADOS

### 🔧 **1. Configuración de Vite Corregida**
- ✅ Proxy cambiado de `http://backend:8000` a `http://localhost:8000`
- ✅ Configuración optimizada para desarrollo local

### 🔗 **2. URLs de API Estandarizadas**
- ✅ Dashboard actualizado para usar `/api/v1/declarations/`
- ✅ Implementación mejorada usando `declarationService`
- ✅ Manejo de respuestas corregido

### 🛠️ **3. Optimizaciones del Código**
- ✅ Dashboard refactorizado para usar servicios existentes
- ✅ Utilidades de estado del servicio implementadas
- ✅ Manejo de errores mejorado

---

## 🧪 PASOS PARA PROBAR LA INTEGRACIÓN

### **Paso 1: Verificar Backend Funcionando**
```bash
# En terminal 1: Ejecutar el backend
cd "C:\Users\justi\Desktop\Proyecto Accountia"
python backend/manage.py runserver

# Verificar que muestre:
# System check identified no issues (0 silenced).
# Starting development server at http://127.0.0.1:8000/
```

### **Paso 2: Probar APIs del Backend**
```bash
# En PowerShell, probar endpoints:
curl http://localhost:8000/health/
curl http://localhost:8000/api/v1/declarations/

# Deberían responder exitosamente
```

### **Paso 3: Instalar Dependencias del Frontend**
```bash
# En terminal 2: Preparar frontend
cd "C:\Users\justi\Desktop\Proyecto Accountia\frontend"
npm install

# Verificar que no hay errores
```

### **Paso 4: Ejecutar Frontend**
```bash
# En el mismo terminal 2:
npm run dev

# Debería mostrar:
# Local:   http://localhost:3000/
# Network: http://192.168.x.x:3000/
```

### **Paso 5: Probar Integración Web**
1. **Abrir navegador**: http://localhost:3000
2. **Verificar carga**: La página debería cargar sin errores de consola
3. **Probar navegación**: Navegar a diferentes secciones
4. **Verificar llamadas API**: Abrir DevTools → Network y ver llamadas a localhost:8000

---

## 🔍 VERIFICACIÓN DE PROBLEMAS COMUNES

### ❌ **Problema: CORS Error**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```
**Solución**: ✅ Ya configurado en `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### ❌ **Problema: Network Error**
```
TypeError: Failed to fetch
```
**Verificar**:
1. Backend ejecutándose en puerto 8000
2. Variables de entorno cargadas correctamente
3. Proxy de Vite configurado (✅ ya corregido)

### ❌ **Problema: 404 en APIs**
```
GET http://localhost:8000/declarations/ 404 (Not Found)
```
**Solución**: ✅ Ya corregido - URLs cambiadas a `/api/v1/declarations/`

---

## 🎯 FUNCIONALIDADES A PROBAR

### **Dashboard Principal**
- [ ] Carga lista de declaraciones existentes
- [ ] Muestra estadísticas correctas
- [ ] Botón "Crear Declaración" funciona
- [ ] Estados de declaraciones se muestran correctamente

### **Creación de Declaraciones**
- [ ] Formulario de nueva declaración funciona
- [ ] Se envía al backend correctamente
- [ ] Redirección después de crear funciona
- [ ] Lista se actualiza con nueva declaración

### **Manejo de Errores**
- [ ] Errores de red se muestran al usuario
- [ ] Errores de validación se muestran
- [ ] Estados de carga funcionan

---

## 📊 DATOS DE PRUEBA DISPONIBLES

Tu backend ya tiene estos datos de prueba:

```json
// Declaración ID 1
{
  "id": 1,
  "fiscal_year": 2024,
  "status": "draft",
  "total_income": "0.00",
  "total_withholdings": "0.00",
  "user_email": "test@accountia.co"
}

// Declaración ID 2  
{
  "id": 2,
  "fiscal_year": 2025,
  "status": "draft"
}
```

---

## 🚀 COMANDOS ÚTILES

### **Desarrollo Rápido**
```bash
# Terminal 1 - Backend
npm run backend

# Terminal 2 - Frontend  
npm run frontend

# Terminal 3 - Ambos (alternativa)
npm run dev
```

### **Debugging**
```bash
# Ver logs del backend
tail -f logs/django.log

# Ver logs del frontend
# Abrir DevTools en navegador
```

### **Reiniciar Servicios**
```bash
# Reiniciar backend si hay cambios
Ctrl+C y luego: python backend/manage.py runserver

# Reiniciar frontend si hay cambios
Ctrl+C y luego: npm run dev
```

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [x] ✅ Variables de entorno configuradas
- [x] ✅ Backend ejecutándose en puerto 8000
- [x] ✅ Frontend configurado para puerto 3000
- [x] ✅ Proxy de Vite corregido
- [x] ✅ URLs de API estandarizadas
- [x] ✅ Servicios del frontend optimizados
- [ ] ⏳ Frontend ejecutándose sin errores
- [ ] ⏳ Llamadas API funcionando
- [ ] ⏳ Dashboard cargando datos
- [ ] ⏳ Creación de declaraciones funcional

---

## 🆘 RESOLUCIÓN DE PROBLEMAS

### **Si el Frontend No Conecta**
1. Verificar que backend esté en puerto 8000
2. Comprobar variables VITE_API_URL en .env
3. Reiniciar el servidor de desarrollo de Vite
4. Limpiar caché: `npm run build && npm run dev`

### **Si Hay Errores de TypeScript**
```bash
cd frontend
npm run type-check
```

### **Si Hay Errores de ESLint**
```bash
cd frontend
npm run lint:fix
```

---

## 🔄 PRÓXIMOS PASOS DESPUÉS DE LA INTEGRACIÓN

1. **Implementar Autenticación Real**
   - Habilitar Firebase Auth
   - Remover `DEV_SKIP_AUTH_FOR_TESTING`

2. **Agregar Más Funcionalidades**
   - Carga de documentos
   - Procesamiento de exógena
   - Generación de reportes

3. **Optimización**
   - Implementar estado global con Zustand
   - Agregar caching de APIs
   - Mejorar manejo de errores

---

## 📞 SOPORTE

Si encuentras problemas:
1. Verificar que todos los pasos se siguieron
2. Revisar logs de consola del navegador
3. Verificar logs del backend Django
4. Comprobar que puertos 3000 y 8000 estén disponibles

**¡La integración debería funcionar perfectamente con estos cambios! 🚀**
