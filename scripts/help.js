#!/usr/bin/env node

const chalk = require('chalk');

const commands = {
  '🚀 Desarrollo': {
    'npm run setup': 'Configuración inicial del proyecto (ejecutar primero)',
    'npm run dev': 'Iniciar entorno de desarrollo',
    'npm start': 'Alias para npm run dev',
    'npm run stop': 'Detener todos los servicios',
    'npm run restart': 'Reiniciar todos los servicios',
    'npm run logs': 'Ver logs de todos los servicios',
    'npm run logs:backend': 'Ver logs del backend',
    'npm run logs:frontend': 'Ver logs del frontend'
  },
  
  '🗄️ Base de Datos': {
    'npm run db:migrate': 'Ejecutar migraciones de base de datos',
    'npm run db:makemigrations': 'Crear nuevas migraciones',
    'npm run db:seed': 'Cargar datos iniciales/prueba',
    'npm run db:shell': 'Abrir shell de PostgreSQL',
    'npm run db:backup': 'Crear backup de la base de datos',
    'npm run db:restore': 'Restaurar backup de BD',
    'npm run db:reset': 'Limpiar toda la base de datos'
  },
  
  '👤 Usuario y Shell': {
    'npm run user:create': 'Crear superusuario de Django',
    'npm run shell:backend': 'Abrir shell de Django',
    'npm run shell:db': 'Abrir shell de base de datos'
  },
  
  '🧪 Testing': {
    'npm test': 'Ejecutar todos los tests',
    'npm run test:backend': 'Ejecutar tests del backend',
    'npm run test:frontend': 'Ejecutar tests del frontend',
    'npm run test:coverage': 'Tests con reporte de cobertura',
    'npm run test:e2e': 'Tests end-to-end',
    'npm run test:load': 'Tests de carga'
  },
  
  '🎨 Calidad de Código': {
    'npm run lint': 'Verificar calidad de código',
    'npm run format': 'Formatear código automáticamente',
    'npm run lint:backend': 'Linting solo backend',
    'npm run lint:frontend': 'Linting solo frontend'
  },
  
  '🤖 Inteligencia Artificial': {
    'npm run ai:update-kb': 'Actualizar base de conocimiento de IA',
    'npm run ai:test': 'Probar funcionalidades de IA',
    'npm run ai:process-docs': 'Procesar nuevos documentos para IA'
  },
  
  '🔨 Build y Deploy': {
    'npm run build': 'Construir imágenes Docker',
    'npm run build:prod': 'Construir para producción',
    'npm run deploy:dev': 'Deploy a desarrollo',
    'npm run deploy:staging': 'Deploy a staging',
    'npm run deploy:prod': 'Deploy a producción'
  },
  
  '📚 Documentación': {
    'npm run docs': 'Generar documentación de API',
    'npm run docs:serve': 'Servir documentación localmente'
  },
  
  '🔍 Verificación de Servicios': {
    'npm run verify:all': 'Verificar todos los servicios desde Docker',
    'npm run verify:services': 'Verificar Redis, Celery y Base de Datos',
    'npm run verify:gcs': 'Verificar Google Cloud Storage (Mock)',
    'npm run celery:test': 'Verificar servicios desde Docker',
    'npm run gcs:test': 'Verificar Google Cloud Storage',
    'npm run redis:cli': 'Acceder a Redis CLI',
    'npm run celery:worker': 'Ver logs del worker Celery'
  },
  
  '🛠️ Utilidades': {
    'npm run health': 'Verificar salud de servicios',
    'npm run monitoring': 'Iniciar stack de monitoreo',
    'npm run clean': 'Limpiar contenedores y volúmenes',
    'npm run reset': 'Reset completo (clean + setup)',
    'npm run debug': 'Información de debug del sistema'
  }
};

console.log(chalk.blue.bold('📖 AccountIA - Comandos Disponibles\n'));

Object.entries(commands).forEach(([category, cmds]) => {
  console.log(chalk.yellow.bold(category));
  Object.entries(cmds).forEach(([cmd, desc]) => {
    console.log(`  ${chalk.green(cmd.padEnd(30))} ${desc}`);
  });
  console.log('');
});

console.log(chalk.cyan('💡 Ejemplos de uso:'));
console.log('  npm run setup         # Configuración inicial');
console.log('  npm run dev           # Iniciar desarrollo');
console.log('  npm run verify:all    # Verificar todos los servicios');
console.log('  npm test              # Ejecutar tests');
console.log('  npm run logs          # Ver logs');
console.log('');
console.log(chalk.yellow('🆘 ¿Problemas?'));
console.log('  npm run debug         # Información de debug');
console.log('  npm run health        # Verificar servicios');
console.log('  npm run verify:all    # Verificación completa desde Docker');
console.log('  npm run clean         # Limpiar todo');
console.log('');