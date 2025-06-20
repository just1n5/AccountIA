Documento de Requisitos de Producto (PRD) Simplificado - AccountIA
Versión: 1.0
Fecha: 18 de junio de 2025
Propósito: Este es un documento vivo que define el Producto Mínimo Viable (MVP) para AccountIA. Sirve como la fuente única de verdad para el equipo de desarrollo, alineando la visión de producto con los objetivos de negocio y las necesidades del usuario.

1. Visión del Producto y Propuesta de Valor Única (UVP)
   Visión: Ser la herramienta digital de referencia en Colombia para que cualquier persona natural pueda entender, preparar y optimizar su declaración de renta con confianza y sin estrés.
   Propuesta de Valor Única: AccountIA es tu asesor fiscal personal impulsado por IA. Transformamos el complejo proceso de la declaración de renta en un flujo guiado, simple y rápido, usando tu propia información de la DIAN para maximizar tus deducciones y asegurar tu tranquilidad.
   Concepto de Alto Nivel: Un "TurboTax" inteligente y localizado para el contribuyente colombiano.
2. Lean Canvas de AccountIA
   Problema
   Solución (Características Clave del MVP)
   Métricas Clave
   Propuesta de Valor Única
   Ventaja Injusta (Diferencial Difícil de Copiar)
   Canales
   Segmentos de Clientes
3. La declaración de renta en Colombia es un proceso complejo, opaco y genera ansiedad.
4. Los contribuyentes desconocen las deducciones y beneficios a los que tienen derecho, perdiendo dinero.
5. Contratar un contador es costoso para declaraciones de complejidad media/baja.
6. Las herramientas de la DIAN (Muisca) no son intuitivas.
7. Carga y Análisis Automatizado: El usuario sube su archivo de información exógena (Excel DIAN) y la IA extrae y categoriza los datos automáticamente.
8. Asistente Guiado por IA: Un flujo paso a paso que "conversa" con el usuario, solicitando documentos de soporte específicos (ej: "Veo un crédito hipotecario, ¿tienes el certificado de intereses?").
9. Motor de Borrador Simplificado: Generación de un borrador claro y entendible de la declaración, explicando los renglones más importantes.
10. Bóveda Segura de Documentos: Un espacio para que el usuario guarde los soportes de su declaración actual y futuras.

- Tasa de Activación: % de usuarios registrados que suben exitosamente su archivo de exógena.
- Tasa de Conversión: % de usuarios que, tras ver el borrador, pagan para obtener el reporte final.
- Tiempo de Completado: Tiempo promedio desde el registro hasta la generación del borrador.
- Feedback Cualitativo / NPS: Medir la confianza y claridad percibida por los usuarios.
  Tu asesor fiscal personal con IA.

Declaración de renta simple, rápida y optimizada.

- Foco exclusivo en el ecosistema fiscal colombiano: Profundo conocimiento de las normativas locales (Estatuto Tributario).
- Lógica de IA propietaria: Un pipeline RAG entrenado y validado con las particularidades de Colombia, que mejora con cada declaración.
- Experiencia de Usuario (UX) Superior: Obsesión por hacer el proceso fácil y generar confianza, algo que los competidores grandes o incumbentes suelen descuidar.
- Marketing de Contenidos: Blog y videos explicando temas fiscales (SEO).
- Publicidad Digital: Anuncios en Google y redes sociales (Meta) segmentados por intereses.
- Redes Profesionales: Presencia en LinkedIn.
- Programa de Referidos: Incentivar el boca a boca.
  Personas Naturales en Colombia que deban declarar renta:

1. Profesionales Dependientes e Independientes: Empleados con ingresos adicionales, freelancers. Buscan eficiencia y optimización sin el costo de un contador fijo.

2. Declarantes por Primera Vez: Jóvenes profesionales que se enfrentan al proceso por primera vez y se sienten abrumados.

---

