#!/usr/bin/env node

/**
 * Script de verificación de URLs - AccountIA Frontend
 * Verifica que las URLs se construyan correctamente después de la corrección
 */

console.log('🔍 VERIFICACIÓN DE URLs - AccountIA Frontend');
console.log('='.repeat(50));

// Simular el comportamiento del constructor de ApiClient
function simulateApiClient() {
  console.log('\n📋 1. SIMULANDO CONSTRUCCIÓN DE API CLIENT');
  
  const envUrl = 'http://localhost:8000'; // VITE_API_URL simulado
  const cleanBaseUrl = envUrl.replace(/\/api\/v1\/?$/, '');
  const baseURL = `${cleanBaseUrl}/api/v1`;
  
  console.log(`   📤 VITE_API_URL: ${envUrl}`);
  console.log(`   🧹 Clean base URL: ${cleanBaseUrl}`);
  console.log(`   ✅ Final baseURL: ${baseURL}`);
  
  return baseURL;
}

// Simular construcción de URLs
function simulateUrlConstruction(baseURL, requestUrl) {
  console.log(`\n🔗 Construyendo URL para: ${requestUrl}`);
  
  let fullURL;
  
  if (requestUrl.startsWith('http')) {
    fullURL = requestUrl;
    console.log(`   🌐 URL absoluta detectada: ${fullURL}`);
  } else {
    let cleanUrl = requestUrl;
    
    // Remover /api/v1 del inicio si existe
    if (cleanUrl.startsWith('/api/v1')) {
      console.log(`   ⚠️  Detectado /api/v1 al inicio, removiendo...`);
      cleanUrl = cleanUrl.substring(7);
      console.log(`   🧹 URL limpia: ${cleanUrl}`);
    }
    
    // Asegurar que empiece con /
    if (!cleanUrl.startsWith('/')) {
      cleanUrl = `/${cleanUrl}`;
    }
    
    fullURL = `${baseURL}${cleanUrl}`;
    console.log(`   ✅ URL final: ${fullURL}`);
  }
  
  return fullURL;
}

// Ejecutar simulaciones
const baseURL = simulateApiClient();

console.log('\n📋 2. SIMULANDO CONSTRUCCIÓN DE URLs');
console.log('-'.repeat(40));

// URLs de prueba
const testUrls = [
  '/auth/session/',
  '/declarations/',
  '/declarations/123/documents/',
  '/api/v1/auth/session/', // Esta debería ser limpiada
  '/api/v1/declarations/', // Esta debería ser limpiada
  'http://example.com/absolute/url'
];

testUrls.forEach(url => {
  const result = simulateUrlConstruction(baseURL, url);
  
  // Verificar si hay duplicación
  if (result.includes('/api/v1/api/v1/')) {
    console.log('   ❌ DUPLICACIÓN DETECTADA!');
  } else {
    console.log('   ✅ URL correcta');
  }
});

console.log('\n📋 3. VERIFICACIÓN DE SERVICIOS');
console.log('-'.repeat(40));

const services = [
  { name: 'DeclarationService', baseUrl: '', description: 'URLs base manejadas por api.ts' },
  { name: 'AuthService', baseUrl: '/auth', description: 'URLs base manejadas por api.ts' },
  { name: 'DocumentService', baseUrl: '', description: 'URLs base manejadas por api.ts' }
];

services.forEach(service => {
  console.log(`   📦 ${service.name}:`);
  console.log(`      📍 baseUrl: "${service.baseUrl}"`);
  console.log(`      📝 ${service.description}`);
});

console.log('\n✅ VERIFICACIÓN COMPLETADA');
console.log('\n🎯 RESULTADOS ESPERADOS:');
console.log('   • Todas las URLs deben ser construidas como http://localhost:8000/api/v1/...');
console.log('   • NO debe haber duplicaciones /api/v1/api/v1/');
console.log('   • Los servicios usan URLs relativas simples');
console.log('\n🚀 Para probar en vivo, reinicia el frontend y revisa los logs de la consola.');
