Historias de Usuario para el MVP de AccountIA
Versión: 1.0
Fecha: 18 de junio de 2025
Propósito: Este documento desglosa las funcionalidades definidas en el PRD en historias de usuario accionables. Cada historia representa un pequeño entregable de valor desde la perspectiva del usuario y servirá como base para la planificación del desarrollo.
Formato: Como un [tipo de usuario], quiero [realizar una acción] para poder [obtener un beneficio].

Epic 1: Onboarding y Autenticación de Usuarios
(Objetivo: Permitir que los usuarios se registren de forma segura y accedan a la aplicación).
HU-01: Visualización de la Propuesta de Valor

Como un visitante que llega a la página de aterrizaje,
quiero entender claramente qué hace AccountIA, para quién es y por qué es seguro,
para poder tomar la decisión de registrarme con confianza.
Criterios de Aceptación (AC):
El titular principal comunica la Propuesta de Valor Única.
Se explica el proceso en 3 pasos simples.
Se muestran insignias o menciones de seguridad (ej: "Datos Cifrados", "Cumple Ley 1581").
El botón de "Empieza Gratis" (Call to Action) es claramente visible.
HU-02: Registro de Cuenta Nueva

Como un nuevo visitante,
quiero registrar una cuenta usando mi correo electrónico y una contraseña segura,
para poder acceder a las funcionalidades de la aplicación.
AC:
El formulario de registro solicita nombre, email y contraseña.
La contraseña tiene un requisito mínimo de seguridad (ej: 8 caracteres).
Se valida que el formato del email sea correcto.
Si el email ya existe, se muestra un error amigable.
Al registrarse exitosamente, soy redirigido al panel de usuario (dashboard).
HU-03: Inicio de Sesión

Como un usuario ya registrado,
quiero iniciar sesión con mi correo y contraseña,
para poder acceder a mi panel personal y continuar con mi declaración.
AC:
Si las credenciales son correctas, soy redirigido al dashboard.
Si las credenciales son incorrectas, se muestra un mensaje de error claro.
HU-04: Recuperación de Contraseña

Como un usuario registrado que olvidó su contraseña,
quiero un enlace de "Olvidé mi contraseña" para poder restablecerla a través de mi correo,
para poder recuperar el acceso a mi cuenta.
AC:
El flujo solicita mi email.
Recibo un correo con un enlace único y de tiempo limitado para restablecer la contraseña.
El enlace me lleva a una página para crear una nueva contraseña.
Epic 2: Panel de Usuario y Gestión de Declaraciones
(Objetivo: Ofrecer un punto de partida claro y sencillo para los usuarios que inician sesión).
HU-05: Vista del Dashboard Principal
Como un usuario que ha iniciado sesión,
quiero ver un panel de control limpio y con una acción principal clara,
para poder saber inmediatamente cómo empezar mi declaración de renta.
AC:
Se muestra un mensaje de bienvenida con mi nombre.
Un botón grande y prominente dice "Crear mi Declaración 2024".
No hay otra información que me distraiga en el MVP.
Epic 3: Creación de Declaración - Carga y Análisis de Exógena
(Objetivo: Implementar el "gancho" principal de la aplicación: el análisis automático del reporte de la DIAN).
HU-06: Carga del Archivo de Información Exógena

Como un usuario que inicia una nueva declaración,
quiero subir fácilmente mi archivo de información exógena en formato Excel,
para poder que la aplicación extraiga mis datos de forma automática.
AC:
La interfaz presenta un área para arrastrar y soltar (drag-and-drop) o un botón para seleccionar el archivo.
Se valida que el archivo sea de un formato compatible (.xlsx, .xls).
Se muestra una barra de progreso o animación mientras el archivo se sube.
HU-07: Procesamiento y Confirmación de Datos Extraídos

Como un usuario que ha subido su archivo,
quiero ver un resumen de los datos clave que la IA extrajo,
para poder confirmar que la información es correcta antes de continuar.
AC:
Mientras el backend procesa, se muestra un mensaje como "Nuestra IA está analizando tu información...".
Al finalizar, se muestra un resumen claro: "Hemos encontrado: Ingresos por $X, Retenciones por $Y".
Si el archivo está corrupto o no se puede leer, se muestra un error claro con posibles soluciones.
Epic 4: Asistente Guiado por IA y Carga de Soportes
(Objetivo: Guiar al usuario a través del proceso de completar la información faltante para su declaración).
HU-08: Interacción con el Asistente IA

Como un usuario,
quiero que el asistente de IA me haga preguntas simples y contextuales basadas en mis datos,
para poder identificar qué información adicional o deducciones aplican a mi caso.
AC:
La IA presenta preguntas de una en una (ej: "¿Tienes un crédito hipotecario?").
Las respuestas son simples (Sí/No, opciones múltiples).
El flujo de preguntas se adapta basado en mis respuestas.
HU-09: Carga de Documentos de Soporte

Como un usuario,
quiero que la aplicación me solicite y me permita adjuntar los documentos de soporte necesarios (certificados, facturas),
para poder tener un respaldo de mis deducciones y tener todo organizado.
AC:
La opción de carga aparece contextualmente (ej: después de responder "Sí" a "¿Tienes medicina prepagada?").
Se aceptan formatos comunes (PDF, JPG, PNG).
Se muestra una confirmación visual cuando un archivo se ha subido correctamente.
Epic 5: Visualización y Finalización de la Declaración
(Objetivo: Mostrar el valor final al usuario y convertirlo en un cliente de pago).
HU-10: Visualización del Borrador Simplificado

Como un usuario que ha completado la guía,
quiero ver un borrador resumido de mi declaración en un lenguaje fácil de entender,
para poder conocer el resultado (impuesto a pagar o saldo a favor) antes de finalizar.
AC:
Se muestra una vista simplificada del Formulario 210.
Se explican los renglones clave con textos de ayuda.
El resultado final (impuesto/saldo) se muestra de forma destacada.
HU-11: Opción de Pago para Informe Final

Como un usuario satisfecho con el borrador,
quiero tener una opción clara para realizar un pago,
para poder desbloquear y descargar el reporte final detallado de mi declaración.
AC:
Se muestra claramente lo que incluye el pago (Reporte PDF, resumen de soportes, etc.).
El precio es visible.
Un botón "Pagar y Descargar Reporte" inicia el flujo de pago (la integración con la pasarela de pagos puede ser una historia separada).
Priorización para el MVP
Para lanzar una primera versión funcional que valide la idea, el equipo debe enfocarse en el "camino feliz" completo.
Prioridad Máxima (El Core Loop): HU-02, HU-03, HU-05, HU-06, HU-07, HU-10, HU-11. Esto prueba que el flujo principal, desde el registro hasta la conversión, funciona.
Prioridad Alta (Funcionalidad Esencial): HU-01, HU-04, HU-08, HU-09. Son necesarios para una experiencia de usuario completa y para cumplir la promesa de la IA.
A Considerar Post-MVP: Funcionalidades como un dashboard con historial detallado, edición de datos ya cargados, eliminación de cuenta, etc., pueden ser desarrolladas en versiones futuras.
