"""
Detector de Anomalías - Detecta inconsistencias que un contador profesional notaría
Identifica patrones sospechosos, valores atípicos y posibles errores en los datos fiscales.
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter, defaultdict
import statistics
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detecta inconsistencias que un contador profesional notaría:
    - Valores desproporcionados
    - Duplicados sospechosos  
    - Falta de información clave
    - Patrones anómalos en los datos
    """
    
    def __init__(self):
        self.anomalies_found = []
        self.severity_levels = {
            'low': {'weight': 1, 'color': 'yellow'},
            'medium': {'weight': 2, 'color': 'orange'}, 
            'high': {'weight': 3, 'color': 'red'},
            'critical': {'weight': 4, 'color': 'dark-red'}
        }
        
        # Patrones conocidos de problemas
        self.known_patterns = {
            'round_numbers': [1000000, 5000000, 10000000, 50000000, 100000000],
            'suspicious_nits': ['123456789', '000000000', '999999999'],
            'test_companies': ['TEST', 'PRUEBA', 'EJEMPLO', 'DEMO'],
            'incomplete_data_indicators': ['N/A', 'NO APLICA', 'SIN INFORMACION', '']
        }
    
    def detect_anomalies(self, records: List[Dict[str, Any]], 
                        cedulas_totals: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Detecta anomalías en los datos fiscales
        
        Args:
            records: Lista de registros procesados
            cedulas_totals: Totales por cédula tributaria
            
        Returns:
            Dict con anomalías detectadas y recomendaciones
        """
        try:
            logger.info("Iniciando detección de anomalías")
            
            self.anomalies_found = []
            
            if not records:
                return self._empty_response("No hay registros para analizar")
            
            # 1. Detectar valores atípicos estadísticamente
            statistical_anomalies = self._detect_statistical_outliers(records)
            
            # 2. Detectar duplicados sospechosos
            duplicate_anomalies = self._detect_suspicious_duplicates(records)
            
            # 3. Detectar inconsistencias en datos
            data_inconsistencies = self._detect_data_inconsistencies(records)
            
            # 4. Detectar patrones sospechosos
            pattern_anomalies = self._detect_suspicious_patterns(records)
            
            # 5. Detectar falta de información crítica
            missing_data_anomalies = self._detect_missing_critical_data(records)
            
            # 6. Validar coherencia entre cédulas
            coherence_anomalies = self._validate_cedulas_coherence(cedulas_totals)
            
            # 7. Detectar posibles errores de clasificación
            classification_anomalies = self._detect_classification_errors(records)
            
            # Consolidar todas las anomalías
            all_anomalies = (
                statistical_anomalies + duplicate_anomalies + data_inconsistencies +
                pattern_anomalies + missing_data_anomalies + coherence_anomalies +
                classification_anomalies
            )
            
            # Calcular score de riesgo general
            risk_score = self._calculate_risk_score(all_anomalies)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(all_anomalies, risk_score)
            
            logger.info(f"Detección completada: {len(all_anomalies)} anomalías encontradas")
            
            return {
                'success': True,
                'anomalies_count': len(all_anomalies),
                'risk_score': risk_score,
                'anomalies': all_anomalies,
                'recommendations': recommendations,
                'summary': self._generate_summary(all_anomalies, risk_score),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en detección de anomalías: {str(e)}")
            return {
                'success': False,
                'error': f"Error en detección: {str(e)}",
                'anomalies': [],
                'recommendations': []
            }
    
    def _detect_statistical_outliers(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta valores atípicos usando análisis estadístico"""
        anomalies = []
        
        if len(records) < 3:  # Necesitamos al menos 3 registros para estadísticas
            return anomalies
        
        # Analizar valores de ingresos
        amounts = [record.get('gross_amount', 0) for record in records if record.get('gross_amount', 0) > 0]
        
        if len(amounts) < 3:
            return anomalies
        
        try:
            mean_amount = statistics.mean(amounts)
            median_amount = statistics.median(amounts)
            stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Detectar outliers usando regla de 3 desviaciones estándar
            threshold_high = mean_amount + (3 * stdev_amount)
            threshold_low = mean_amount - (3 * stdev_amount)
            
            for record in records:
                amount = record.get('gross_amount', 0)
                
                if amount > threshold_high and amount > 10000000:  # Más de 10M y outlier
                    anomalies.append({
                        'type': 'statistical_outlier_high',
                        'severity': 'medium',
                        'title': 'Valor Inusualmente Alto Detectado',
                        'description': f'Ingreso de ${amount:,.0f} es {amount/mean_amount:.1f}x mayor que el promedio',
                        'record_details': {
                            'nit': record.get('third_party_nit', ''),
                            'name': record.get('third_party_name', ''),
                            'amount': amount
                        },
                        'recommendation': 'Verificar que el monto sea correcto y no sea un error de digitación',
                        'statistical_info': {
                            'amount': amount,
                            'mean': mean_amount,
                            'median': median_amount,
                            'stdev': stdev_amount
                        }
                    })
                
                elif amount < threshold_low and amount > 0:
                    anomalies.append({
                        'type': 'statistical_outlier_low',
                        'severity': 'low',
                        'title': 'Valor Inusualmente Bajo',
                        'description': f'Ingreso de ${amount:,.0f} es significativamente menor al patrón',
                        'record_details': {
                            'nit': record.get('third_party_nit', ''),
                            'name': record.get('third_party_name', ''),
                            'amount': amount
                        },
                        'recommendation': 'Revisar si falta información o hay errores'
                    })
            
            # Detectar concentración excesiva en pocos terceros
            nit_amounts = defaultdict(float)
            for record in records:
                nit = record.get('third_party_nit', '')
                if nit:
                    nit_amounts[nit] += record.get('gross_amount', 0)
            
            total_income = sum(amounts)
            for nit, amount in nit_amounts.items():
                concentration = amount / total_income if total_income > 0 else 0
                
                if concentration > 0.8:  # Más del 80% de un solo tercero
                    third_party_name = next(
                        (r.get('third_party_name', '') for r in records if r.get('third_party_nit') == nit),
                        'Desconocido'
                    )
                    
                    anomalies.append({
                        'type': 'income_concentration',
                        'severity': 'medium',
                        'title': 'Alta Concentración de Ingresos',
                        'description': f'{concentration*100:.1f}% de tus ingresos provienen de un solo tercero: {third_party_name}',
                        'record_details': {
                            'nit': nit,
                            'name': third_party_name,
                            'amount': amount,
                            'concentration': concentration
                        },
                        'recommendation': 'Verificar que todos los ingresos estén reportados correctamente'
                    })
                    
        except statistics.StatisticsError:
            pass  # No hay suficientes datos para análisis estadístico
        
        return anomalies
    
    def _detect_suspicious_duplicates(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta duplicados sospechosos"""
        anomalies = []
        
        # Agrupar por NIT y monto para detectar duplicados exactos
        nit_amount_groups = defaultdict(list)
        for i, record in enumerate(records):
            nit = record.get('third_party_nit', '')
            amount = record.get('gross_amount', 0)
            key = f"{nit}_{amount}"
            nit_amount_groups[key].append((i, record))
        
        # Detectar duplicados exactos
        for key, group in nit_amount_groups.items():
            if len(group) > 1:
                nit, amount_str = key.split('_')
                amount = float(amount_str) if amount_str.replace('.', '').isdigit() else 0
                
                anomalies.append({
                    'type': 'exact_duplicate',
                    'severity': 'high',
                    'title': 'Posible Duplicado Detectado',
                    'description': f'Mismo tercero (NIT: {nit}) con el mismo monto (${amount:,.0f}) aparece {len(group)} veces',
                    'record_details': {
                        'nit': nit,
                        'amount': amount,
                        'occurrences': len(group),
                        'record_indices': [i for i, _ in group]
                    },
                    'recommendation': 'Verificar si son registros diferentes o duplicados por error'
                })
        
        # Detectar nombres similares con NITs diferentes (posibles errores)
        name_groups = defaultdict(list)
        for i, record in enumerate(records):
            name = record.get('third_party_name', '').strip().upper()
            if name and len(name) > 5:  # Solo nombres significativos
                name_groups[name].append((i, record))
        
        for name, group in name_groups.items():
            if len(group) > 1:
                nits = set(record.get('third_party_nit', '') for _, record in group)
                if len(nits) > 1:  # Mismo nombre, diferentes NITs
                    anomalies.append({
                        'type': 'name_nit_mismatch',
                        'severity': 'medium',
                        'title': 'Inconsistencia Nombre-NIT',
                        'description': f'El nombre "{name}" aparece con diferentes NITs: {", ".join(nits)}',
                        'record_details': {
                            'name': name,
                            'nits': list(nits),
                            'record_indices': [i for i, _ in group]
                        },
                        'recommendation': 'Verificar que los NITs sean correctos para esta empresa'
                    })
        
        return anomalies
    
    def _detect_data_inconsistencies(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta inconsistencias en los datos"""
        anomalies = []
        
        for i, record in enumerate(records):
            # Retenciones mayores que ingresos brutos
            gross_amount = record.get('gross_amount', 0)
            withholding = record.get('withholding_amount', 0)
            
            if withholding > gross_amount and gross_amount > 0:
                anomalies.append({
                    'type': 'withholding_exceeds_gross',
                    'severity': 'high',
                    'title': 'Retención Mayor que Ingreso Bruto',
                    'description': f'Retención de ${withholding:,.0f} es mayor que ingreso bruto de ${gross_amount:,.0f}',
                    'record_details': {
                        'record_index': i,
                        'nit': record.get('third_party_nit', ''),
                        'name': record.get('third_party_name', ''),
                        'gross_amount': gross_amount,
                        'withholding': withholding
                    },
                    'recommendation': 'Verificar los montos - esto indica un posible error'
                })
            
            # Retenciones inusualmente altas (más del 50%)
            if gross_amount > 0 and withholding > 0:
                retention_rate = withholding / gross_amount
                if retention_rate > 0.5:  # Más del 50%
                    anomalies.append({
                        'type': 'high_withholding_rate',
                        'severity': 'medium',
                        'title': 'Tasa de Retención Inusualmente Alta',
                        'description': f'Retención del {retention_rate*100:.1f}% es superior al promedio',
                        'record_details': {
                            'record_index': i,
                            'nit': record.get('third_party_nit', ''),
                            'name': record.get('third_party_name', ''),
                            'retention_rate': retention_rate
                        },
                        'recommendation': 'Revisar si la tasa de retención es correcta para este tipo de ingreso'
                    })
            
            # NITs con formato sospechoso
            nit = record.get('third_party_nit', '')
            if nit in self.known_patterns['suspicious_nits']:
                anomalies.append({
                    'type': 'suspicious_nit_format',
                    'severity': 'high',
                    'title': 'NIT con Formato Sospechoso',
                    'description': f'NIT "{nit}" tiene un formato que podría indicar datos de prueba',
                    'record_details': {
                        'record_index': i,
                        'nit': nit,
                        'name': record.get('third_party_name', '')
                    },
                    'recommendation': 'Verificar que sea un NIT real y válido'
                })
        
        return anomalies
    
    def _detect_suspicious_patterns(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta patrones sospechosos en los datos"""
        anomalies = []
        
        # Detectar números redondos sospechosos
        round_number_count = 0
        total_records = len(records)
        
        for record in records:
            amount = record.get('gross_amount', 0)
            if amount in self.known_patterns['round_numbers']:
                round_number_count += 1
        
        if total_records > 0 and round_number_count / total_records > 0.3:  # Más del 30%
            anomalies.append({
                'type': 'excessive_round_numbers',
                'severity': 'medium',
                'title': 'Muchos Números Redondos',
                'description': f'{round_number_count} de {total_records} registros tienen montos exactamente redondos',
                'record_details': {
                    'round_count': round_number_count,
                    'total_count': total_records,
                    'percentage': round_number_count / total_records * 100
                },
                'recommendation': 'Los montos muy redondos pueden indicar estimaciones en lugar de valores reales'
            })
        
        # Detectar empresas de prueba
        for i, record in enumerate(records):
            name = record.get('third_party_name', '').upper()
            if any(test_word in name for test_word in self.known_patterns['test_companies']):
                anomalies.append({
                    'type': 'test_company_detected',
                    'severity': 'critical',
                    'title': 'Empresa de Prueba Detectada',
                    'description': f'El nombre "{name}" parece ser una empresa de prueba',
                    'record_details': {
                        'record_index': i,
                        'nit': record.get('third_party_nit', ''),
                        'name': name
                    },
                    'recommendation': 'Eliminar datos de prueba antes de la declaración real'
                })
        
        return anomalies
    
    def _detect_missing_critical_data(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta falta de información crítica"""
        anomalies = []
        
        missing_nits = 0
        missing_names = 0
        missing_concepts = 0
        
        for record in records:
            if not record.get('third_party_nit', '').strip():
                missing_nits += 1
            
            if not record.get('third_party_name', '').strip():
                missing_names += 1
                
            if not record.get('concept_code', '').strip():
                missing_concepts += 1
        
        total_records = len(records)
        
        if missing_nits > 0:
            anomalies.append({
                'type': 'missing_nits',
                'severity': 'high',
                'title': 'NITs Faltantes',
                'description': f'{missing_nits} de {total_records} registros no tienen NIT del tercero',
                'record_details': {
                    'missing_count': missing_nits,
                    'total_count': total_records
                },
                'recommendation': 'Los NITs son obligatorios para validar la información'
            })
        
        if missing_names > total_records * 0.1:  # Más del 10% sin nombres
            anomalies.append({
                'type': 'missing_names',
                'severity': 'medium',
                'title': 'Nombres de Terceros Faltantes',
                'description': f'{missing_names} registros no tienen nombre del tercero',
                'record_details': {
                    'missing_count': missing_names,
                    'total_count': total_records
                },
                'recommendation': 'Los nombres ayudan a validar la consistencia de los datos'
            })
        
        return anomalies
    
    def _validate_cedulas_coherence(self, cedulas_totals: Dict[str, Dict]) -> List[Dict]:
        """Valida coherencia entre cédulas tributarias"""
        anomalies = []
        
        # Verificar si hay ingresos en cédulas inesperadas
        total_ingresos = sum(
            cedula.get('ingresos_brutos', 0) 
            for cedula in cedulas_totals.values()
        )
        
        if total_ingresos == 0:
            anomalies.append({
                'type': 'no_income_detected',
                'severity': 'critical',
                'title': 'No se Detectaron Ingresos',
                'description': 'No se encontraron ingresos válidos en ninguna cédula tributaria',
                'record_details': cedulas_totals,
                'recommendation': 'Verificar que el archivo de exógena contenga datos válidos'
            })
        
        # Detectar desproporción entre cédulas
        rentas_trabajo = cedulas_totals.get('rentas_trabajo', {}).get('ingresos_brutos', 0)
        rentas_capital = cedulas_totals.get('rentas_capital', {}).get('ingresos_brutos', 0)
        
        if total_ingresos > 0:
            ratio_capital = rentas_capital / total_ingresos
            
            if ratio_capital > 0.7:  # Más del 70% son rentas de capital
                anomalies.append({
                    'type': 'high_capital_income_ratio',
                    'severity': 'medium',
                    'title': 'Alta Proporción de Rentas de Capital',
                    'description': f'{ratio_capital*100:.1f}% de tus ingresos son rentas de capital',
                    'record_details': {
                        'capital_income': rentas_capital,
                        'total_income': total_ingresos,
                        'ratio': ratio_capital
                    },
                    'recommendation': 'Verificar la clasificación de ingresos - la mayoría suelen ser laborales'
                })
        
        return anomalies
    
    def _detect_classification_errors(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """Detecta posibles errores de clasificación"""
        anomalies = []
        
        # Detectar clasificaciones con baja confianza
        low_confidence_count = 0
        
        for i, record in enumerate(records):
            # Si el parser incluye información de confianza
            if hasattr(record, 'classification_confidence'):
                confidence = record.get('classification_confidence', 1.0)
                if confidence < 0.7:  # Menos del 70% de confianza
                    low_confidence_count += 1
                    
                    anomalies.append({
                        'type': 'low_classification_confidence',
                        'severity': 'medium',
                        'title': 'Clasificación Incierta',
                        'description': f'La clasificación automática tiene solo {confidence*100:.1f}% de confianza',
                        'record_details': {
                            'record_index': i,
                            'nit': record.get('third_party_nit', ''),
                            'name': record.get('third_party_name', ''),
                            'confidence': confidence,
                            'classification': record.get('income_type', '')
                        },
                        'recommendation': 'Revisar manualmente la clasificación de este ingreso'
                    })
        
        return anomalies
    
    def _calculate_risk_score(self, anomalies: List[Dict]) -> Dict[str, Any]:
        """Calcula un score de riesgo basado en las anomalías encontradas"""
        if not anomalies:
            return {
                'score': 0,
                'level': 'low',
                'description': 'No se detectaron anomalías significativas'
            }
        
        # Calcular score ponderado
        total_weight = sum(
            self.severity_levels.get(anomaly['severity'], {}).get('weight', 1)
            for anomaly in anomalies
        )
        
        # Normalizar a escala 0-100
        max_possible_weight = len(anomalies) * 4  # Máximo si todas fueran críticas
        score = min(100, (total_weight / max_possible_weight) * 100) if max_possible_weight > 0 else 0
        
        # Determinar nivel de riesgo
        if score < 20:
            level = 'low'
            description = 'Riesgo bajo - Anomalías menores detectadas'
        elif score < 50:
            level = 'medium'
            description = 'Riesgo medio - Requiere revisión'
        elif score < 80:
            level = 'high'
            description = 'Riesgo alto - Revisión detallada recomendada'
        else:
            level = 'critical'
            description = 'Riesgo crítico - Revisión inmediata necesaria'
        
        return {
            'score': round(score, 1),
            'level': level,
            'description': description,
            'total_anomalies': len(anomalies),
            'by_severity': Counter(anomaly['severity'] for anomaly in anomalies)
        }
    
    def _generate_recommendations(self, anomalies: List[Dict], risk_score: Dict) -> List[Dict]:
        """Genera recomendaciones basadas en las anomalías"""
        recommendations = []
        
        if risk_score['level'] == 'critical':
            recommendations.append({
                'type': 'urgent_review',
                'priority': 'high',
                'title': 'Revisión Urgente Requerida',
                'description': 'Se detectaron anomalías críticas que requieren atención inmediata',
                'action': 'Revisar todos los datos antes de proceder con la declaración'
            })
        
        # Contar tipos de anomalías para recomendaciones específicas
        anomaly_types = Counter(anomaly['type'] for anomaly in anomalies)
        
        if anomaly_types.get('exact_duplicate', 0) > 0:
            recommendations.append({
                'type': 'duplicates_review',
                'priority': 'high',
                'title': 'Revisar Duplicados',
                'description': 'Se encontraron registros duplicados que podrían inflar los ingresos',
                'action': 'Eliminar registros duplicados antes de continuar'
            })
        
        if anomaly_types.get('withholding_exceeds_gross', 0) > 0:
            recommendations.append({
                'type': 'amounts_verification',
                'priority': 'high', 
                'title': 'Verificar Montos',
                'description': 'Hay inconsistencias en montos de ingresos y retenciones',
                'action': 'Validar que todos los montos sean correctos'
            })
        
        if risk_score['level'] in ['low', 'medium']:
            recommendations.append({
                'type': 'proceed_with_caution',
                'priority': 'medium',
                'title': 'Proceder con Precaución',
                'description': 'Los datos parecen correctos pero se encontraron algunas inconsistencias menores',
                'action': 'Revisar las anomalías señaladas y proceder'
            })
        
        return recommendations
    
    def _generate_summary(self, anomalies: List[Dict], risk_score: Dict) -> Dict[str, Any]:
        """Genera resumen ejecutivo de las anomalías"""
        return {
            'total_anomalies': len(anomalies),
            'risk_level': risk_score['level'],
            'risk_score': risk_score['score'],
            'main_issues': [
                anomaly['title'] for anomaly in anomalies 
                if anomaly['severity'] in ['high', 'critical']
            ][:3],  # Top 3 issues
            'recommended_action': 'review' if risk_score['level'] in ['high', 'critical'] else 'proceed',
            'confidence_level': 'high' if risk_score['level'] == 'low' else 'medium' if risk_score['level'] == 'medium' else 'low'
        }
    
    def _empty_response(self, message: str) -> Dict[str, Any]:
        """Respuesta vacía con mensaje"""
        return {
            'success': True,
            'anomalies_count': 0,
            'risk_score': {'score': 0, 'level': 'low', 'description': message},
            'anomalies': [],
            'recommendations': [],
            'summary': {'total_anomalies': 0, 'risk_level': 'low'},
            'analysis_date': datetime.now().isoformat()
        }


# Instancia singleton del detector
_anomaly_detector = None

def get_anomaly_detector() -> AnomalyDetector:
    """Factory function para obtener instancia del detector"""
    global _anomaly_detector
    
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    
    return _anomaly_detector
