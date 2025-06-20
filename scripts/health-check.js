#!/usr/bin/env node

const { execSync } = require('child_process');
const chalk = require('chalk');

function checkService(name, url, timeout = 5000) {
  return new Promise((resolve) => {
    try {
      const startTime = Date.now();
      execSync(`curl -f --max-time 5 ${url}`, { stdio: 'ignore' });
      const responseTime = Date.now() - startTime;
      resolve({ 
        name, 
        status: 'healthy', 
        responseTime: `${responseTime}ms`,
        url 
      });
    } catch (error) {
      resolve({ 
        name, 
        status: 'unhealthy', 
        error: error.message,
        url 
      });
    }
  });
}

async function checkDockerServices() {
  try {
    const output = execSync('docker-compose ps --format json', { encoding: 'utf8' });
    const services = output.trim().split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
    
    return services.map(service => ({
      name: service.Service,
      status: service.State,
      ports: service.Publishers ? service.Publishers.map(p => `${p.PublishedPort}:${p.TargetPort}`).join(', ') : 'No ports',
      health: service.Health || 'N/A'
    }));
  } catch (error) {
    return [];
  }
}

async function main() {
  console.log(chalk.blue.bold('🏥 AccountIA - Health Check\n'));

  // Verificar servicios Docker
  console.log(chalk.yellow('📦 Docker Services:'));
  const dockerServices = await checkDockerServices();
  
  if (dockerServices.length === 0) {
    console.log(chalk.red('❌ No se pudieron obtener los servicios Docker'));
    console.log(chalk.yellow('💡 Ejecuta: npm run dev'));
    return;
  }

  dockerServices.forEach(service => {
    const statusColor = service.status === 'running' ? 'green' : 'red';
    const statusIcon = service.status === 'running' ? '✅' : '❌';
    console.log(`  ${statusIcon} ${chalk[statusColor](service.name.padEnd(20))} ${service.status.padEnd(10)} ${service.ports}`);
  });

  console.log('\n' + chalk.yellow('🔄 Background Services:'));
  
  // Verificar Redis
  try {
    execSync('docker-compose exec -T accountia_redis redis-cli ping', { stdio: 'ignore' });
    console.log(`  ✅ ${chalk.green('Redis'.padEnd(20))} healthy`);
  } catch (error) {
    console.log(`  ❌ ${chalk.red('Redis'.padEnd(20))} unhealthy`);
  }
  
  // Verificar Celery Worker
  try {
    const output = execSync('docker-compose exec -T accountia_celery_worker celery -A config inspect active', { encoding: 'utf8', timeout: 5000 });
    if (output.includes('OK') || output.includes('active')) {
      console.log(`  ✅ ${chalk.green('Celery Worker'.padEnd(20))} healthy`);
    } else {
      console.log(`  ⚠️ ${chalk.yellow('Celery Worker'.padEnd(20))} no active tasks`);
    }
  } catch (error) {
    console.log(`  ❌ ${chalk.red('Celery Worker'.padEnd(20))} unhealthy`);
  }

  console.log('\n' + chalk.yellow('🌐 HTTP Services:'));

  // Verificar endpoints HTTP
  const httpChecks = [
    { name: 'Frontend', url: 'http://localhost:3000' },
    { name: 'Backend API', url: 'http://localhost:8000/health/' },
    { name: 'Django Admin', url: 'http://localhost:8000/admin/' },
    { name: 'API Docs', url: 'http://localhost:8000/api/docs/' },
    { name: 'PgAdmin', url: 'http://localhost:5050' },
    { name: 'MailHog', url: 'http://localhost:8025' }
  ];

  const results = await Promise.all(
    httpChecks.map(check => checkService(check.name, check.url))
  );

  results.forEach(result => {
    const statusColor = result.status === 'healthy' ? 'green' : 'red';
    const statusIcon = result.status === 'healthy' ? '✅' : '❌';
    const responseTime = result.responseTime ? `(${result.responseTime})` : '';
    console.log(`  ${statusIcon} ${chalk[statusColor](result.name.padEnd(20))} ${result.status.padEnd(10)} ${responseTime}`);
    if (result.status === 'unhealthy') {
      console.log(`      ${chalk.gray('URL: ' + result.url)}`);
    }
  });

  // Resumen
  const healthyServices = results.filter(r => r.status === 'healthy').length;
  const totalServices = results.length;
  
  console.log('\n' + chalk.yellow('📊 Resumen:'));
  if (healthyServices === totalServices) {
    console.log(chalk.green(`✅ Todos los servicios están funcionando (${healthyServices}/${totalServices})`));
  } else {
    console.log(chalk.red(`❌ ${totalServices - healthyServices} servicios tienen problemas`));
    console.log(chalk.yellow('💡 Ejecuta: npm run logs para ver los errores'));
  }

  // Sugerencias
  if (healthyServices < totalServices) {
    console.log('\n' + chalk.yellow('🔧 Posibles soluciones:'));
    console.log('• npm run restart  - Reiniciar servicios');
    console.log('• npm run logs     - Ver logs para diagnosticar');
    console.log('• npm run debug    - Información detallada del sistema');
  }
  
  // Comandos útiles adicionales
  console.log('\n' + chalk.blue('🛠️ Comandos útiles:'));
  console.log('• npm run celery:test     - Probar Celery y Redis');
  console.log('• npm run gcs:test        - Verificar Google Cloud Storage');
  console.log('• npm run celery:worker   - Ver logs del worker');
  console.log('• npm run redis:cli       - Acceder a Redis CLI');

  console.log('');
}

main().catch(console.error);