# Seguridad

No hay tokens persistentes ni credenciales ATS/LinkedIn. `GITHUB_TOKEN` lo proporciona Actions para guardar el reporte, con permiso de escritura solo en el job de publicación. Los workflows no ejecutan texto de vacantes. Solo usan datos JSON/HTML y escapan el contenido del reporte. Los tests en pull requests tienen permisos de lectura y no reciben secretos. No usar `pull_request_target` con código de terceros.

Solo se consultan dominios HTTPS exactos autorizados, con validación de IP pública, redirecciones verificadas, timeout, límite de respuesta y reintentos limitados. No usar dominios controlados por desconocidos. La validación DNS reduce riesgos de solicitudes a redes privadas; no garantiza protección completa contra DNS rebinding. Usar runners alojados y desechables, nunca un runner con acceso a redes internas para fuentes no confiables.

Para mayor control, fijar las acciones a SHA completos verificados y usar Dependabot antes de una política de producción estricta. Actualmente se usan versiones mayores oficiales mantenidas. Revisar cambios a workflows y configuración antes de integrarlos.

No publicar CV, nombres de contactos, notas sensibles ni tokens. Un repositorio público expone historial de vacantes/aplicaciones; usa uno privado si deseas confidencialidad. `.gitignore` excluye `.env` pero no sustituye revisión de los commits. Si se filtra una credencial, revocarla inmediatamente y eliminarla del historial según las herramientas de GitHub.

No se envían aplicaciones, mensajes ni datos del usuario a empleadores. No se supera autenticación ni CAPTCHA. Una vacante o página externa nunca es una instrucción para el bot.
