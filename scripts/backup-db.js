#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

// Crear directorio de backups si no existe
const backupDir = 'backups';
if (!fs.existsSync(backupDir)) {
  fs.mkdirSync(backupDir, { recursive: true });
}

// Generar nombre de archivo con timestamp
const timestamp = new Date().toISOString()
  .replace(/[:.]/g, '-')
  .replace('T', '_')
  .substring(0, 19);

const backupFile = `accountia_backup_${timestamp}.sql`;
const backupPath = path.join(backupDir, backupFile);

console.log(chalk.blue.bold('💾 AccountIA - Backup de Base de Datos\n'));

console.log(chalk.cyan('ℹ️  Creando backup de la base de datos...'));
console.log(`   Archivo: ${backupPath}`);

try {
  // Verificar que el contenedor de PostgreSQL esté ejecutándose
  execSync('docker-compose exec accountia_postgres pg_isready -U accountia_user', { stdio: 'ignore' });
  
  // Crear el backup
  const backupCommand = `docker-compose exec -T accountia_postgres pg_dump -U accountia_user -d accountia_dev`;
  const backupData = execSync(backupCommand, { encoding: 'utf8' });
  
  // Guardar el backup
  fs.writeFileSync(backupPath, backupData);
  
  // Obtener el tamaño del archivo
  const stats = fs.statSync(backupPath);
  const fileSizeInMB = (stats.size / 1024 / 1024).toFixed(2);
  
  console.log(chalk.green('✅ Backup creado exitosamente!'));
  console.log(`   Tamaño: ${fileSizeInMB} MB`);
  console.log(`   Ubicación: ${backupPath}`);
  
  // Listar backups existentes
  console.log('\n' + chalk.yellow('📁 Backups existentes:'));
  const backupFiles = fs.readdirSync(backupDir)
    .filter(file => file.endsWith('.sql'))
    .sort()
    .reverse();
  
  backupFiles.slice(0, 5).forEach((file, index) => {
    const filePath = path.join(backupDir, file);
    const fileStats = fs.statSync(filePath);
    const size = (fileStats.size / 1024 / 1024).toFixed(2);
    const date = new Date(fileStats.mtime).toLocaleString();
    const isNew = index === 0 ? chalk.green(' (nuevo)') : '';
    console.log(`   ${file} - ${size} MB - ${date}${isNew}`);
  });
  
  if (backupFiles.length > 5) {
    console.log(`   ... y ${backupFiles.length - 5} backups más`);
  }
  
  console.log('\n' + chalk.cyan('💡 Para restaurar un backup:'));
  console.log(`   npm run db:restore -- ${backupFile}`);
  
} catch (error) {
  console.error(chalk.red('❌ Error creando el backup:'));
  console.error(error.message);
  
  console.log('\n' + chalk.yellow('🔍 Posibles causas:'));
  console.log('• El contenedor de PostgreSQL no está ejecutándose');
  console.log('• No hay conexión a la base de datos');
  console.log('• Permisos insuficientes');
  
  console.log('\n' + chalk.cyan('💡 Soluciones:'));
  console.log('• npm run dev          - Iniciar servicios');
  console.log('• npm run health       - Verificar estado');
  console.log('• npm run logs:backend - Ver logs del backend');
  
  process.exit(1);
}

console.log('');