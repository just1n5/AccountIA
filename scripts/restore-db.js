#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

// Obtener el archivo de backup desde argumentos
const backupFile = process.argv[2];

if (!backupFile) {
  console.log(chalk.red('❌ Por favor especifica un archivo de backup'));
  console.log(chalk.yellow('Uso: npm run db:restore -- <archivo_backup.sql>'));
  console.log('');
  
  // Mostrar backups disponibles
  const backupDir = 'backups';
  if (fs.existsSync(backupDir)) {
    console.log(chalk.cyan('📁 Backups disponibles:'));
    const backupFiles = fs.readdirSync(backupDir)
      .filter(file => file.endsWith('.sql'))
      .sort()
      .reverse();
    
    backupFiles.slice(0, 10).forEach(file => {
      const filePath = path.join(backupDir, file);
      const stats = fs.statSync(filePath);
      const size = (stats.size / 1024 / 1024).toFixed(2);
      const date = new Date(stats.mtime).toLocaleString();
      console.log(`   ${file} - ${size} MB - ${date}`);
    });
    
    if (backupFiles.length === 0) {
      console.log('   No hay backups disponibles');
      console.log('   Ejecuta: npm run db:backup');
    }
  }
  process.exit(1);
}

// Buscar el archivo de backup
let backupPath;
if (fs.existsSync(backupFile)) {
  backupPath = backupFile;
} else if (fs.existsSync(path.join('backups', backupFile))) {
  backupPath = path.join('backups', backupFile);
} else {
  console.error(chalk.red(`❌ Archivo de backup no encontrado: ${backupFile}`));
  process.exit(1);
}

console.log(chalk.blue.bold('📥 AccountIA - Restaurar Base de Datos\n'));

console.log(chalk.yellow('⚠️  ADVERTENCIA: Esta operación sobrescribirá todos los datos actuales'));
console.log(`   Archivo a restaurar: ${backupPath}`);

// Verificar el tamaño del archivo
const stats = fs.statSync(backupPath);
const fileSizeInMB = (stats.size / 1024 / 1024).toFixed(2);
console.log(`   Tamaño del backup: ${fileSizeInMB} MB`);

console.log('\nPresiona Ctrl+C para cancelar o Enter para continuar...');
process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', function(key) {
  if (key[0] === 3) { // Ctrl+C
    console.log('\n' + chalk.yellow('Operación cancelada'));
    process.exit(0);
  } else if (key[0] === 13) { // Enter
    console.log('');
    restoreDatabase();
  }
});

function restoreDatabase() {
  process.stdin.setRawMode(false);
  process.stdin.pause();
  
  try {
    console.log(chalk.cyan('ℹ️  Verificando estado de la base de datos...'));
    
    // Verificar que PostgreSQL esté ejecutándose
    execSync('docker-compose exec accountia_postgres pg_isready -U accountia_user', { stdio: 'ignore' });
    
    console.log(chalk.cyan('ℹ️  Limpiando base de datos actual...'));
    
    // Limpiar la base de datos actual
    const dropCommand = `docker-compose exec -T accountia_postgres psql -U accountia_user -d accountia_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"`;
    execSync(dropCommand, { stdio: 'ignore' });
    
    console.log(chalk.cyan('ℹ️  Restaurando backup...'));
    
    // Restaurar el backup
    const restoreCommand = `docker-compose exec -T accountia_postgres psql -U accountia_user -d accountia_dev`;
    const backupData = fs.readFileSync(backupPath, 'utf8');
    
    const child = require('child_process').spawn('docker-compose', [
      'exec', '-T', 'accountia_postgres', 
      'psql', '-U', 'accountia_user', '-d', 'accountia_dev'
    ], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    child.stdin.write(backupData);
    child.stdin.end();
    
    child.on('close', (code) => {
      if (code === 0) {
        console.log(chalk.green('✅ Base de datos restaurada exitosamente!'));
        
        console.log('\n' + chalk.cyan('🔄 Ejecutando migraciones post-restauración...'));
        try {
          execSync('docker-compose exec accountia_backend python manage.py migrate --noinput', { stdio: 'inherit' });
          console.log(chalk.green('✅ Migraciones completadas'));
        } catch (error) {
          console.log(chalk.yellow('⚠️  Algunas migraciones fallaron, pero la restauración fue exitosa'));
        }
        
        console.log('\n' + chalk.cyan('💡 Próximos pasos:'));
        console.log('• Reinicia los servicios: npm run restart');
        console.log('• Verifica el estado: npm run health');
        console.log('• Crea un nuevo superusuario si es necesario: npm run user:create');
        
      } else {
        console.error(chalk.red('❌ Error durante la restauración'));
        process.exit(1);
      }
    });
    
  } catch (error) {
    console.error(chalk.red('❌ Error restaurando el backup:'));
    console.error(error.message);
    
    console.log('\n' + chalk.yellow('🔍 Posibles causas:'));
    console.log('• El contenedor de PostgreSQL no está ejecutándose');
    console.log('• El archivo de backup está corrupto');
    console.log('• No hay suficiente espacio en disco');
    
    console.log('\n' + chalk.cyan('💡 Soluciones:'));
    console.log('• npm run dev     - Asegurar que los servicios estén corriendo');
    console.log('• npm run health  - Verificar estado de servicios');
    
    process.exit(1);
  }
}

console.log('');