Early Adopters: Profesionales tech-savvy entre 25-45 años que ya usan soluciones digitales para sus finanzas (ej. apps de inversión, neobancos).

Estructura de Costos
Flujos de Ingreso

- Costos de Infraestructura (Google Cloud): Cloud Run, Cloud SQL (PostgreSQL), Cloud Storage.
- Costos de API de IA (Google Gemini / Vertex AI): Costo variable por uso.
- Equipo (Fijo): Salarios de los 2 desarrolladores.
- Marketing y Publicidad: Presupuesto para campañas de adquisición.
- Costos Legales y Contables: Asesoría para la creación de la empresa y cumplimiento.
  Modelo Freemium / Tiered:

- Plan Gratuito (El Gancho):

* Registro y subida de exógena.
* Visualización de un resumen de ingresos y retenciones.
* Diagnóstico inicial de la IA ("Necesitarás estos 3 documentos").

- Plan "Declara Seguro" (Pago único por declaración):

* Todas las funcionalidades del plan gratuito.
* Generación del borrador detallado de la declaración.
* Recomendaciones de optimización y deducciones.
* Exportación de un reporte final en PDF.

3. Funcionalidades Detalladas del MVP
   Página de Aterrizaje (Landing Page):
   Propósito: Comunicar la UVP y generar confianza.
   Contenido:
   Título claro: "Tu declaración de renta, por fin simple".
   Explicación en 3 pasos: 1. Sube tu exógena, 2. Responde a las preguntas de nuestra IA, 3. Obtén tu borrador optimizado.
   Menciones explícitas a la seguridad y cumplimiento con la ley colombiana.
   CTA principal: "Empieza Gratis".
   Autenticación de Usuarios:
   Tecnología: Google Firebase Authentication.
   Flujo: Registro con Email/Contraseña y/o Google. Inicio de sesión y recuperación de contraseña.
   Panel de Usuario (Dashboard):
   Vista Principal: Bienvenida al usuario.
   Acción Principal: Un botón grande y visible: "Crear mi Declaración 2024".
   Historial (Post-MVP): En el MVP, esta sección puede estar vacía o indicar "Aquí verás tus declaraciones anteriores".
   Flujo de Creación de Declaración (MVP enfocado en "Declaración Guiada"):
   Paso 1: Carga de Exógena: El usuario sube el archivo Excel. Se muestra un spinner de carga mientras el backend procesa.
   Paso 2: Validación y Resumen: La app muestra los datos clave extraídos: "Confirmamos Ingresos por X, Retenciones por Y".
   Paso 3: Asistente IA:
   La IA hace preguntas simples basadas en los datos: "¿Estos ingresos por servicios profesionales son tu única actividad? ¿Pagaste seguridad social como independiente?".
   El sistema solicita documentos de soporte: "Para deducir los intereses de tu crédito, por favor sube el certificado del banco aquí". El usuario adjunta PDFs o imágenes.
   Paso 4: Generación del Borrador:
   Se presenta una vista simplificada del Formulario 210, explicando en lenguaje llano qué significa cada renglón importante.
   Se muestra un cálculo del impuesto a pagar o saldo a favor.
   Se presenta la opción de pago para desbloquear la descarga del informe final en PDF.
4. Requisitos No Funcionales (MVP)
   Seguridad: Cifrado de documentos en reposo (en GCS) y en tránsito (HTTPS/TLS). Los datos sensibles en la BD (PostgreSQL) deben estar igualmente protegidos.
   Privacidad: Cumplimiento estricto con la Ley 1581 de 2012 (Habeas Data). La política de privacidad debe ser clara y accesible.
   Rendimiento: El procesamiento del archivo Excel no debe tardar más de 30-45 segundos para el MVP. La interfaz debe ser rápida y responsiva.
   Usabilidad: La aplicación debe ser usable por alguien sin conocimientos contables. El lenguaje debe ser simple, evitando la jerga fiscal siempre que sea posible.
