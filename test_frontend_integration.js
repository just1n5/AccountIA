#!/usr/bin/env node

/**
 * Script de Prueba - Integración Frontend-Backend AccountIA
 * 
 * Este script verifica que la configuración del frontend esté correcta
 * y que pueda conectarse exitosamente con el backend.
 */

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';

const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
};

const log = {
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
  warning: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
  info: (msg) => console.log(`${colors.blue}ℹ️  ${msg}${colors.reset}`),
  title: (msg) => console.log(`${colors.bold}${colors.blue}\n🔍 ${msg}${colors.reset}`)
};

async function testEndpoint(url, method = 'GET', body = null) {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    const data = await response.json();
    
    return {
      success: response.ok,
      status: response.status,
      data: data
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

async function checkEnvironmentVariables() {
  log.title('Verificando Variables de Entorno');
  
  const envPath = path.join(process.cwd(), '.env');
  
  if (!fs.existsSync(envPath)) {
    log.error('Archivo .env no encontrado');
    return false;
  }
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  const requiredVars = [
    'VITE_API_URL',
    'DEV_SKIP_AUTH_FOR_TESTING',
    'CORS_ALLOWED_ORIGINS'
  ];
  
  let allPresent = true;
  
  requiredVars.forEach(varName => {
    if (envContent.includes(`${varName}=`)) {
      log.success(`${varName} configurada`);
    } else {
      log.error(`${varName} no encontrada`);
      allPresent = false;
    }
  });
  
  // Verificar valores específicos
  if (envContent.includes('VITE_API_URL=http://localhost:8000/api/v1')) {
    log.success('VITE_API_URL apunta correctamente al backend');
  } else {
    log.warning('VITE_API_URL podría no estar configurada para desarrollo local');
  }
  
  if (envContent.includes('DEV_SKIP_AUTH_FOR_TESTING=1')) {
    log.success('Modo de desarrollo sin autenticación habilitado');
  }
  
  return allPresent;
}

async function checkBackendConnection() {
  log.title('Verificando Conexión con Backend');
  
  const baseUrl = 'http://localhost:8000';
  
  // Test 1: Health check
  log.info('Probando health check...');
  const healthCheck = await testEndpoint(`${baseUrl}/health/`);
  
  if (healthCheck.success) {
    log.success('Health check OK');
  } else {
    log.error(`Health check falló: ${healthCheck.error || healthCheck.status}`);
    return false;
  }
  
  // Test 2: API Schema
  log.info('Probando API schema...');
  const schemaCheck = await testEndpoint(`${baseUrl}/api/schema/`);
  
  if (schemaCheck.success) {
    log.success('API schema accesible');
  } else {
    log.warning('API schema no accesible (no crítico)');
  }
  
  // Test 3: Declarations endpoint
  log.info('Probando endpoint de declaraciones...');
  const declarationsCheck = await testEndpoint(`${baseUrl}/api/v1/declarations/`);
  
  if (declarationsCheck.success) {
    log.success(`Declaraciones endpoint OK - ${declarationsCheck.data.length || 0} declaraciones encontradas`);
    if (declarationsCheck.data.length > 0) {
      log.info(`Primera declaración: ID ${declarationsCheck.data[0].id}, año ${declarationsCheck.data[0].fiscal_year}`);
    }
  } else {
    log.error(`Declaraciones endpoint falló: ${declarationsCheck.error || declarationsCheck.status}`);
    return false;
  }
  
  // Test 4: Crear declaración de prueba
  log.info('Probando creación de declaración...');
  const createTest = await testEndpoint(`${baseUrl}/api/v1/declarations/`, 'POST', {
    fiscal_year: 2024
  });
  
  if (createTest.success) {
    log.success(`Declaración creada exitosamente: ID ${createTest.data.id}`);
  } else if (createTest.status === 400 && createTest.data.fiscal_year) {
    log.warning('Ya existe declaración para 2024 (esto es normal)');
  } else {
    log.error(`Error creando declaración: ${createTest.error || JSON.stringify(createTest.data)}`);
  }
  
  return true;
}

async function checkFrontendConfiguration() {
  log.title('Verificando Configuración del Frontend');
  
  // Verificar package.json
  const frontendPackagePath = path.join(process.cwd(), 'frontend', 'package.json');
  if (fs.existsSync(frontendPackagePath)) {
    log.success('package.json del frontend encontrado');
    
    const packageContent = JSON.parse(fs.readFileSync(frontendPackagePath, 'utf8'));
    
    // Verificar dependencias críticas
    const criticalDeps = ['react', 'typescript', 'vite', 'axios'];
    criticalDeps.forEach(dep => {
      if (packageContent.dependencies?.[dep] || packageContent.devDependencies?.[dep]) {
        log.success(`Dependencia ${dep} presente`);
      } else {
        log.warning(`Dependencia ${dep} no encontrada`);
      }
    });
  }
  
  // Verificar vite.config.js
  const viteConfigPath = path.join(process.cwd(), 'frontend', 'vite.config.js');
  if (fs.existsSync(viteConfigPath)) {
    log.success('vite.config.js encontrado');
    
    const viteContent = fs.readFileSync(viteConfigPath, 'utf8');
    if (viteContent.includes('http://localhost:8000')) {
      log.success('Proxy de Vite configurado para desarrollo local');
    } else if (viteContent.includes('http://backend:8000')) {
      log.warning('Proxy de Vite configurado para Docker (debería ser localhost para desarrollo)');
    }
  }
  
  // Verificar servicios del frontend
  const servicesPath = path.join(process.cwd(), 'frontend', 'src', 'services');
  if (fs.existsSync(servicesPath)) {
    log.success('Directorio de servicios encontrado');
    
    const services = ['api.ts', 'authService.ts', 'declarationService.ts'];
    services.forEach(service => {
      const servicePath = path.join(servicesPath, service);
      if (fs.existsSync(servicePath)) {
        log.success(`Servicio ${service} presente`);
      } else {
        log.error(`Servicio ${service} no encontrado`);
      }
    });
  }
  
  return true;
}

async function main() {
  console.log(`${colors.bold}${colors.blue}
🚀 AccountIA - Verificación de Integración Frontend-Backend
===========================================================
${colors.reset}`);
  
  let allChecksPass = true;
  
  // Verificar variables de entorno
  if (!await checkEnvironmentVariables()) {
    allChecksPass = false;
  }
  
  // Verificar conexión con backend
  if (!await checkBackendConnection()) {
    allChecksPass = false;
  }
  
  // Verificar configuración del frontend
  if (!await checkFrontendConfiguration()) {
    allChecksPass = false;
  }
  
  // Resumen final
  console.log(`\n${colors.bold}📋 RESUMEN DE VERIFICACIÓN${colors.reset}\n`);
  
  if (allChecksPass) {
    log.success('Todas las verificaciones pasaron exitosamente');
    log.info('Tu frontend está listo para conectarse al backend');
    
    console.log(`\n${colors.bold}🎯 PRÓXIMOS PASOS:${colors.reset}`);
    console.log('1. Ejecutar el backend: npm run backend');
    console.log('2. Ejecutar el frontend: npm run frontend');
    console.log('3. Abrir http://localhost:3000');
    
  } else {
    log.error('Algunas verificaciones fallaron');
    log.warning('Revisa los problemas indicados arriba antes de continuar');
  }
  
  console.log(`\n${colors.blue}Para más ayuda, consulta el README.md del proyecto${colors.reset}\n`);
}

// Ejecutar solo si es llamado directamente
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { main as testIntegration };
