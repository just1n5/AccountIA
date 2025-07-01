#!/usr/bin/env python3
"""
Script de Implementación - Testing Frontend AccountIA
Automatiza la configuración inicial del sistema de pruebas frontend

Este script:
1. Configura herramientas de testing (Jest, Cypress)
2. Crea estructura de carpetas para pruebas
3. Instala dependencias necesarias
4. Genera archivos de configuración
5. Crea templates de prueba iniciales
"""

import os
import json
from pathlib import Path

class FrontendTestingSetup:
    """Configurador de pruebas frontend para AccountIA"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.frontend_path = self.project_root / "frontend"
        self.test_config = {
            "jest": {
                "testEnvironment": "jsdom",
                "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
                "moduleNameMapping": {
                    "^@/(.*)$": "<rootDir>/src/$1"
                },
                "collectCoverageFrom": [
                    "src/**/*.{js,jsx,ts,tsx}",
                    "!src/index.js",
                    "!src/reportWebVitals.js"
                ],
                "coverageThreshold": {
                    "global": {
                        "branches": 80,
                        "functions": 80,
                        "lines": 80,
                        "statements": 80
                    }
                }
            },
            "cypress": {
                "e2e": {
                    "baseUrl": "http://localhost:3000",
                    "supportFile": "cypress/support/e2e.js",
                    "specPattern": "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
                    "video": True,
                    "screenshotOnRunFailure": True,
                    "viewportWidth": 1280,
                    "viewportHeight": 720
                }
            }
        }
    
    def run_setup(self):
        """Ejecuta configuración completa de testing"""
        print("🚀 CONFIGURANDO TESTING FRONTEND ACCOUNTIA")
        print("=" * 60)
        
        try:
            # Paso 1: Verificar estructura
            self.verify_project_structure()
            
            # Paso 2: Configurar Jest
            self.setup_jest()
            
            # Paso 3: Configurar Cypress  
            self.setup_cypress()
            
            # Paso 4: Crear estructura de carpetas
            self.create_test_directories()
            
            # Paso 5: Generar archivos de prueba template
            self.create_test_templates()
            
            # Paso 6: Configurar scripts NPM
            self.update_package_scripts()
            
            # Paso 7: Crear archivos de configuración
            self.create_config_files()
            
            print("\n🎉 ¡CONFIGURACIÓN COMPLETADA CON ÉXITO!")
            self.print_next_steps()
            
        except Exception as e:
            print(f"\n❌ Error durante configuración: {str(e)}")
            return False
        
        return True
    
    def verify_project_structure(self):
        """Verifica que existe la estructura del proyecto"""
        print("\n📋 1. Verificando estructura del proyecto...")
        
        if not self.frontend_path.exists():
            raise Exception(f"No se encontró la carpeta frontend en {self.frontend_path}")
        
        package_json = self.frontend_path / "package.json"
        if not package_json.exists():
            raise Exception("No se encontró package.json en el frontend")
        
        print("✅ Estructura del proyecto verificada")
    
    def setup_jest(self):
        """Configura Jest para pruebas unitarias"""
        print("\n🧪 2. Configurando Jest...")
        
        # Leer package.json actual
        package_json_path = self.frontend_path / "package.json"
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # Agregar configuración de Jest
        package_data["jest"] = self.test_config["jest"]
        
        # Agregar dependencias de testing si no existen
        dev_deps = package_data.setdefault("devDependencies", {})
        testing_deps = {
            "@testing-library/jest-dom": "^5.16.5",
            "@testing-library/react": "^13.4.0", 
            "@testing-library/user-event": "^14.4.3",
            "jest-environment-jsdom": "^29.0.0"
        }
        
        for dep, version in testing_deps.items():
            if dep not in dev_deps:
                dev_deps[dep] = version
        
        # Guardar package.json actualizado
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Jest configurado correctamente")
    
    def setup_cypress(self):
        """Configura Cypress para pruebas E2E"""
        print("\n🎯 3. Configurando Cypress...")
        
        # Crear archivo de configuración de Cypress
        cypress_config = {
            "e2e": self.test_config["cypress"]["e2e"],
            "component": {
                "devServer": {
                    "framework": "create-react-app",
                    "bundler": "webpack"
                }
            }
        }
        
        cypress_config_path = self.frontend_path / "cypress.config.js"
        with open(cypress_config_path, 'w', encoding='utf-8') as f:
            f.write(f"""
import {{ defineConfig }} from 'cypress'

