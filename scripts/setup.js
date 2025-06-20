#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');

// Función para ejecutar comandos con output en tiempo real
function execCommand(command, options = {}) {
  try {
    return execSync(command, { 
      stdio: 'inherit', 
      encoding: 'utf8',
      ...options 
    });
  } catch (error) {
    console.error(chalk.red(`❌ Error ejecutando: ${command}`));
    console.error(error.message);
    process.exit(1);
  }
}

// Función para verificar si un comando existe
function commandExists(command) {
  try {
    execSync(`${command} --version`, { stdio: 'ignore' });
    return true;
  } catch (error) {
    return false;
  }
}

// Función para crear directorios si no existen
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

// Función para crear archivo si no existe
function createFileIfNotExists(filePath, content = '# Python package\n') {
  ensureDirectoryExists(path.dirname(filePath));
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, content);
  }
}

// Mostrar header
console.log(chalk.blue.bold('=================================================='));
console.log(chalk.blue.bold('🚀 AccountIA - Setup Script'));
console.log(chalk.blue.bold('==================================================\n'));

// Verificar prerrequisitos
console.log(chalk.cyan('ℹ️  Verificando prerrequisitos...'));

if (!commandExists('docker')) {
  console.error(chalk.red('❌ Docker no está instalado. Por favor instala Docker Desktop primero.'));
  console.log('   Descarga desde: https://www.docker.com/products/docker-desktop/');
  process.exit(1);
}

// Verificar si Docker está ejecutándose
try {
  execSync('docker info', { stdio: 'ignore' });
} catch (error) {
  console.error(chalk.red('❌ Docker Desktop no está ejecutándose.'));
  console.log(chalk.yellow('💡 Por favor inicia Docker Desktop y espera a que esté listo.'));
  console.log('   Luego ejecuta: npm run setup');
  process.exit(1);
}

if (!commandExists('docker-compose')) {
  console.error(chalk.red('❌ Docker Compose no está disponible.'));
  process.exit(1);
}

console.log(chalk.green('✅ Prerrequisitos verificados'));

// Configurar variables de entorno
console.log(chalk.cyan('ℹ️  Configurando variables de entorno...'));

if (!fs.existsSync('.env')) {
  fs.copyFileSync('.env.example', '.env');
  console.log(chalk.green('✅ Archivo .env creado desde template'));
  console.log(chalk.yellow('⚠️  Por favor edita el archivo .env con tus configuraciones reales'));
} else {
  console.log(chalk.yellow('⚠️  Archivo .env ya existe, omitiendo...'));
}

// Crear directorios necesarios
console.log(chalk.cyan('ℹ️  Creando directorios necesarios...'));

