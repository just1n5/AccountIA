# AccountIA Frontend

Aplicación React con TypeScript para AccountIA.

## Stack Tecnológico

- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Herramienta de build rápida
- **Tailwind CSS** - Framework de estilos utilitarios
- **Firebase** - Autenticación
- **Zustand** - Gestión de estado
- **React Router** - Enrutamiento
- **React Hook Form** - Manejo de formularios
- **Axios** - Cliente HTTP

## Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── ui/             # Componentes base (Button, Input, etc.)
│   ├── layout/         # Layout y navegación
│   ├── auth/           # Componentes de autenticación
│   └── declaration/    # Componentes específicos de declaraciones
├── pages/              # Páginas/rutas principales
├── hooks/              # Custom hooks
├── services/           # Servicios API y Firebase
├── store/              # Gestión de estado (Zustand)
├── utils/              # Utilidades y helpers
├── types/              # Definiciones de TypeScript
└── styles/             # Estilos globales
```

## Comandos Disponibles

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Tests
npm run test

# Linting
npm run lint

# Formateo de código
npm run format

# Type checking
npm run type-check
```

## Configuración de Entorno

Copia `.env.example` a `.env` y configura las variables necesarias:

```bash
cp .env.example .env
```

Variables importantes:
- `VITE_API_URL` - URL del backend
- `VITE_FIREBASE_*` - Configuración de Firebase

## Estructura de Componentes

### Sistema de Diseño
Todos los componentes siguen el sistema de diseño definido en `src/styles/` basado en:
- Paleta de colores centrada en azul (confianza) y verde (éxito)
- Tipografía Inter para máxima legibilidad
- Espaciado consistente basado en múltiplos de 4px
- Componentes reutilizables en `components/ui/`

### Componentes Principales
- `Button` - Botones con variantes (primary, secondary, success)
- `Input` - Campos de formulario con validación
- `Card` - Contenedores de contenido
- `Alert` - Notificaciones y mensajes
- `FileUpload` - Carga de archivos con drag & drop

## Autenticación

La autenticación se maneja a través de Firebase Auth con los siguientes métodos:
- Email/Password
- Google OAuth
- Recuperación de contraseña

Los tokens se almacenan automáticamente y se incluyen en las requests al backend.

## Gestión de Estado

Utilizamos Zustand para el estado global:
- `authStore` - Estado de autenticación
- `declarationStore` - Estado de declaraciones
- `uiStore` - Estado de UI (modales, loading, etc.)

## API Integration

Los servicios de API están en `src/services/`:
- Configuración base con interceptors
- Manejo automático de tokens
- Transformación de respuestas
- Manejo centralizado de errores

## Testing

- **Vitest** - Framework de testing
- **Testing Library** - Utilities para testing de React
- **MSW** - Mock Service Worker para mocking de APIs

## Deployment

El frontend se despliega automáticamente:
- Development: Cada push a `develop`
- Staging: Cada push a `staging`  
- Production: Cada push a `main`