export default defineConfig({json.dumps(cypress_config, indent=2)})
""")
        
        # Agregar Cypress a devDependencies
        package_json_path = self.frontend_path / "package.json"
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        dev_deps = package_data.setdefault("devDependencies", {})
        cypress_deps = {
            "cypress": "^13.0.0",
            "@cypress/react": "^8.0.0"
        }
        
        for dep, version in cypress_deps.items():
            if dep not in dev_deps:
                dev_deps[dep] = version
        
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Cypress configurado correctamente")
    
    def create_test_directories(self):
        """Crea estructura de carpetas para pruebas"""
        print("\n📁 4. Creando estructura de carpetas...")
        
        directories = [
            # Jest/Unit tests
            "src/__tests__",
            "src/__tests__/components", 
            "src/__tests__/hooks",
            "src/__tests__/utils",
            "src/__tests__/services",
            
            # Cypress E2E
            "cypress",
            "cypress/e2e",
            "cypress/fixtures",
            "cypress/support",
            
            # Test utilities
            "src/test-utils",
            "src/__mocks__"
        ]
        
        for directory in directories:
            dir_path = self.frontend_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  📂 {directory}")
        
        print("✅ Estructura de carpetas creada")
    
    def create_test_templates(self):
        """Crea archivos template de pruebas"""
        print("\n📝 5. Creando templates de prueba...")
        
        # setupTests.js
        setup_tests_content = '''
import '@testing-library/jest-dom';

// Mock de APIs globales
global.fetch = jest.fn();

// Mock de window.fs para testing
Object.defineProperty(window, 'fs', {
  value: {
    readFile: jest.fn()
  },
  writable: true
});

// Configuración global de testing
beforeEach(() => {
  jest.clearAllMocks();
});
'''
        
        with open(self.frontend_path / "src/setupTests.js", 'w') as f:
            f.write(setup_tests_content)
        
        # Template de prueba unitaria
        unit_test_template = '''
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FiscalAnalysisDashboard } from '../FiscalAnalysisDashboard';

// Mock de datos de prueba
const mockAnalysisData = {
  success: true,
  base_gravable: 45000000,
  impuesto_calculado: 8500000,
  saldo_a_favor: 2500000,
  recommendations: [
    {
      tipo: 'Dependientes',
      ahorro_estimado: 500000,
      urgencia: 'ALTA'
    }
  ]
};

describe('FiscalAnalysisDashboard', () => {
  test('muestra resumen ejecutivo correctamente', () => {
    render(<FiscalAnalysisDashboard data={mockAnalysisData} />);
    
    expect(screen.getByText(/base gravable/i)).toBeInTheDocument();
    expect(screen.getByText('$45.000.000')).toBeInTheDocument();
  });
  
  test('maneja estado de carga', () => {
    render(<FiscalAnalysisDashboard loading={true} />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByText(/analizando/i)).toBeInTheDocument();
  });
  
  test('muestra recomendaciones de optimización', () => {
    render(<FiscalAnalysisDashboard data={mockAnalysisData} />);
    
    expect(screen.getByText('Dependientes')).toBeInTheDocument();
    expect(screen.getByText('$500.000')).toBeInTheDocument();
  });
});
'''
        
        with open(self.frontend_path / "src/__tests__/components/FiscalAnalysisDashboard.test.jsx", 'w') as f:
            f.write(unit_test_template)
        
        # Template de prueba E2E
        e2e_test_template = '''
describe('Flujo Principal - Análisis Fiscal', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('completa flujo de análisis fiscal exitosamente', () => {
    // 1. Landing page y navegación
    cy.contains('Empezar Gratis').click();
    
    // 2. Registro/Login (mock)
    cy.url().should('include', '/dashboard');
    
    // 3. Carga de archivo
    cy.get('[data-testid="file-upload"]').should('be.visible');
    cy.fixture('exogena-demo.xlsx').then(fileContent => {
      cy.get('input[type="file"]').selectFile({
        contents: fileContent,
        fileName: 'exogena-demo.xlsx'
      });
    });
    
    // 4. Verificar procesamiento
    cy.contains('Procesando').should('be.visible');
    cy.contains('Análisis completado', { timeout: 30000 }).should('be.visible');
    
    // 5. Verificar resultados
    cy.get('[data-testid="base-gravable"]').should('contain', '$');
    cy.get('[data-testid="recommendations"]').should('be.visible');
    
    // 6. Verificar que puede proceder
    cy.contains('Continuar').should('be.enabled');
  });

  it('maneja errores de archivo inválido', () => {
    cy.get('[data-testid="file-upload"]').should('be.visible');
    
    // Cargar archivo inválido
    cy.fixture('invalid-file.txt').then(fileContent => {
      cy.get('input[type="file"]').selectFile({
        contents: fileContent,
        fileName: 'invalid-file.txt'
      });
    });
    
    // Verificar mensaje de error
    cy.contains('Formato de archivo no válido').should('be.visible');
    cy.get('[data-testid="error-message"]').should('contain', 'Excel');
  });
});
'''
        
        with open(self.frontend_path / "cypress/e2e/fiscal-analysis-flow.cy.js", 'w') as f:
            f.write(e2e_test_template)
        
        # Cypress support file
        cypress_support = '''
import './commands';

// Configuración global de Cypress
Cypress.on('uncaught:exception', (err, runnable) => {
  // Evitar que Cypress falle en errores no relacionados con nuestro código
  return false;
});

// Comandos personalizados para AccountIA
Cypress.Commands.add('loginAsUser', (email = 'test@accountia.com') => {
  cy.window().then((win) => {
    win.localStorage.setItem('authToken', 'mock-jwt-token');
    win.localStorage.setItem('user', JSON.stringify({
      email: email,
      name: 'Usuario de Prueba'
    }));
  });
});

Cypress.Commands.add('uploadExogenaFile', (filename = 'exogena-demo.xlsx') => {
  cy.fixture(filename).then(fileContent => {
    cy.get('input[type="file"]').selectFile({
      contents: fileContent,
      fileName: filename
    });
  });
});
'''
        
        with open(self.frontend_path / "cypress/support/e2e.js", 'w') as f:
            f.write(cypress_support)
        
        print("✅ Templates de prueba creados")
    
    def update_package_scripts(self):
        """Actualiza scripts NPM para testing"""
        print("\n⚙️ 6. Configurando scripts NPM...")
        
        package_json_path = self.frontend_path / "package.json"
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # Agregar scripts de testing
        scripts = package_data.setdefault("scripts", {})
        testing_scripts = {
            "test": "react-scripts test --watchAll=false",
            "test:watch": "react-scripts test",
            "test:coverage": "react-scripts test --coverage --watchAll=false",
            "test:ci": "CI=true react-scripts test --coverage --watchAll=false",
            "cy:open": "cypress open",
            "cy:run": "cypress run",
            "test:e2e": "cypress run",
            "test:all": "npm run test:ci && npm run test:e2e",
            "test:unit": "npm run test:coverage"
        }
        
        for script, command in testing_scripts.items():
            scripts[script] = command
        
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Scripts NPM configurados")
    
    def create_config_files(self):
        """Crea archivos de configuración adicionales"""
        print("\n🔧 7. Creando archivos de configuración...")
        
        # .eslintrc para testing
        eslint_config = {
            "env": {
                "jest": True,
                "cypress/globals": True
            },
            "plugins": ["cypress"],
            "extends": [
                "plugin:cypress/recommended",
                "plugin:testing-library/react"
            ]
        }
        
        with open(self.frontend_path / ".eslintrc.testing.json", 'w') as f:
            json.dump(eslint_config, f, indent=2)
        
        # GitHub Actions workflow para testing
        github_workflow = '''
name: Frontend Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: frontend
      run: npm ci
    
    - name: Run unit tests
      working-directory: frontend
      run: npm run test:ci
    
    - name: Run E2E tests
      working-directory: frontend
      run: npm run cy:run
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: frontend/coverage/lcov.info
'''
        
        github_dir = self.project_root / ".github/workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        with open(github_dir / "frontend-testing.yml", 'w') as f:
            f.write(github_workflow)
        
        print("✅ Archivos de configuración creados")
    
    def print_next_steps(self):
        """Imprime próximos pasos para el desarrollador"""
        print("\n🚀 PRÓXIMOS PASOS:")
        print("-" * 40)
        print("1. Instalar dependencias:")
        print("   cd frontend && npm install")
        print()
        print("2. Ejecutar pruebas unitarias:")
        print("   npm run test")
        print()
        print("3. Abrir Cypress (E2E):")
        print("   npm run cy:open")
        print()
        print("4. Crear componentes con sus pruebas:")
        print("   - FiscalAnalysisDashboard.jsx + test")
        print("   - IntelligentFileUpload.jsx + test")
        print("   - OptimizationAssistant.jsx + test")
        print()
        print("5. Verificar cobertura:")
        print("   npm run test:coverage")
        print()
        print("📋 Archivos importantes creados:")
        print("   ✅ cypress.config.js")
        print("   ✅ src/setupTests.js")
        print("   ✅ Templates de prueba en src/__tests__/")
        print("   ✅ Scripts NPM actualizados")
        print("   ✅ Configuración GitHub Actions")
        print()
        print("🎯 OBJETIVO: Alcanzar >80% cobertura en 2 semanas")
        print("💡 TIP: Escribir pruebas ANTES de implementar componentes (TDD)")


if __name__ == "__main__":
    print("🧪 ACCOUNTIA - CONFIGURADOR DE TESTING FRONTEND")
    print("Automatiza la configuración completa del sistema de pruebas")
    print()
    
    # Detectar ruta del proyecto
    current_dir = Path(__file__).parent
    
    try:
        configurator = FrontendTestingSetup(current_dir)
        success = configurator.run_setup()
        
        if success:
            print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
            print("El sistema de pruebas frontend está listo para usar")
        else:
            print("\n❌ Configuración incompleta")
            print("Revisa los errores reportados arriba")
            
    except KeyboardInterrupt:
        print("\n⚠️ Configuración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