const directories = [
  'backend/apps/authentication/migrations',
  'backend/apps/authentication/tests',
  'backend/apps/users/migrations',
  'backend/apps/users/tests',
  'backend/apps/declarations/migrations',
  'backend/apps/declarations/tests',
  'backend/apps/declarations/services',
  'backend/apps/documents/migrations',
  'backend/apps/documents/tests',
  'backend/apps/documents/services',
  'backend/apps/ai_core/migrations',
  'backend/apps/ai_core/tests',
  'backend/apps/ai_core/services',
  'backend/apps/ai_core/prompts',
  'backend/apps/payments/migrations',
  'backend/apps/payments/tests',
  'backend/apps/payments/services',
  'backend/apps/common',
  'backend/core',
  'backend/static',
  'backend/media/uploads',
  'backend/templates/emails',
  'backend/fixtures',
  'backend/scripts',
  'frontend/src/components/ui',
  'frontend/src/components/layout',
  'frontend/src/components/auth',
  'frontend/src/components/declaration',
  'frontend/src/components/common',
  'frontend/src/pages/DeclarationFlow',
  'frontend/src/hooks',
  'frontend/src/services',
  'frontend/src/store',
  'frontend/src/utils',
  'frontend/src/types',
  'frontend/src/styles',
  'frontend/tests/__mocks__',
  'frontend/tests/utils',
  'frontend/tests/components',
  'frontend/tests/pages',
  'ai_knowledge/documents/estatuto_tributario',
  'ai_knowledge/documents/dian_concepts',
  'ai_knowledge/documents/regulations',
  'ai_knowledge/processed/embeddings',
  'ai_knowledge/processed/chunks',
  'ai_knowledge/processed/index',
  'ai_knowledge/scripts',
  'ai_knowledge/config',
  'database/fixtures',
  'database/schemas',
  'infrastructure/docker/backend',
  'infrastructure/docker/frontend',
  'infrastructure/docker/nginx',
  'infrastructure/gcp/terraform/modules/cloud-run',
  'infrastructure/gcp/terraform/modules/cloud-sql',
  'infrastructure/gcp/terraform/modules/cloud-storage',
  'infrastructure/gcp/terraform/modules/iam',
  'infrastructure/gcp/terraform/environments/development',
  'infrastructure/gcp/terraform/environments/staging',
  'infrastructure/gcp/terraform/environments/production',
  'infrastructure/gcp/cloudbuild',
  'infrastructure/gcp/scripts',
  'infrastructure/monitoring/prometheus/rules',
  'infrastructure/monitoring/grafana/dashboards',
  'infrastructure/monitoring/grafana/provisioning',
  'infrastructure/monitoring/alerts',
  'tests/integration',
  'tests/e2e/cypress/integration',
  'tests/e2e/cypress/fixtures',
  'tests/e2e/cypress/plugins',
  'tests/e2e/cypress/support',
  'tests/load/scenarios',
  'tests/load/results',
  'tests/fixtures',
  'logs',
  'backups',
  'tools/code-quality',
  'tools/monitoring',
  'tools/utilities'
];

directories.forEach(dir => {
  ensureDirectoryExists(dir);
});

console.log(chalk.green('✅ Directorios creados'));

// Crear archivos Python básicos
console.log(chalk.cyan('ℹ️  Creando archivos Python básicos...'));

const pythonApps = ['authentication', 'users', 'declarations', 'documents', 'ai_core', 'payments', 'common'];

pythonApps.forEach(app => {
  const appDir = `backend/apps/${app}`;
  
  // Crear archivos principales de la app
  createFileIfNotExists(`${appDir}/__init__.py`);
  createFileIfNotExists(`${appDir}/migrations/__init__.py`);
  createFileIfNotExists(`${appDir}/tests/__init__.py`);
  
  // Crear archivos básicos de Django si no existen
  createFileIfNotExists(`${appDir}/models.py`, `# ${app} models\nfrom django.db import models\n\n# Create your models here.\n`);
  createFileIfNotExists(`${appDir}/views.py`, `# ${app} views\nfrom rest_framework import viewsets\n\n# Create your views here.\n`);
  createFileIfNotExists(`${appDir}/urls.py`, `# ${app} URLs\nfrom django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\n\nurlpatterns = [\n    path('', include(router.urls)),\n]\n`);
  createFileIfNotExists(`${appDir}/serializers.py`, `# ${app} serializers\nfrom rest_framework import serializers\n\n# Create your serializers here.\n`);
  createFileIfNotExists(`${appDir}/admin.py`, `# ${app} admin\nfrom django.contrib import admin\n\n# Register your models here.\n`);
  
  if (app !== 'common') {
    createFileIfNotExists(`${appDir}/apps.py`, `from django.apps import AppConfig\n\n\nclass ${app.charAt(0).toUpperCase() + app.slice(1)}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.${app}'\n    verbose_name = '${app.charAt(0).toUpperCase() + app.slice(1)}'\n\n    def ready(self):\n        # Import signal handlers\n        pass\n`);
  }
});

