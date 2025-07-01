"""
Servicio de Análisis Fiscal - Replica la lógica del contador profesional
Implementa el conocimiento del contador para calcular cédulas tributarias,
detectar optimizaciones fiscales y generar sugerencias inteligentes.
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class FiscalAnalysisService:
    """
    Replica la lógica del contador para análisis fiscal inteligente.
    
    Funcionalidades principales:
    - Calcular cédulas tributarias
    - Aplicar deducciones automáticas
    - Detectar optimizaciones fiscales
    - Generar sugerencias paso a paso
    """
    
    def __init__(self):
        # Valores UVT para 2024 (actualizable por configuración)
        self.UVT_2024 = 47065  # Valor UVT vigente
        
        # Tarifas y límites fiscales para 2024
        self.FISCAL_LIMITS = {
            'limite_no_declarante': 47 * self.UVT_2024,  # 47 UVT
            'tope_renta_exenta_trabajo': 240 * self.UVT_2024,  # 240 UVT
            'limite_deducciones_dependientes': 32 * self.UVT_2024,  # 32 UVT por dependiente
            'limite_deduccion_salud': 16 * self.UVT_2024,  # 16 UVT medicina prepagada
            'limite_deduccion_vivienda': 1200 * self.UVT_2024,  # 1200 UVT intereses vivienda
            'limite_deduccion_afc': 2800 * self.UVT_2024,  # 2800 UVT AFC
        }
        
        # Tarifa progresiva renta 2024 (personas naturales)
        self.TARIFA_RENTA = [
            (0, 1090 * self.UVT_2024, 0, 0),  # 0%
            (1090 * self.UVT_2024, 1700 * self.UVT_2024, 0.19, 0),  # 19%
            (1700 * self.UVT_2024, 4100 * self.UVT_2024, 0.28, 153 * self.UVT_2024),  # 28%
            (4100 * self.UVT_2024, 8670 * self.UVT_2024, 0.33, 357 * self.UVT_2024),  # 33%
            (8670 * self.UVT_2024, 18970 * self.UVT_2024, 0.35, 531 * self.UVT_2024),  # 35%
            (18970 * self.UVT_2024, float('inf'), 0.37, 911 * self.UVT_2024),  # 37%
        ]
        
        # Categorías de deducciones con sus límites
        self.DEDUCTION_CATEGORIES = {
            'salud': {
                'limite_prepagada': 16 * self.UVT_2024,
                'keywords': ['medicina prepagada', 'seguro salud', 'eps'],
                'descripcion': 'Medicina prepagada y seguros de salud'
            },
            'educacion': {
                'limite': None,  # Sin límite específico
                'keywords': ['educacion', 'universidad', 'colegio', 'matricula'],
                'descripcion': 'Gastos de educación propia, cónyuge e hijos'
            },
            'dependientes': {
                'limite_por_dependiente': 32 * self.UVT_2024,
                'keywords': ['dependiente', 'hijo', 'padre', 'madre'],
                'descripcion': 'Dependientes económicos'
            },
            'vivienda': {
                'limite_interes': 1200 * self.UVT_2024,
                'keywords': ['interes vivienda', 'credito hipotecario', 'vivienda'],
                'descripcion': 'Intereses de crédito de vivienda'
            },
            'afc': {
                'limite': 2800 * self.UVT_2024,
                'keywords': ['afc', 'ahorro programado', 'cesantias'],
                'descripcion': 'Aportes a AFC y ahorro programado'
            }
        }
    
    def analyze_exogena_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis completo estilo contador profesional
        
        Args:
            processed_data: Datos procesados por el ExogenaParser
            
        Returns:
            Dict con análisis fiscal completo
        """
        try:
            logger.info("Iniciando análisis fiscal inteligente")
            
            if not processed_data.get('success', False):
                return self._error_response("Datos de entrada inválidos")
            
            records = processed_data.get('records', [])
            if not records:
                return self._error_response("No hay registros para analizar")
            
            # 1. Clasificar por cédulas tributarias
            cedulas_classification = self._classify_by_cedulas(records)
            
            # 2. Calcular totales por cédula
            cedulas_totals = self._calculate_cedulas_totals(cedulas_classification)
            
            # 3. Detectar deducciones aplicables
            potential_deductions = self._detect_potential_deductions(records, cedulas_totals)
            
            # 4. Calcular renta líquida gravable
            renta_liquida = self._calculate_renta_liquida(cedulas_totals, potential_deductions)
            
            # 5. Calcular impuesto de renta
            tax_calculation = self._calculate_income_tax(renta_liquida)
            
            # 6. Detectar anomalías y optimizaciones
            anomalies = self._detect_anomalies(records, cedulas_totals)
            optimizations = self._suggest_optimizations(cedulas_totals, potential_deductions, tax_calculation)
            
            # 7. Generar recomendaciones paso a paso
            step_by_step = self._generate_step_by_step_analysis(
                cedulas_totals, potential_deductions, tax_calculation, optimizations
            )
            
            logger.info("Análisis fiscal completado exitosamente")
            
            return {
                'success': True,
                'analysis_date': datetime.now().isoformat(),
                'fiscal_year': 2024,
                'cedulas_classification': cedulas_classification,
                'cedulas_totals': cedulas_totals,
                'potential_deductions': potential_deductions,
                'renta_liquida': renta_liquida,
                'tax_calculation': tax_calculation,
                'anomalies': anomalies,
                'optimizations': optimizations,
                'step_by_step_analysis': step_by_step,
                'requires_declaration': tax_calculation['base_gravable'] > self.FISCAL_LIMITS['limite_no_declarante'],
                'estimated_refund': max(0, tax_calculation['retenciones_totales'] - tax_calculation['impuesto_neto']),
                'estimated_payment': max(0, tax_calculation['impuesto_neto'] - tax_calculation['retenciones_totales'])
            }
            
        except Exception as e:
            logger.error(f"Error en análisis fiscal: {str(e)}")
            return self._error_response(f"Error en análisis: {str(e)}")
    
    def _classify_by_cedulas(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Clasifica registros por cédulas tributarias"""
        classification = {
            'rentas_trabajo': [],  # Cédula laboral
            'rentas_capital': [],  # Cédula capital
            'rentas_no_laborales': [],  # Cédula no laboral
            'ganancias_ocasionales': [],  # Ganancias ocasionales
            'otros': []
        }
        
        for record in records:
            cedula = self._determine_cedula(record)
            classification[cedula].append(record)
        
        return classification
    
    def _determine_cedula(self, record: Dict[str, Any]) -> str:
        """Determina la cédula tributaria según el tipo de ingreso"""
        income_type = record.get('income_type', '').lower()
        tax_schedule = record.get('tax_schedule', '').lower()
        third_party_name = record.get('third_party_name', '').lower()
        concept_description = record.get('concept_description', '').lower()
        
        # Rentas de trabajo (salarios, honorarios, servicios)
        if (income_type in ['salary', 'honorarios', 'services', 'commissions'] or
            tax_schedule == 'labor' or
            any(keyword in concept_description for keyword in ['salario', 'honorario', 'comision', 'prestacion'])):
            return 'rentas_trabajo'
        
        # Rentas de capital (intereses, arrendamientos, dividendos)
        elif (income_type in ['interests', 'rental', 'dividends'] or
              tax_schedule == 'capital' or
              any(keyword in concept_description for keyword in ['interes', 'rendimiento', 'arrendamiento', 'dividendo'])):
            return 'rentas_capital'
        
        # Ganancias ocasionales (premios, rifas, loterías)
        elif (income_type in ['prizes', 'lottery'] or
              any(keyword in concept_description for keyword in ['premio', 'rifa', 'loteria', 'chance'])):
            return 'ganancias_ocasionales'
        
        # Rentas no laborales (otros ingresos)
        elif income_type == 'other':
            return 'rentas_no_laborales'
        
        # Default a rentas de trabajo si no se puede clasificar
        else:
            return 'rentas_trabajo'
    
    def _calculate_cedulas_totals(self, classification: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Calcula totales por cada cédula tributaria"""
        totals = {}
        
        for cedula, records in classification.items():
            if not records:
                totals[cedula] = {
                    'ingresos_brutos': 0.0,
                    'retenciones': 0.0,
                    'ingresos_netos': 0.0,
                    'registros_count': 0
                }
                continue
            
            ingresos_brutos = sum(record.get('gross_amount', 0) for record in records)
            retenciones = sum(record.get('withholding_amount', 0) for record in records)
            
            totals[cedula] = {
                'ingresos_brutos': ingresos_brutos,
                'retenciones': retenciones,
                'ingresos_netos': ingresos_brutos - retenciones,
                'registros_count': len(records),
                'third_parties': len(set(record.get('third_party_nit', '') for record in records))
            }
        
        return totals
    
    def _detect_potential_deductions(self, records: List[Dict], cedulas_totals: Dict) -> Dict[str, Any]:
        """Detecta deducciones potenciales basándose en los ingresos"""
        potential_deductions = {
            'renta_exenta_trabajo': 0.0,
            'deducciones_dependientes': 0.0,
            'deducciones_salud': 0.0,
            'deducciones_educacion': 0.0,
            'deducciones_vivienda': 0.0,
            'deducciones_afc': 0.0,
            'suggestions': []
        }
        
        # Calcular renta exenta de trabajo (hasta 240 UVT)
        rentas_trabajo = cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0)
        if rentas_trabajo > 0:
            renta_exenta = min(rentas_trabajo * 0.25, self.FISCAL_LIMITS['tope_renta_exenta_trabajo'])
            potential_deductions['renta_exenta_trabajo'] = renta_exenta
            
            # Generar sugerencias basadas en análisis
            if rentas_trabajo > self.FISCAL_LIMITS['limite_no_declarante']:
                potential_deductions['suggestions'].append({
                    'type': 'renta_exenta',
                    'title': 'Renta Exenta de Trabajo Detectada',
                    'description': f'Puedes aplicar renta exenta por ${renta_exenta:,.0f} (25% de tus ingresos laborales)',
                    'legal_base': 'Artículo 206 del Estatuto Tributario',
                    'potential_saving': renta_exenta * 0.33,  # Estimado en tarifa promedio
                    'action_required': 'Automáticamente aplicada en la declaración'
                })
        
        # Sugerir deducciones comunes
        self._suggest_common_deductions(potential_deductions, rentas_trabajo)
        
        return potential_deductions
    
    def _suggest_common_deductions(self, deductions: Dict, rentas_trabajo: float):
        """Sugiere deducciones comunes basándose en el perfil de ingresos"""
        suggestions = deductions['suggestions']
        
        # Dependientes
        if rentas_trabajo > 20000000:  # Más de 20M sugiere posibles dependientes
            suggestions.append({
                'type': 'dependientes',
                'title': 'Deducción por Dependientes',
                'description': f'¿Tienes padres, hijos o familiares que dependan económicamente de ti? Puedes deducir hasta ${self.FISCAL_LIMITS["limite_deducciones_dependientes"]:,.0f} por dependiente',
                'legal_base': 'Artículo 387 del Estatuto Tributario',
                'potential_saving': self.FISCAL_LIMITS["limite_deducciones_dependientes"] * 0.33,
                'action_required': 'Subir certificado de dependencia económica'
            })
        
        # Medicina prepagada
        if rentas_trabajo > 15000000:  # Perfil que típicamente tiene prepagada
            suggestions.append({
                'type': 'salud',
                'title': 'Medicina Prepagada',
                'description': f'Si tienes medicina prepagada, puedes deducir hasta ${self.FISCAL_LIMITS["limite_deduccion_salud"]:,.0f} anuales',
                'legal_base': 'Artículo 387 del Estatuto Tributario',
                'potential_saving': self.FISCAL_LIMITS["limite_deduccion_salud"] * 0.33,
                'action_required': 'Subir certificado de pagos de medicina prepagada'
            })
        
        # Intereses de vivienda
        suggestions.append({
            'type': 'vivienda',
            'title': 'Intereses de Crédito Hipotecario',
            'description': f'Si tienes crédito hipotecario, puedes deducir los intereses hasta ${self.FISCAL_LIMITS["limite_deduccion_vivienda"]:,.0f} anuales',
            'legal_base': 'Artículo 119 del Estatuto Tributario',
            'potential_saving': self.FISCAL_LIMITS["limite_deduccion_vivienda"] * 0.33,
            'action_required': 'Subir certificado del banco con intereses pagados'
        })
    
    def _calculate_renta_liquida(self, cedulas_totals: Dict, deductions: Dict) -> Dict[str, float]:
        """Calcula la renta líquida gravable"""
        # Suma de todas las cédulas de renta
        total_ingresos = (
            cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0) +
            cedulas_totals.get('rentas_capital', {}).get('ingresos_brutos', 0) +
            cedulas_totals.get('rentas_no_laborales', {}).get('ingresos_brutos', 0)
        )
        
        # Aplicar renta exenta de trabajo
        renta_exenta = deductions.get('renta_exenta_trabajo', 0)
        
        # Aplicar deducciones (actualmente estimadas, luego serán reales)
        total_deducciones = (
            deductions.get('deducciones_dependientes', 0) +
            deductions.get('deducciones_salud', 0) +
            deductions.get('deducciones_educacion', 0) +
            deductions.get('deducciones_vivienda', 0) +
            deductions.get('deducciones_afc', 0)
        )
        
        # Calcular renta líquida
        renta_liquida_ordinaria = max(0, total_ingresos - renta_exenta - total_deducciones)
        
        return {
            'total_ingresos': total_ingresos,
            'renta_exenta_trabajo': renta_exenta,
            'total_deducciones': total_deducciones,
            'renta_liquida_ordinaria': renta_liquida_ordinaria,
            'base_gravable': renta_liquida_ordinaria  # Para personas naturales sin compensaciones
        }
    
    def _calculate_income_tax(self, renta_liquida: Dict) -> Dict[str, float]:
        """Calcula el impuesto de renta usando la tarifa progresiva"""
        base_gravable = renta_liquida['base_gravable']
        
        if base_gravable <= self.FISCAL_LIMITS['limite_no_declarante']:
            return {
                'base_gravable': base_gravable,
                'impuesto_calculado': 0.0,
                'impuesto_neto': 0.0,
                'retenciones_totales': 0.0,
                'saldo_a_favor': 0.0,
                'saldo_a_pagar': 0.0,
                'no_declarante': True
            }
        
        # Aplicar tarifa progresiva
        impuesto = 0.0
        for min_range, max_range, rate, fixed_amount in self.TARIFA_RENTA:
            if base_gravable > min_range:
                taxable_in_range = min(base_gravable, max_range) - min_range
                impuesto += (taxable_in_range * rate) + fixed_amount
                break
        
        # Por ahora, usar retenciones estimadas (luego serán reales del parser)
        retenciones_totales = base_gravable * 0.10  # Estimado 10%
        
        # Calcular saldo final
        saldo_a_favor = max(0, retenciones_totales - impuesto)
        saldo_a_pagar = max(0, impuesto - retenciones_totales)
        
        return {
            'base_gravable': base_gravable,
            'impuesto_calculado': impuesto,
            'impuesto_neto': impuesto,
            'retenciones_totales': retenciones_totales,
            'saldo_a_favor': saldo_a_favor,
            'saldo_a_pagar': saldo_a_pagar,
            'no_declarante': False
        }
    
    def _detect_anomalies(self, records: List[Dict], cedulas_totals: Dict) -> List[Dict]:
        """Detecta anomalías y inconsistencias en los datos"""
        anomalies = []
        
        # Detectar valores atípicos
        for record in records:
            if record.get('gross_amount', 0) > 100000000:  # Más de 100M
                anomalies.append({
                    'type': 'high_value',
                    'severity': 'warning',
                    'message': f'Ingreso inusualmente alto: ${record["gross_amount"]:,.0f} de {record.get("third_party_name", "tercero desconocido")}',
                    'suggestion': 'Verifica que el monto sea correcto'
                })
        
        # Detectar posibles falsos ingresos (implementado en el parser)
        for record in records:
            if 'potential_false_income' in record.get('special_flags', []):
                anomalies.append({
                    'type': 'false_income_detected',
                    'severity': 'critical',
                    'message': 'Detectado posible falso ingreso de fiduciaria',
                    'suggestion': 'Este monto debe ir en patrimonio, no en ingresos. AccountIA lo ha reclasificado automáticamente.',
                    'auto_fixed': True
                })
        
        return anomalies
    
    def _suggest_optimizations(self, cedulas_totals: Dict, deductions: Dict, tax_calc: Dict) -> List[Dict]:
        """Sugiere optimizaciones fiscales específicas"""
        optimizations = []
        
        total_ingresos = sum(cedula.get('ingresos_brutos', 0) for cedula in cedulas_totals.values())
        
        # Optimización: Aportes voluntarios a pensión
        if total_ingresos > 30000000 and tax_calc.get('saldo_a_pagar', 0) > 1000000:
            optimizations.append({
                'type': 'pension_voluntary',
                'title': 'Aportes Voluntarios a Pensión',
                'description': 'Considera hacer aportes voluntarios a tu fondo de pensiones para reducir la base gravable',
                'potential_saving': min(total_ingresos * 0.30, 4500 * self.UVT_2024) * 0.33,
                'effort': 'medium',
                'deadline': 'Hasta abril del siguiente año',
                'legal_base': 'Artículo 126-1 del Estatuto Tributario'
            })
        
        # Optimización: AFC (Ahorro para el Fomento de la Construcción)
        if total_ingresos > 25000000:
            optimizations.append({
                'type': 'afc',
                'title': 'Cuenta AFC',
                'description': 'Abre una cuenta AFC para ahorrar hasta 2800 UVT deducibles de impuestos',
                'potential_saving': self.FISCAL_LIMITS['limite_deduccion_afc'] * 0.33,
                'effort': 'low',
                'deadline': 'Hasta diciembre del año gravable',
                'legal_base': 'Artículo 126-4 del Estatuto Tributario'
            })
        
        return optimizations
    
    def _generate_step_by_step_analysis(self, cedulas_totals: Dict, deductions: Dict, 
                                      tax_calc: Dict, optimizations: List[Dict]) -> List[Dict]:
        """Genera análisis paso a paso estilo contador"""
        steps = []
        
        # Paso 1: Resumen de ingresos
        total_ingresos = sum(cedula.get('ingresos_brutos', 0) for cedula in cedulas_totals.values())
        steps.append({
            'step': 1,
            'title': 'Análisis de Ingresos',
            'description': f'Tus ingresos totales del año son ${total_ingresos:,.0f}',
            'details': [
                f"Rentas de trabajo: ${cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0):,.0f}",
                f"Rentas de capital: ${cedulas_totals.get('rentas_capital', {}).get('ingresos_brutos', 0):,.0f}",
                f"Otras rentas: ${cedulas_totals.get('rentas_no_laborales', {}).get('ingresos_brutos', 0):,.0f}"
            ],
            'status': 'completed'
        })
        
        # Paso 2: Aplicación de renta exenta
        renta_exenta = deductions.get('renta_exenta_trabajo', 0)
        if renta_exenta > 0:
            steps.append({
                'step': 2,
                'title': 'Renta Exenta de Trabajo',
                'description': f'Se aplicó renta exenta por ${renta_exenta:,.0f} (25% de ingresos laborales)',
                'details': ['Esta deducción reduce automáticamente tu base gravable'],
                'status': 'completed'
            })
        
        # Paso 3: Deducciones adicionales
        total_deducciones = deductions.get('total_deducciones', 0)
        steps.append({
            'step': 3,
            'title': 'Deducciones Adicionales',
            'description': f'Deducciones adicionales aplicables: ${total_deducciones:,.0f}',
            'details': [
                'Medicina prepagada: Pendiente de documentos',
                'Dependientes: Pendiente de documentos',
                'Intereses vivienda: Pendiente de documentos'
            ],
            'status': 'pending_documents'
        })
        
        # Paso 4: Cálculo final
        if tax_calc.get('no_declarante', False):
            steps.append({
                'step': 4,
                'title': 'Resultado Final',
                'description': 'No estás obligado a declarar renta',
                'details': ['Tus ingresos están por debajo del límite de 47 UVT'],
                'status': 'completed'
            })
        else:
            saldo_favor = tax_calc.get('saldo_a_favor', 0)
            saldo_pagar = tax_calc.get('saldo_a_pagar', 0)
            
            if saldo_favor > 0:
                steps.append({
                    'step': 4,
                    'title': 'Resultado Final - Saldo a Favor',
                    'description': f'La DIAN te debe devolver ${saldo_favor:,.0f}',
                    'details': ['Tus retenciones fueron mayores al impuesto calculado'],
                    'status': 'completed'
                })
            else:
                steps.append({
                    'step': 4,
                    'title': 'Resultado Final - Saldo a Pagar',
                    'description': f'Debes pagar ${saldo_pagar:,.0f} a la DIAN',
                    'details': ['Puedes reducir este valor con las optimizaciones sugeridas'],
                    'status': 'action_required'
                })
        
        return steps
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Genera respuesta de error estándar"""
        return {
            'success': False,
            'error': error_message,
            'analysis_date': datetime.now().isoformat()
        }


# Instancia singleton del servicio
_fiscal_analysis_service = None

def get_fiscal_analysis_service() -> FiscalAnalysisService:
    """Factory function para obtener instancia del servicio"""
    global _fiscal_analysis_service
    
    if _fiscal_analysis_service is None:
        _fiscal_analysis_service = FiscalAnalysisService()
    
    return _fiscal_analysis_service
