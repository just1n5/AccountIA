#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const chalk = require('chalk');

function getCommandOutput(command, fallback = 'No disponible') {
  try {
    return execSync(command, { encoding: 'utf8' }).trim();
  } catch (error) {
    return fallback;
  }
}

function checkFileExists(filePath) {
  return fs.existsSync(filePath) ? '✅ Existe' : '❌ No encontrado';
}

console.log(chalk.blue.bold('🐛 AccountIA - Información de Debug\n'));

// Información del sistema
console.log(chalk.yellow('💻 Sistema:'));
console.log(`  OS: ${os.type()} ${os.release()} (${os.arch()})`);
console.log(`  Node.js: ${process.version}`);
console.log(`  Memoria total: ${Math.round(os.totalmem() / 1024 / 1024 / 1024)} GB`);
console.log(`  Memoria libre: ${Math.round(os.freemem() / 1024 / 1024 / 1024)} GB`);
console.log(`  CPU: ${os.cpus()[0].model} (${os.cpus().length} cores)`);

console.log('\n' + chalk.yellow('🔧 Herramientas:'));
console.log(`  Docker: ${getCommandOutput('docker --version')}`);
console.log(`  Docker Compose: ${getCommandOutput('docker-compose --version')}`);
console.log(`  Git: ${getCommandOutput('git --version')}`);
console.log(`  Python: ${getCommandOutput('python --version')}`);
console.log(`  npm: ${getCommandOutput('npm --version')}`);

console.log('\n' + chalk.yellow('📁 Archivos de configuración:'));
console.log(`  .env: ${checkFileExists('.env')}`);
console.log(`  docker-compose.yml: ${checkFileExists('docker-compose.yml')}`);
console.log(`  package.json: ${checkFileExists('package.json')}`);
console.log(`  backend/requirements.txt: ${checkFileExists('backend/requirements.txt')}`);
console.log(`  frontend/package.json: ${checkFileExists('frontend/package.json')}`);

console.log('\n' + chalk.yellow('🐳 Docker:'));
try {
  const dockerInfo = getCommandOutput('docker info --format "{{.ServerVersion}}"');
  console.log(`  Docker Engine: ${dockerInfo}`);
  
  const runningContainers = getCommandOutput('docker ps --filter "name=accountia" --format "{{.Names}}"');
  if (runningContainers) {
    console.log(`  Contenedores AccountIA ejecutándose:`);
    runningContainers.split('\n').forEach(container => {
      console.log(`    - ${container}`);
    });
  } else {
    console.log('  ❌ No hay contenedores AccountIA ejecutándose');
  }
  
  const dockerImages = getCommandOutput('docker images --filter "reference=accountia*" --format "{{.Repository}}:{{.Tag}} ({{.Size}})"');
  if (dockerImages) {
    console.log(`  Imágenes AccountIA:`);
    dockerImages.split('\n').forEach(image => {
      console.log(`    - ${image}`);
    });
  }
  
} catch (error) {
  console.log('  ❌ Docker no está disponible o no responde');
}

console.log('\n' + chalk.yellow('📊 Uso de recursos:'));
try {
  const dockerStats = getCommandOutput('docker stats --no-stream --format "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}" --filter "name=accountia"');
  console.log(dockerStats);
} catch (error) {
  console.log('  No se pudo obtener estadísticas de Docker');
}

console.log('\n' + chalk.yellow('🌐 Puertos en uso:'));
const ports = ['3000', '8000', '5432', '6379', '5050', '8025'];
ports.forEach(port => {
  try {
    if (process.platform === 'win32') {
      const result = getCommandOutput(`netstat -an | findstr :${port}`);
      console.log(`  Puerto ${port}: ${result ? '🟢 En uso' : '🔴 Libre'}`);
    } else {
      const result = getCommandOutput(`lsof -i :${port}`);
      console.log(`  Puerto ${port}: ${result ? '🟢 En uso' : '🔴 Libre'}`);
    }
  } catch (error) {
    console.log(`  Puerto ${port}: ❓ No se pudo verificar`);
  }
});

console.log('\n' + chalk.yellow('📝 Variables de entorno clave:'));
if (fs.existsSync('.env')) {
  const envContent = fs.readFileSync('.env', 'utf8');
  const hasDebug = envContent.includes('DEBUG=1') ? '✅' : '❌';
  const hasDatabaseUrl = envContent.includes('DATABASE_URL=') ? '✅' : '❌';
  const hasFirebase = envContent.includes('FIREBASE_API_KEY=') ? '✅' : '❌';
  const hasGoogleCloud = envContent.includes('GOOGLE_CLOUD_PROJECT=') ? '✅' : '❌';
  
  console.log(`  DEBUG configurado: ${hasDebug}`);
  console.log(`  DATABASE_URL configurado: ${hasDatabaseUrl}`);
  console.log(`  Firebase configurado: ${hasFirebase}`);
  console.log(`  Google Cloud configurado: ${hasGoogleCloud}`);
} else {
  console.log('  ❌ Archivo .env no existe');
}

console.log('\n' + chalk.yellow('🔍 Logs recientes:'));
try {
  const logs = getCommandOutput('docker-compose logs --tail=5 2>/dev/null');
  if (logs) {
    console.log('  Últimas 5 líneas de logs:');
    logs.split('\n').slice(-5).forEach(line => {
      console.log(`    ${line}`);
    });
  }
} catch (error) {
  console.log('  No se pudieron obtener los logs');
}

console.log('\n' + chalk.cyan('💡 Comandos útiles para debug:'));
console.log('  npm run logs           - Ver todos los logs');
console.log('  npm run health         - Verificar salud de servicios');
console.log('  npm run restart        - Reiniciar servicios');
console.log('  docker-compose ps      - Ver estado de contenedores');
console.log('  docker system df       - Ver uso de espacio Docker');
console.log('');