// Crear archivos core
createFileIfNotExists('backend/core/__init__.py');
createFileIfNotExists('backend/core/celery.py', `# Celery configuration\nimport os\nfrom celery import Celery\n\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')\n\napp = Celery('accountia')\napp.config_from_object('django.conf:settings', namespace='CELERY')\napp.autodiscover_tasks()\n`);

console.log(chalk.green('✅ Archivos Python básicos creados'));

// Verificar y construir imágenes Docker
console.log(chalk.cyan('ℹ️  Verificando imágenes Docker...'));

try {
  // Intentar construir las imágenes
  console.log(chalk.cyan('ℹ️  Construyendo imágenes Docker (esto puede tomar unos minutos)...'));
  execCommand('docker-compose build --parallel');
  console.log(chalk.green('✅ Imágenes Docker construidas'));
} catch (error) {
  console.log(chalk.yellow('⚠️  Hubo un problema construyendo las imágenes Docker'));
  console.log(chalk.yellow('   Esto es normal en la primera ejecución. Continuando...'));
}

// Iniciar servicios básicos
console.log(chalk.cyan('ℹ️  Iniciando servicios básicos...'));

try {
  execCommand('docker-compose up -d postgres redis');
  console.log(chalk.green('✅ Servicios de base de datos iniciados'));
  
  console.log(chalk.cyan('ℹ️  Esperando que la base de datos esté lista...'));
  
  // Esperar a que PostgreSQL esté listo
  let dbReady = false;
  let attempts = 0;
  const maxAttempts = 30;
  
  while (!dbReady && attempts < maxAttempts) {
    try {
      execSync('docker-compose exec postgres pg_isready -U accountia_user', { stdio: 'ignore' });
      dbReady = true;
    } catch (error) {
      attempts++;
      if (attempts < maxAttempts) {
        process.stdout.write('.');
        // Esperar 2 segundos
        const start = Date.now();
        while (Date.now() - start < 2000) {
          // Busy wait
        }
      }
    }
  }
  
  if (dbReady) {
    console.log(chalk.green('\n✅ Base de datos lista'));
  } else {
    console.log(chalk.yellow('\n⚠️  La base de datos está tardando en iniciar, pero continuamos...'));
  }
  
} catch (error) {
  console.log(chalk.yellow('⚠️  Los servicios se iniciarán cuando ejecutes npm run dev'));
}

// Mostrar información final
console.log('\n' + chalk.blue.bold('=================================================='));
console.log(chalk.green.bold('✅ Setup de AccountIA completado! 🎉'));
console.log(chalk.blue.bold('==================================================\n'));

console.log(chalk.cyan('🎯 Próximos pasos:'));
console.log('1. Edita el archivo .env con tus configuraciones:');
console.log('   ' + chalk.yellow('code .env'));
console.log('2. Inicia el entorno de desarrollo:');
console.log('   ' + chalk.yellow('npm run dev'));
console.log('3. Verifica que todo funcione:');
console.log('   ' + chalk.yellow('npm run health'));
console.log('');

console.log(chalk.cyan('🌐 Servicios que estarán disponibles:'));
console.log('• Frontend:  http://localhost:3000');
console.log('• Backend:   http://localhost:8000');
console.log('• Admin:     http://localhost:8000/admin');
console.log('• API Docs:  http://localhost:8000/api/docs');
console.log('• PgAdmin:   http://localhost:5050');
console.log('• MailHog:   http://localhost:8025');
console.log('');

console.log(chalk.cyan('🛠️  Comandos útiles:'));
console.log('• npm run help     - Ver todos los comandos');
console.log('• npm run logs     - Ver logs de servicios');
console.log('• npm test         - Ejecutar tests');
console.log('• npm run health   - Verificar salud de servicios');
console.log('• npm run debug    - Información de debug');
console.log('');

console.log(chalk.yellow('⚠️  No olvides:'));
console.log('• Configurar Firebase authentication en .env');
console.log('• Configurar Google Cloud Platform para IA');
console.log('• Crear un superusuario: npm run user:create');
console.log('');