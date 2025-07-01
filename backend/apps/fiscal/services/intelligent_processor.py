"""
Servicio Principal de Análisis Fiscal Inteligente
Orquesta todos los componentes: parser, análisis, detección de anomalías y validación.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# TEMPORALMENTE COMENTADO - Requiere pandas
from apps.documents.parsers.excel_parser import ExogenaParser
from .analysis_service import get_fiscal_analysis_service
from .anomaly_detector import get_anomaly_detector
from .consistency_validator import get_consistency_validator

logger = logging.getLogger(__name__)


class IntelligentFiscalProcessor:
    """
    Procesador fiscal inteligente que replica el conocimiento del contador.
    Orquesta todo el pipeline de análisis desde el Excel hasta las recomendaciones finales.
    """
    
    def __init__(self):
        # TEMPORALMENTE COMENTADO - Requiere pandas
        # self.parser = ExogenaParser()
        self.parser = None  # Parser temporalmente deshabilitado
        self.fiscal_analyzer = get_fiscal_analysis_service()
        self.anomaly_detector = get_anomaly_detector()
        self.consistency_validator = get_consistency_validator()
        
        self.processing_steps = []
        self.total_processing_time = 0
    
    def process_complete_analysis(self, file_path_or_bytes, user_context: Dict = None) -> Dict[str, Any]:
        """
        Procesamiento completo estilo contador profesional
        
        Args:
            file_path_or_bytes: Archivo Excel de exógena o datos binarios
            user_context: Contexto adicional del usuario (dependientes, etc.)
            
        Returns:
            Dict con análisis fiscal completo
        """
        try:
            start_time = datetime.now()
            logger.info("🚀 Iniciando procesamiento fiscal inteligente")
            
            self.processing_steps = []
            
            # PASO 1: Parser inteligente de Excel
            step1_result = self._step1_intelligent_parsing(file_path_or_bytes)
            if not step1_result['success']:
                return step1_result
            
            # PASO 2: Análisis fiscal profesional
            step2_result = self._step2_fiscal_analysis(step1_result['data'])
            if not step2_result['success']:
                return step2_result
            
            # PASO 3: Detección de anomalías
            step3_result = self._step3_anomaly_detection(
                step1_result['data']['records'],
                step2_result['data']['cedulas_totals']
            )
            
            # PASO 4: Validación de consistencia
            step4_result = self._step4_consistency_validation(step2_result['data'])
            
            # PASO 5: Síntesis final y recomendaciones
            final_result = self._step5_final_synthesis(
                step1_result['data'],
                step2_result['data'], 
                step3_result['data'],
                step4_result['data'],
                user_context
            )
            
            # Calcular tiempo total
            end_time = datetime.now()
            self.total_processing_time = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Procesamiento completado en {self.total_processing_time:.2f} segundos")
            
            return {
                'success': True,
                'processing_time': self.total_processing_time,
                'processing_steps': self.processing_steps,
                'analysis_date': datetime.now().isoformat(),
                'parser_results': step1_result['data'],
                'fiscal_analysis': step2_result['data'],
                'anomaly_detection': step3_result['data'],
                'consistency_validation': step4_result['data'],
                'final_recommendations': final_result,
                'user_friendly_summary': self._generate_user_summary(final_result)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento fiscal: {str(e)}")
            return {
                'success': False,
                'error': f"Error en procesamiento: {str(e)}",
                'processing_steps': self.processing_steps,
                'processing_time': 0
            }
    
    def _step1_intelligent_parsing(self, file_path_or_bytes) -> Dict[str, Any]:
        """Paso 1: Parsing inteligente del archivo Excel"""
        try:
            self._log_step("Paso 1: Analizando archivo de información exógena...")
            
            # TEMPORALMENTE DESHABILITADO - Requiere pandas
            if self.parser is None:
                self._log_step("❌ Parser de Excel temporalmente deshabilitado - pandas no instalado")
                return {
                    'success': False,
                    'error': 'Parser de Excel temporalmente deshabilitado. Instalar pandas para habilitar.',
                    'step_summary': 'Parser no disponible'
                }
            
            if isinstance(file_path_or_bytes, str) and file_path_or_bytes == 'demo':
                # Usar datos demo para testing
                result = self.parser.parse_demo_data()
            else:
                # Procesar archivo real
                result = self.parser.parse_excel_file(file_path_or_bytes)
            
            if result['success']:
                records_count = len(result.get('records', []))
                total_income = sum(r.get('valor_bruto', 0) for r in result.get('records', []))
                
                self._log_step(f"✅ Archivo procesado: {records_count} registros, ${total_income:,.0f} en ingresos")
                
                # Aplicar reglas especiales del contador (falsos ingresos)
                enhanced_result = self._apply_contador_rules(result)
                
                return {
                    'success': True,
                    'data': enhanced_result,
                    'step_summary': f"Archivo procesado exitosamente con {records_count} registros"
                }
            else:
                error_msg = f"Error en parsing: {result.get('error', 'Error desconocido')}"
                self._log_step(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'data': result
                }
                
        except Exception as e:
            error_msg = f"Error crítico en parsing: {str(e)}"
            self._log_step(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _step2_fiscal_analysis(self, parser_data: Dict) -> Dict[str, Any]:
        """Paso 2: Análisis fiscal profesional"""
        try:
            self._log_step("Paso 2: Realizando análisis fiscal profesional...")
            
            analysis_result = self.fiscal_analyzer.analyze_exogena_data(parser_data)
            
            if analysis_result['success']:
                base_gravable = analysis_result['tax_calculation']['base_gravable']
                must_declare = analysis_result['requires_declaration']
                
                status = "Debe declarar" if must_declare else "No obligado a declarar"
                self._log_step(f"✅ Análisis completado: {status}, Base gravable: ${base_gravable:,.0f}")
                
                return {
                    'success': True,
                    'data': analysis_result,
                    'step_summary': f"Análisis fiscal completado - {status}"
                }
            else:
                error_msg = f"Error en análisis: {analysis_result.get('error', 'Error desconocido')}"
                self._log_step(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'data': analysis_result
                }
                
        except Exception as e:
            error_msg = f"Error crítico en análisis: {str(e)}"
            self._log_step(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _step3_anomaly_detection(self, records: List[Dict], cedulas_totals: Dict) -> Dict[str, Any]:
        """Paso 3: Detección de anomalías"""
        try:
            self._log_step("Paso 3: Detectando anomalías y inconsistencias...")
            
            anomaly_result = self.anomaly_detector.detect_anomalies(records, cedulas_totals)
            
            if anomaly_result['success']:
                anomaly_count = anomaly_result['anomalies_count']
                risk_level = anomaly_result['risk_score']['level']
                
                self._log_step(f"✅ Detección completada: {anomaly_count} anomalías, Riesgo: {risk_level}")
                
                return {
                    'success': True,
                    'data': anomaly_result,
                    'step_summary': f"{anomaly_count} anomalías detectadas (Riesgo: {risk_level})"
                }
            else:
                self._log_step("⚠️ Error en detección de anomalías")
                return {
                    'success': False,
                    'data': anomaly_result,
                    'step_summary': "Error en detección de anomalías"
                }
                
        except Exception as e:
            error_msg = f"Error en detección de anomalías: {str(e)}"
            self._log_step(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _step4_consistency_validation(self, fiscal_analysis: Dict) -> Dict[str, Any]:
        """Paso 4: Validación de consistencia"""
        try:
            self._log_step("Paso 4: Validando consistencia con normativa tributaria...")
            
            validation_result = self.consistency_validator.validate_data_consistency(fiscal_analysis)
            
            if validation_result['success']:
                score = validation_result['consistency_score']['score']
                level = validation_result['consistency_score']['level']
                
                self._log_step(f"✅ Validación completada: Score {score}/100 ({level})")
                
                return {
                    'success': True,
                    'data': validation_result,
                    'step_summary': f"Consistencia: {score}/100 ({level})"
                }
            else:
                self._log_step("⚠️ Error en validación de consistencia")
                return {
                    'success': False,
                    'data': validation_result,
                    'step_summary': "Error en validación"
                }
                
        except Exception as e:
            error_msg = f"Error en validación: {str(e)}"
            self._log_step(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _step5_final_synthesis(self, parser_data: Dict, fiscal_analysis: Dict, 
                             anomaly_data: Dict, validation_data: Dict,
                             user_context: Dict = None) -> Dict[str, Any]:
        """Paso 5: Síntesis final y recomendaciones"""
        try:
            self._log_step("Paso 5: Generando síntesis final y recomendaciones...")
            
            # Consolidar información crítica
            critical_issues = []
            recommendations = []
            next_steps = []
            
            # Analizar anomalías críticas
            if anomaly_data.get('success'):
                critical_anomalies = [
                    a for a in anomaly_data.get('anomalies', [])
                    if a.get('severity') in ['critical', 'high']
                ]
                critical_issues.extend(critical_anomalies)
            
            # Analizar problemas de consistencia
            if validation_data.get('success'):
                critical_validations = [
                    v for v in validation_data.get('validations', [])
                    if v.get('severity') in ['critical', 'error']
                ]
                critical_issues.extend(critical_validations)
            
            # Generar recomendaciones inteligentes
            if fiscal_analysis.get('success'):
                optimizations = fiscal_analysis.get('optimizations', [])
                recommendations.extend(optimizations)
                
                # Agregar recomendaciones basadas en perfil
                profile_recommendations = self._generate_profile_recommendations(
                    fiscal_analysis, user_context
                )
                recommendations.extend(profile_recommendations)
            
            # Determinar próximos pasos
            next_steps = self._determine_next_steps(
                fiscal_analysis, critical_issues, validation_data
            )
            
            # Calcular score general
            overall_score = self._calculate_overall_score(
                fiscal_analysis, anomaly_data, validation_data
            )
            
            synthesis = {
                'overall_score': overall_score,
                'critical_issues': critical_issues,
                'recommendations': recommendations,
                'next_steps': next_steps,
                'requires_attention': len(critical_issues) > 0,
                'ready_for_declaration': overall_score['ready_for_declaration'],
                'estimated_completion_time': self._estimate_completion_time(next_steps),
                'priority_actions': self._get_priority_actions(critical_issues, next_steps)
            }
            
            self._log_step(f"✅ Síntesis completada: Score {overall_score['score']}/100")
            
            return synthesis
            
        except Exception as e:
            error_msg = f"Error en síntesis final: {str(e)}"
            self._log_step(f"❌ {error_msg}")
            return {
                'error': error_msg,
                'overall_score': {'score': 0, 'ready_for_declaration': False}
            }
    
    def _apply_contador_rules(self, parser_result: Dict) -> Dict:
        """Aplica las reglas especiales del contador (ej: detección falsos ingresos)"""
        if not parser_result.get('success'):
            return parser_result
        
        records = parser_result.get('records', [])
        
        # Buscar y reclasificar falsos ingresos (fiduciaria + notaría)
        reclassified_count = 0
        
        for record in records:
            special_flags = record.get('special_flags', [])
            
            if 'reclassify_needed' in special_flags and 'move_to_patrimonio' in special_flags:
                # Marcar como patrimonio en lugar de ingreso
                record['original_classification'] = record.get('income_type', 'unknown')
                record['income_type'] = 'patrimonio'
                record['tax_schedule'] = 'patrimonio'
                record['reclassified_by_ai'] = True
                record['reclassification_reason'] = 'Detectado como operación patrimonial (fiduciaria-notaría)'
                reclassified_count += 1
        
        if reclassified_count > 0:
            parser_result['reclassifications'] = {
                'count': reclassified_count,
                'reason': 'Aplicación de regla del contador: falsos ingresos detectados'
            }
            logger.info(f"🧠 Regla del contador aplicada: {reclassified_count} registros reclasificados")
        
        return parser_result
    
    def _generate_profile_recommendations(self, fiscal_analysis: Dict, 
                                        user_context: Dict = None) -> List[Dict]:
        """Genera recomendaciones basadas en el perfil del usuario"""
        recommendations = []
        
        if not fiscal_analysis.get('success'):
            return recommendations
        
        cedulas_totals = fiscal_analysis.get('cedulas_totals', {})
        total_income = sum(
            cedula.get('ingresos_brutos', 0) 
            for cedula in cedulas_totals.values()
        )
        
        # Recomendaciones por nivel de ingresos
        if total_income > 100000000:  # Más de 100M
            recommendations.append({
                'type': 'high_income_planning',
                'title': 'Planeación Fiscal para Altos Ingresos',
                'description': 'Con ingresos superiores a $100M, considera estrategias avanzadas de planeación fiscal',
                'priority': 'high',
                'potential_saving': total_income * 0.05,  # Estimado 5%
                'actions': [
                    'Evaluar constitución de empresa unipersonal',
                    'Considerar inversiones en activos productivos',
                    'Revisar estrategias de ahorro programado'
                ]
            })
        
        # Recomendaciones por tipo de ingresos
        trabajo_income = cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0)
        capital_income = cedulas_totals.get('rentas_capital', {}).get('ingresos_brutos', 0)
        
        if capital_income > trabajo_income * 0.3:  # Más del 30% capital
            recommendations.append({
                'type': 'capital_optimization',
                'title': 'Optimización de Rentas de Capital',
                'description': 'Tienes significativas rentas de capital. Revisa la estructura de tus inversiones',
                'priority': 'medium',
                'actions': [
                    'Evaluar diversificación de portafolio',
                    'Considerar inversiones con beneficios tributarios',
                    'Revisar timing de realizaciones de ganancias'
                ]
            })
        
        return recommendations
    
    def _determine_next_steps(self, fiscal_analysis: Dict, critical_issues: List,
                            validation_data: Dict) -> List[Dict]:
        """Determina los próximos pasos basados en el análisis"""
        next_steps = []
        
        # Si hay problemas críticos, priorizar corrección
        if critical_issues:
            next_steps.append({
                'step': 1,
                'title': 'Corregir Problemas Críticos',
                'description': f'Se encontraron {len(critical_issues)} problemas que requieren atención inmediata',
                'priority': 'urgent',
                'estimated_time': '30-60 minutos',
                'actions': [issue.get('title', 'Problema no especificado') for issue in critical_issues[:3]]
            })
        
        # Si el análisis fiscal fue exitoso
        if fiscal_analysis.get('success'):
            requires_declaration = fiscal_analysis.get('requires_declaration', False)
            
            if requires_declaration:
                next_steps.append({
                    'step': 2,
                    'title': 'Recopilar Documentos Soporte',
                    'description': 'Reunir documentos adicionales para maximizar deducciones',
                    'priority': 'high',
                    'estimated_time': '2-3 horas',
                    'actions': [
                        'Certificados de medicina prepagada',
                        'Documentos de dependientes',
                        'Certificados de intereses de vivienda',
                        'Comprobantes de aportes voluntarios'
                    ]
                })
                
                next_steps.append({
                    'step': 3,
                    'title': 'Completar Declaración',
                    'description': 'Diligenciar formulario 210 con la información validada',
                    'priority': 'high',
                    'estimated_time': '1-2 horas',
                    'actions': [
                        'Revisar borrador generado',
                        'Validar cálculos finales',
                        'Presentar declaración'
                    ]
                })
            else:
                next_steps.append({
                    'step': 2,
                    'title': 'Confirmación - No Obligado a Declarar',
                    'description': 'Tus ingresos están por debajo del límite, pero puedes declarar voluntariamente',
                    'priority': 'low',
                    'estimated_time': '15 minutos',
                    'actions': [
                        'Evaluar si conviene declarar voluntariamente',
                        'Guardar análisis para próximo año'
                    ]
                })
        
        return next_steps
    
    def _calculate_overall_score(self, fiscal_analysis: Dict, anomaly_data: Dict,
                               validation_data: Dict) -> Dict[str, Any]:
        """Calcula score general del análisis"""
        scores = []
        
        # Score de análisis fiscal (peso 40%)
        if fiscal_analysis.get('success'):
            scores.append(('fiscal', 85, 0.4))  # Score base alto para análisis exitoso
        else:
            scores.append(('fiscal', 0, 0.4))
        
        # Score de anomalías (peso 30%)
        if anomaly_data.get('success'):
            anomaly_score = 100 - anomaly_data.get('risk_score', {}).get('score', 0)
            scores.append(('anomalies', anomaly_score, 0.3))
        else:
            scores.append(('anomalies', 50, 0.3))  # Score neutral si hay error
        
        # Score de consistencia (peso 30%)
        if validation_data.get('success'):
            consistency_score = validation_data.get('consistency_score', {}).get('score', 0)
            scores.append(('consistency', consistency_score, 0.3))
        else:
            scores.append(('consistency', 50, 0.3))  # Score neutral si hay error
        
        # Calcular score ponderado
        weighted_score = sum(score * weight for _, score, weight in scores)
        
        # Determinar nivel y estado
        if weighted_score >= 90:
            level = 'excellent'
            ready = True
            description = 'Análisis excelente - Listo para declaración'
        elif weighted_score >= 75:
            level = 'good'
            ready = True
            description = 'Análisis bueno - Listo con correcciones menores'
        elif weighted_score >= 60:
            level = 'acceptable'
            ready = False
            description = 'Análisis aceptable - Requiere revisiones'
        else:
            level = 'poor'
            ready = False
            description = 'Análisis requiere mejoras significativas'
        
        return {
            'score': round(weighted_score, 1),
            'level': level,
            'ready_for_declaration': ready,
            'description': description,
            'component_scores': {name: score for name, score, _ in scores}
        }
    
    def _estimate_completion_time(self, next_steps: List[Dict]) -> str:
        """Estima tiempo total para completar próximos pasos"""
        if not next_steps:
            return "Completado"
        
        # Sumar tiempos estimados (extraer horas de strings como "2-3 horas")
        total_hours = 0
        for step in next_steps:
            time_str = step.get('estimated_time', '1 hora')
            # Extracción simple - en producción sería más robusta
            if 'hora' in time_str or 'hour' in time_str:
                if '-' in time_str:
                    # Tomar el valor promedio del rango
                    try:
                        parts = time_str.split('-')
                        min_hours = float(parts[0])
                        max_hours = float(parts[1].split()[0])
                        total_hours += (min_hours + max_hours) / 2
                    except:
                        total_hours += 1
                else:
                    try:
                        total_hours += float(time_str.split()[0])
                    except:
                        total_hours += 1
            elif 'minuto' in time_str or 'minute' in time_str:
                total_hours += 0.5  # Redondear minutos a media hora
        
        if total_hours <= 1:
            return "Menos de 1 hora"
        elif total_hours <= 4:
            return f"{int(total_hours)} horas aproximadamente"
        else:
            return f"{int(total_hours)} horas (se puede hacer en varios días)"
    
    def _get_priority_actions(self, critical_issues: List, next_steps: List) -> List[str]:
        """Obtiene las 3 acciones más prioritarias"""
        priority_actions = []
        
        # Agregar problemas críticos primero
        for issue in critical_issues[:2]:  # Máximo 2 problemas críticos
            priority_actions.append(issue.get('title', 'Problema crítico'))
        
        # Agregar primera acción de próximos pasos
        if next_steps and len(priority_actions) < 3:
            first_step = next_steps[0]
            if first_step.get('actions'):
                priority_actions.append(first_step['actions'][0])
        
        return priority_actions[:3]
    
    def _generate_user_summary(self, final_recommendations: Dict) -> Dict[str, Any]:
        """Genera resumen amigable para el usuario final"""
        overall_score = final_recommendations.get('overall_score', {})
        
        # Mensaje principal basado en score
        score = overall_score.get('score', 0)
        ready = overall_score.get('ready_for_declaration', False)
        
        if ready and score >= 85:
            main_message = "¡Excelente! Tu información está lista para la declaración de renta."
            status_color = "green"
        elif ready:
            main_message = "Muy bien! Tu información está casi lista, solo faltan algunos ajustes menores."
            status_color = "yellow"
        else:
            main_message = "Necesitamos revisar algunos aspectos antes de proceder con tu declaración."
            status_color = "orange"
        
        # Acciones prioritarias en lenguaje simple
        priority_actions = final_recommendations.get('priority_actions', [])
        next_steps = final_recommendations.get('next_steps', [])
        
        return {
            'main_message': main_message,
            'status_color': status_color,
            'overall_score': score,
            'is_ready': ready,
            'priority_actions': priority_actions,
            'estimated_time': final_recommendations.get('estimated_completion_time', 'Sin estimar'),
            'critical_issues_count': len(final_recommendations.get('critical_issues', [])),
            'recommendations_count': len(final_recommendations.get('recommendations', [])),
            'next_step_title': next_steps[0].get('title', 'Sin próximos pasos') if next_steps else 'Análisis completado'
        }
    
    def _log_step(self, message: str):
        """Registra un paso del procesamiento"""
        timestamp = datetime.now().isoformat()
        step_entry = f"[{timestamp}] {message}"
        self.processing_steps.append(step_entry)
        logger.info(step_entry)


# Instancia singleton del procesador
_fiscal_processor = None

def get_intelligent_fiscal_processor() -> IntelligentFiscalProcessor:
    """Factory function para obtener instancia del procesador"""
    global _fiscal_processor
    
    if _fiscal_processor is None:
        _fiscal_processor = IntelligentFiscalProcessor()
    
    return _fiscal_processor
