"""
Validador de Consistencia - Valida que los datos cumplan reglas fiscales
Verifica límites de deducciones, coherencia entre cédulas y cumplimiento normativo.
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """
    Valida que los datos cumplan reglas fiscales:
    - Límites de deducciones
    - Coherencia entre cédulas  
    - Verificación de topes legales
    - Consistencia con normativa tributaria
    """
    
    def __init__(self):
        # Valores UVT 2024
        self.UVT_2024 = 47065
        
        # Límites legales según Estatuto Tributario
        self.LEGAL_LIMITS = {
            # Límites de deducciones
            'deduccion_dependientes_max': 32 * self.UVT_2024,  # Art. 387 E.T.
            'deduccion_salud_max': 16 * self.UVT_2024,  # Art. 387 E.T.
            'deduccion_educacion_max': None,  # Sin límite específico
            'deduccion_vivienda_max': 1200 * self.UVT_2024,  # Art. 119 E.T.
            'deduccion_afc_max': 2800 * self.UVT_2024,  # Art. 126-4 E.T.
            
            # Renta exenta de trabajo
            'renta_exenta_trabajo_max': 240 * self.UVT_2024,  # Art. 206 E.T.
            'renta_exenta_trabajo_percentage': 0.25,  # 25% de ingresos laborales
            
            # Límites para declarar
            'patrimonio_bruto_limite': 154 * self.UVT_2024,  # Art. 594-1 E.T.
            'ingresos_brutos_limite': 47 * self.UVT_2024,  # Art. 594-1 E.T.
            
            # Límites de retención
            'retencion_trabajo_min': 4 * self.UVT_2024,  # Art. 383 E.T.
            'retencion_honorarios_rate': 0.10,  # 10% para honorarios
            'retencion_intereses_rate': 0.07,  # 7% para intereses
            
            # Límites de aportes voluntarios
            'aporte_voluntario_pension_max_percentage': 0.30,  # 30% del ingreso
            'aporte_voluntario_pension_max_uvt': 4500 * self.UVT_2024,  # 4500 UVT
        }
        
        # Rangos de tarifa normal (para validaciones)
        self.TARIFA_RANGES = [
            (0, 1090 * self.UVT_2024, 0.00),
            (1090 * self.UVT_2024, 1700 * self.UVT_2024, 0.19),
            (1700 * self.UVT_2024, 4100 * self.UVT_2024, 0.28),
            (4100 * self.UVT_2024, 8670 * self.UVT_2024, 0.33),
            (8670 * self.UVT_2024, 18970 * self.UVT_2024, 0.35),
            (18970 * self.UVT_2024, float('inf'), 0.37),
        ]
        
        # Códigos de concepto válidos según DIAN
        self.VALID_CONCEPT_CODES = {
            # Rentas de trabajo
            '5001': 'Salarios y demás pagos laborales',
            '5002': 'Honorarios y servicios',
            '5003': 'Servicios de transporte',
            '5004': 'Comisiones',
            '5005': 'Pagos por arrendamiento',
            
            # Rentas de capital
            '1001': 'Rendimientos financieros',
            '1002': 'Dividendos y participaciones',
            '1003': 'Intereses',
            '1004': 'Arrendamientos',
            
            # Otros
            '2001': 'Enajenación de activos fijos',
            '2002': 'Otros ingresos',
        }
    
    def validate_data_consistency(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida la consistencia completa de los datos fiscales
        
        Args:
            analysis_result: Resultado del análisis fiscal
            
        Returns:
            Dict con validaciones y recomendaciones de corrección
        """
        try:
            logger.info("Iniciando validación de consistencia fiscal")
            
            if not analysis_result.get('success', False):
                return self._error_response("Datos de análisis inválidos")
            
            validations = []
            
            # 1. Validar límites de deducciones
            deduction_validations = self._validate_deduction_limits(
                analysis_result.get('potential_deductions', {})
            )
            validations.extend(deduction_validations)
            
            # 2. Validar coherencia entre cédulas
            cedulas_validations = self._validate_cedulas_coherence(
                analysis_result.get('cedulas_totals', {})
            )
            validations.extend(cedulas_validations)
            
            # 3. Validar obligación de declarar
            declaration_validations = self._validate_declaration_obligation(
                analysis_result.get('tax_calculation', {}),
                analysis_result.get('cedulas_totals', {})
            )
            validations.extend(declaration_validations)
            
            # 4. Validar retenciones
            withholding_validations = self._validate_withholdings(
                analysis_result.get('cedulas_totals', {})
            )
            validations.extend(withholding_validations)
            
            # 5. Validar renta exenta
            exempt_validations = self._validate_exempt_income(
                analysis_result.get('potential_deductions', {}),
                analysis_result.get('cedulas_totals', {})
            )
            validations.extend(exempt_validations)
            
            # 6. Validar rangos de tarifa
            tariff_validations = self._validate_tax_brackets(
                analysis_result.get('tax_calculation', {})
            )
            validations.extend(tariff_validations)
            
            # Calcular score de consistencia
            consistency_score = self._calculate_consistency_score(validations)
            
            # Generar recomendaciones de corrección
            corrections = self._generate_correction_recommendations(validations)
            
            logger.info(f"Validación completada: {len(validations)} validaciones realizadas")
            
            return {
                'success': True,
                'validation_date': datetime.now().isoformat(),
                'consistency_score': consistency_score,
                'validations': validations,
                'corrections_needed': corrections,
                'is_consistent': consistency_score['score'] >= 85,
                'summary': self._generate_validation_summary(validations, consistency_score)
            }
            
        except Exception as e:
            logger.error(f"Error en validación de consistencia: {str(e)}")
            return self._error_response(f"Error en validación: {str(e)}")
    
    def _validate_deduction_limits(self, deductions: Dict[str, Any]) -> List[Dict]:
        """Valida que las deducciones no excedan los límites legales"""
        validations = []
        
        # Validar deducción por dependientes
        dependientes_amount = deductions.get('deducciones_dependientes', 0)
        if dependientes_amount > self.LEGAL_LIMITS['deduccion_dependientes_max']:
            validations.append({
                'type': 'deduction_limit_exceeded',
                'category': 'dependientes',
                'severity': 'error',
                'title': 'Límite de Deducción por Dependientes Excedido',
                'description': f'Deducción de ${dependientes_amount:,.0f} excede el límite de ${self.LEGAL_LIMITS["deduccion_dependientes_max"]:,.0f}',
                'legal_reference': 'Artículo 387 del Estatuto Tributario',
                'current_value': dependientes_amount,
                'max_allowed': self.LEGAL_LIMITS['deduccion_dependientes_max'],
                'correction_required': True
            })
        
        # Validar deducción por salud
        salud_amount = deductions.get('deducciones_salud', 0)
        if salud_amount > self.LEGAL_LIMITS['deduccion_salud_max']:
            validations.append({
                'type': 'deduction_limit_exceeded',
                'category': 'salud',
                'severity': 'error',
                'title': 'Límite de Deducción por Salud Excedido',
                'description': f'Deducción de ${salud_amount:,.0f} excede el límite de ${self.LEGAL_LIMITS["deduccion_salud_max"]:,.0f}',
                'legal_reference': 'Artículo 387 del Estatuto Tributario',
                'current_value': salud_amount,
                'max_allowed': self.LEGAL_LIMITS['deduccion_salud_max'],
                'correction_required': True
            })
        
        # Validar deducción por vivienda
        vivienda_amount = deductions.get('deducciones_vivienda', 0)
        if vivienda_amount > self.LEGAL_LIMITS['deduccion_vivienda_max']:
            validations.append({
                'type': 'deduction_limit_exceeded',
                'category': 'vivienda',
                'severity': 'error',
                'title': 'Límite de Deducción por Vivienda Excedido',
                'description': f'Deducción de ${vivienda_amount:,.0f} excede el límite de ${self.LEGAL_LIMITS["deduccion_vivienda_max"]:,.0f}',
                'legal_reference': 'Artículo 119 del Estatuto Tributario',
                'current_value': vivienda_amount,
                'max_allowed': self.LEGAL_LIMITS['deduccion_vivienda_max'],
                'correction_required': True
            })
        
        # Validar deducción AFC
        afc_amount = deductions.get('deducciones_afc', 0)
        if afc_amount > self.LEGAL_LIMITS['deduccion_afc_max']:
            validations.append({
                'type': 'deduction_limit_exceeded',
                'category': 'afc',
                'severity': 'error',
                'title': 'Límite de Deducción AFC Excedido',
                'description': f'Deducción de ${afc_amount:,.0f} excede el límite de ${self.LEGAL_LIMITS["deduccion_afc_max"]:,.0f}',
                'legal_reference': 'Artículo 126-4 del Estatuto Tributario',
                'current_value': afc_amount,
                'max_allowed': self.LEGAL_LIMITS['deduccion_afc_max'],
                'correction_required': True
            })
        
        return validations
    
    def _validate_cedulas_coherence(self, cedulas_totals: Dict[str, Dict]) -> List[Dict]:
        """Valida coherencia entre cédulas tributarias"""
        validations = []
        
        # Verificar que hay ingresos válidos
        total_income = sum(
            cedula.get('ingresos_brutos', 0) 
            for cedula in cedulas_totals.values()
        )
        
        if total_income <= 0:
            validations.append({
                'type': 'no_income_detected',
                'severity': 'critical',
                'title': 'No se Detectaron Ingresos Válidos',
                'description': 'No hay ingresos registrados en ninguna cédula tributaria',
                'legal_reference': 'Artículo 594-1 del Estatuto Tributario',
                'correction_required': True
            })
            return validations
        
        # Validar rentas de trabajo
        trabajo_income = cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0)
        trabajo_withholdings = cedulas_totals.get('rentas_trabajo', {}).get('retenciones', 0)
        
        if trabajo_income > 0:
            # Verificar tasa de retención razonable para trabajo
            if trabajo_withholdings > 0:
                withholding_rate = trabajo_withholdings / trabajo_income
                if withholding_rate > 0.40:  # Más del 40%
                    validations.append({
                        'type': 'excessive_withholding_rate',
                        'category': 'rentas_trabajo',
                        'severity': 'warning',
                        'title': 'Tasa de Retención Excesiva en Rentas de Trabajo',
                        'description': f'Retención del {withholding_rate*100:.1f}% parece excesiva para rentas de trabajo',
                        'current_value': withholding_rate,
                        'expected_range': '5% - 35%',
                        'correction_required': False
                    })
        
        # Validar rentas de capital
        capital_income = cedulas_totals.get('rentas_capital', {}).get('ingresos_brutos', 0)
        capital_withholdings = cedulas_totals.get('rentas_capital', {}).get('retenciones', 0)
        
        if capital_income > 0 and capital_withholdings > 0:
            withholding_rate = capital_withholdings / capital_income
            expected_rate = 0.07  # 7% para intereses
            
            if abs(withholding_rate - expected_rate) > 0.05:  # Diferencia > 5%
                validations.append({
                    'type': 'unexpected_withholding_rate',
                    'category': 'rentas_capital',
                    'severity': 'info',
                    'title': 'Tasa de Retención Atípica en Rentas de Capital',
                    'description': f'Retención del {withholding_rate*100:.1f}% difiere de la tasa típica del 7%',
                    'current_value': withholding_rate,
                    'expected_value': expected_rate,
                    'correction_required': False
                })
        
        return validations
    
    def _validate_declaration_obligation(self, tax_calc: Dict, cedulas_totals: Dict) -> List[Dict]:
        """Valida la obligación de declarar renta"""
        validations = []
        
        base_gravable = tax_calc.get('base_gravable', 0)
        total_income = sum(
            cedula.get('ingresos_brutos', 0) 
            for cedula in cedulas_totals.values()
        )
        
        # Verificar obligación por ingresos
        income_threshold = self.LEGAL_LIMITS['ingresos_brutos_limite']
        
        if total_income > income_threshold:
            must_declare = True
            reason = f'Ingresos de ${total_income:,.0f} superan el límite de ${income_threshold:,.0f}'
        else:
            must_declare = False
            reason = f'Ingresos de ${total_income:,.0f} están por debajo del límite'
        
        validations.append({
            'type': 'declaration_obligation',
            'severity': 'info',
            'title': 'Obligación de Declarar Renta',
            'description': reason,
            'must_declare': must_declare,
            'legal_reference': 'Artículo 594-1 del Estatuto Tributario',
            'income_amount': total_income,
            'income_threshold': income_threshold,
            'correction_required': False
        })
        
        # Si debe declarar, validar que el cálculo sea coherente
        if must_declare and base_gravable <= 0:
            validations.append({
                'type': 'inconsistent_tax_base',
                'severity': 'warning',
                'title': 'Base Gravable Inconsistente',
                'description': 'Debe declarar pero la base gravable es cero o negativa',
                'total_income': total_income,
                'base_gravable': base_gravable,
                'correction_required': True
            })
        
        return validations
    
    def _validate_withholdings(self, cedulas_totals: Dict) -> List[Dict]:
        """Valida retenciones practicadas"""
        validations = []
        
        for cedula_name, cedula_data in cedulas_totals.items():
            income = cedula_data.get('ingresos_brutos', 0)
            withholdings = cedula_data.get('retenciones', 0)
            
            if income <= 0:
                continue
            
            # Validar que hay retenciones cuando deberían haberlas
            if income > self.LEGAL_LIMITS['retencion_trabajo_min'] and withholdings == 0:
                validations.append({
                    'type': 'missing_withholdings',
                    'category': cedula_name,
                    'severity': 'warning',
                    'title': f'Retenciones Faltantes en {cedula_name.replace("_", " ").title()}',
                    'description': f'Ingresos de ${income:,.0f} deberían tener retenciones en la fuente',
                    'income_amount': income,
                    'withholding_threshold': self.LEGAL_LIMITS['retencion_trabajo_min'],
                    'correction_required': False
                })
            
            # Validar que las retenciones no excedan el ingreso
            if withholdings > income:
                validations.append({
                    'type': 'withholding_exceeds_income',
                    'category': cedula_name,
                    'severity': 'error',
                    'title': f'Retenciones Exceden Ingresos en {cedula_name.replace("_", " ").title()}',
                    'description': f'Retenciones de ${withholdings:,.0f} superan ingresos de ${income:,.0f}',
                    'income_amount': income,
                    'withholding_amount': withholdings,
                    'correction_required': True
                })
        
        return validations
    
    def _validate_exempt_income(self, deductions: Dict, cedulas_totals: Dict) -> List[Dict]:
        """Valida la aplicación de renta exenta"""
        validations = []
        
        trabajo_income = cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0)
        exempt_amount = deductions.get('renta_exenta_trabajo', 0)
        
        if trabajo_income > 0:
            # Calcular máximo permitido
            max_by_percentage = trabajo_income * self.LEGAL_LIMITS['renta_exenta_trabajo_percentage']
            max_by_limit = self.LEGAL_LIMITS['renta_exenta_trabajo_max']
            max_allowed = min(max_by_percentage, max_by_limit)
            
            if exempt_amount > max_allowed:
                validations.append({
                    'type': 'exempt_income_exceeded',
                    'severity': 'error',
                    'title': 'Renta Exenta Excede Límite Legal',
                    'description': f'Renta exenta de ${exempt_amount:,.0f} excede el máximo de ${max_allowed:,.0f}',
                    'legal_reference': 'Artículo 206 del Estatuto Tributario',
                    'current_value': exempt_amount,
                    'max_allowed': max_allowed,
                    'max_by_percentage': max_by_percentage,
                    'max_by_limit': max_by_limit,
                    'correction_required': True
                })
            
            # Verificar que se aplicó correctamente
            expected_exempt = max_allowed
            if abs(exempt_amount - expected_exempt) > 1000:  # Diferencia > $1000
                validations.append({
                    'type': 'exempt_income_miscalculated',
                    'severity': 'warning',
                    'title': 'Renta Exenta Mal Calculada',
                    'description': f'Renta exenta debería ser ${expected_exempt:,.0f}',
                    'current_value': exempt_amount,
                    'expected_value': expected_exempt,
                    'correction_required': True
                })
        
        return validations
    
    def _validate_tax_brackets(self, tax_calc: Dict) -> List[Dict]:
        """Valida la aplicación correcta de la tarifa progresiva"""
        validations = []
        
        base_gravable = tax_calc.get('base_gravable', 0)
        impuesto_calculado = tax_calc.get('impuesto_calculado', 0)
        
        if base_gravable <= 0:
            return validations
        
        # Calcular impuesto esperado según tarifa
        expected_tax = 0
        applicable_bracket = None
        
        for i, (min_range, max_range, rate) in enumerate(self.TARIFA_RANGES):
            if base_gravable > min_range:
                applicable_bracket = i
                if i == 0:  # Primera tabla (exenta)
                    expected_tax = 0
                else:
                    # Cálculo simplificado para validación
                    if base_gravable <= max_range:
                        expected_tax = (base_gravable - min_range) * rate
                        break
        
        # Validar que el impuesto esté en el rango esperado
        if applicable_bracket is not None and expected_tax > 0:
            variance = abs(impuesto_calculado - expected_tax) / expected_tax if expected_tax > 0 else 0
            
            if variance > 0.10:  # Diferencia > 10%
                validations.append({
                    'type': 'tax_calculation_variance',
                    'severity': 'warning',
                    'title': 'Variación en Cálculo de Impuesto',
                    'description': f'Impuesto calculado difiere significativamente del esperado',
                    'calculated_tax': impuesto_calculado,
                    'expected_tax': expected_tax,
                    'variance_percentage': variance * 100,
                    'applicable_bracket': applicable_bracket,
                    'correction_required': False
                })
        
        return validations
    
    def _calculate_consistency_score(self, validations: List[Dict]) -> Dict[str, Any]:
        """Calcula score de consistencia basado en validaciones"""
        if not validations:
            return {
                'score': 100,
                'level': 'excellent',
                'description': 'Datos completamente consistentes con la normativa'
            }
        
        # Calcular deducción de puntos por tipo de problema
        total_deduction = 0
        
        for validation in validations:
            if validation['severity'] == 'critical':
                total_deduction += 30
            elif validation['severity'] == 'error':
                total_deduction += 15
            elif validation['severity'] == 'warning':
                total_deduction += 5
            elif validation['severity'] == 'info':
                total_deduction += 1
        
        score = max(0, 100 - total_deduction)
        
        # Determinar nivel
        if score >= 95:
            level = 'excellent'
            description = 'Datos excelentemente consistentes'
        elif score >= 85:
            level = 'good'
            description = 'Datos mayormente consistentes'
        elif score >= 70:
            level = 'acceptable'
            description = 'Datos aceptables con correcciones menores'
        elif score >= 50:
            level = 'poor'
            description = 'Datos requieren correcciones importantes'
        else:
            level = 'critical'
            description = 'Datos inconsistentes - corrección urgente requerida'
        
        return {
            'score': score,
            'level': level,
            'description': description,
            'total_validations': len(validations),
            'corrections_required': sum(1 for v in validations if v.get('correction_required', False))
        }
    
    def _generate_correction_recommendations(self, validations: List[Dict]) -> List[Dict]:
        """Genera recomendaciones específicas de corrección"""
        corrections = []
        
        # Agrupar por tipo de corrección necesaria
        critical_issues = [v for v in validations if v['severity'] == 'critical']
        error_issues = [v for v in validations if v['severity'] == 'error']
        
        if critical_issues:
            corrections.append({
                'priority': 'urgent',
                'title': 'Correcciones Críticas Requeridas',
                'description': 'Estas inconsistencias deben corregirse antes de continuar',
                'issues': [issue['title'] for issue in critical_issues],
                'action': 'Revisar y corregir inmediatamente'
            })
        
        if error_issues:
            corrections.append({
                'priority': 'high',
                'title': 'Errores a Corregir',
                'description': 'Estos errores pueden afectar el cálculo del impuesto',
                'issues': [issue['title'] for issue in error_issues],
                'action': 'Corregir antes de la declaración final'
            })
        
        # Correcciones específicas por categoría
        deduction_errors = [v for v in validations if v.get('type') == 'deduction_limit_exceeded']
        if deduction_errors:
            corrections.append({
                'priority': 'high',
                'title': 'Ajustar Deducciones',
                'description': 'Algunas deducciones exceden los límites legales',
                'action': 'Reducir deducciones a los montos máximos permitidos',
                'specific_limits': {
                    issue['category']: issue['max_allowed'] 
                    for issue in deduction_errors
                }
            })
        
        return corrections
    
    def _generate_validation_summary(self, validations: List[Dict], 
                                   consistency_score: Dict) -> Dict[str, Any]:
        """Genera resumen ejecutivo de validaciones"""
        return {
            'total_validations': len(validations),
            'consistency_level': consistency_score['level'],
            'consistency_score': consistency_score['score'],
            'critical_issues': len([v for v in validations if v['severity'] == 'critical']),
            'errors': len([v for v in validations if v['severity'] == 'error']),
            'warnings': len([v for v in validations if v['severity'] == 'warning']),
            'info': len([v for v in validations if v['severity'] == 'info']),
            'corrections_needed': consistency_score.get('corrections_required', 0),
            'ready_for_declaration': consistency_score['level'] in ['excellent', 'good', 'acceptable']
        }
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Genera respuesta de error estándar"""
        return {
            'success': False,
            'error': error_message,
            'validation_date': datetime.now().isoformat()
        }


# Instancia singleton del validador
_consistency_validator = None

def get_consistency_validator() -> ConsistencyValidator:
    """Factory function para obtener instancia del validador"""
    global _consistency_validator
    
    if _consistency_validator is None:
        _consistency_validator = ConsistencyValidator()
    
    return _consistency_validator
