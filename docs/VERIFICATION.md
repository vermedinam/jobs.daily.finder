# Verificación y cobertura

La fecha de referencia es el día local en America/Los_Angeles al comenzar el run. Timestamps ISO con offset se convierten a California; una fecha ISO sin hora se conserva tal como la declara la fuente. Timestamps sin zona, fechas relativas, fechas ausentes y fechas de actualización no son evidencia de publicación.

Greenhouse: descubre mediante listado público, consulta el detalle oficial y requiere `first_published` del día. Nunca utiliza `updated_at`. Verifica disponibilidad del enlace y que la página/destino contenga el ID de la vacante; una página genérica sin identidad comprobable se excluye. Salario: `pay_input_ranges` con `pay_transparency=true`.

Ashby: descubre mediante API pública, requiere `isListed` y verifica `JobPosting.datePosted` en la página oficial. **`publishedAt` significa última publicación**, por lo que no se utiliza para afirmar publicación original hoy. Sin datos estructurados verificables, queda fuera. Su salario solo se toma de datos oficiales. El resultado puede ser cero aun cuando el ATS tenga vacantes.

LinkedIn: intenta búsquedas públicas por cada título en California, Estados Unidos, Canadá, México y LATAM con filtro de últimas 24 horas. Este filtro solo sirve para descubrir, no verifica una fecha. Si hay bloqueo, 401/403 o error, deja de consultar y lo informa, sin login, cookies, proxy ni evasión. Los enlaces se adjuntan por coincidencia exacta empresa/título con una vacante oficial ya verificada. También inspecciona enlaces oficiales públicos visibles en la ficha: solo se admite una página con un único `JobPosting`, fecha del día, empresa y título coincidentes. LinkedIn puede ocultar esos enlaces o requerir JavaScript; tales candidatas no se incluyen sin evidencia oficial. La búsqueda pública es limitada a la primera página por título/país, no exhaustiva.

Cada recomendación incluye URL oficial directo, timestamp/fecha original, fuente de evidencia, ubicación, salario o “No publicado”, ID, match y vínculo LinkedIn cuando se encuentra. HTTP 200 no garantiza aceptación de solicitudes: se valida identidad y señales explícitas de cierre; las discrepancias requieren revisión humana. No se garantiza detectar todas las formas de cierre.

Los errores parciales se guardan en el reporte; si ningún tablero oficial funciona, el workflow falla y conserva el dashboard anterior. Consultar su fecha para no confundirlo con un reporte nuevo. No genera vacantes ficticias para llegar a 20.

## Referencias oficiales

- [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html)
- [Ashby Public Job Posting API](https://developers.ashbyhq.com/docs/public-job-posting-api)
- [GitHub Actions timezone support](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/)
- [GitHub workflow schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## Cobertura ampliada y prioridad

California se ordena antes del resto de ubicaciones; dentro de cada grupo se ordena por match. Se admiten USA, Canadá, México y LATAM, manteniendo la fecha oficial solicitada. Nunca se amplía el período para completar 20. Si hay menos coincidencias verificadas, se informa el número real.

SmartRecruiters: paginación hasta 20,000 vacantes por empresa; consulta detalle y `releasedDate`, verifica URL directo e identidad. `releasedDate` es fecha de lanzamiento y puede corresponder a una republicación; se etiqueta explícitamente. No se confunde creación de borrador con publicación.

Los destinos oficiales publicados por las APIs ATS pueden incorporar su dominio exacto a la lista permitida durante esa consulta; se mantiene HTTPS, verificación de IP pública, identidad y control de redirecciones. No se autorizan dominios tomados del texto de una vacante. Los candidatos de LinkedIn siguen limitados a dominios previamente configurados.

Amazon Jobs: búsquedas públicas de Program Manager, Delivery Manager y Producer; usa `posted_date`, la fecha literal publicada por la empresa, sin inferir zona horaria a partir de una hora inexistente. Verifica la ficha oficial y el Job ID. No usa `updated_time` como publicación. Se aceptan TPM y Sr. como abreviaturas de los títulos solicitados. Se conservan rangos de salario oficiales presentes en el anuncio; los ausentes se indican como no publicados.
