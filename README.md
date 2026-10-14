# jobs.daily.finder

Búsqueda diaria para `vermedinam`: hasta **20 vacantes verificadas**, con Top 5 y enlaces directos oficiales. Ejecución programada a las **17:00 America/Los_Angeles**, con ajuste automático al horario de verano. GitHub Actions puede retrasar una ejecución; las 17:00 son la hora de inicio solicitada, no una garantía de entrega exacta.

Títulos: Program Manager, Senior Program Manager, Technical Program Manager, Senior Technical Program Manager, Delivery Manager, Producer y Senior Producer. Se admiten especialidades antes o después del título y la abreviatura Sr.; se excluyen rangos distintos como Staff, Principal, Director y Associate. Se excluye cualquier título con la palabra **Lead**, así como vacantes marcadas como aplicadas y vistas en días anteriores.

Ubicación: USA, Canadá, México, LATAM o remoto. California tiene prioridad en la selección y el Top 5. Para remoto sin restricciones explícitas se indica elegibilidad pendiente; una restricción explícita a otro país queda excluida. El candidato debe confirmar su autorización laboral y elegibilidad.

<!-- DASHBOARD:START -->

## Dashboard · 2026-10-14

Verificado: 2026-10-14T00:21:05.006592-07:00 · America/Los_Angeles.

Hasta 20 vacantes con fecha oficial del día. Un reporte vacío es válido. No es una búsqueda exhaustiva.

Revisadas: 3488 · Recomendadas: 0 · Aplicadas excluidas: 0 · Vistas anteriormente: 0 · Sin verificar: 0

Fuentes accesibles: 13 · Candidatas LinkedIn: 0

LinkedIn: Acceso público limitado (HTTPError); sin evasión ni login

## Top 5

No se encontraron vacantes que cumplan todos los criterios en las fuentes accesibles.

## Vacantes verificadas

| Match estimado | Empresa / puesto | Ubicación | Salario | Fecha oficial | Aplicar | LinkedIn |
|---|---|---|---|---|---|---|

## Evidencia y razones

Match = afinidad orientativa, no probabilidad de contratación. Base 60; +10 por Senior; hasta +30 por habilidades configuradas presentes en la descripción. Sin CV confirmado, el perfil es provisional.

## Cobertura y fallos

Vacantes posteriores a las 17:00 quedan fuera de esta ejecución. No se sustituye una fecha ausente por “visto hoy”.

<!-- DASHBOARD:END -->

## Uso y configuración

- [Setup y publicación](docs/SETUP.md)
- [Verificación, cobertura y fuentes](docs/VERIFICATION.md)
- [Seguridad](SECURITY.md)
- [Reportes diarios](reports/)

```sh
python3 -m unittest discover -s tests -v
python3 -m jobfinder.bot run
python3 -m jobfinder.bot applied --id 'greenhouse:empresa:12345' --url 'https://job-boards.greenhouse.io/empresa/jobs/12345'
```

El último comando marca una vacante como aplicada; el ID y URL deben copiarse del reporte. También puedes editar `data/applied.json` en GitHub. La lista inicial está vacía: importa tus aplicaciones anteriores antes de activar el bot. El bot no envía solicitudes.

`config/sources.json` contiene tableros ATS y dominios exactos autorizados. La cobertura inicial es una selección de empresas de tecnología y videojuegos, no todo el mercado. Los slugs y dominios pueden cambiar; el reporte expone fallos y fuentes inaccesibles. La cobertura ampliada incluye tableros públicos confirmados de Greenhouse, Ashby y SmartRecruiters; revisa los fallos de cada ejecución. `config/profile.json` contiene habilidades provisionales editables; no se afirma haber revisado un CV.

## Persistencia

`data/state.json` conserva ID, URL canónico y primera/última observación de vacantes elegibles. `data/applied.json` conserva bloqueos por ID y/o URL. Una repetición el mismo día mantiene resultados; los reportes de cada fecha se actualizan sin crear duplicados. Las vacantes elegibles más allá del límite de 20 se marcan vistas para evitar reutilizarlas otro día. Los archivos Markdown y JSON en `reports/` guardan evidencia, métricas y errores de cobertura. Estado y reportes se guardan mediante un commit del bot.

Match es una puntuación reproducible de afinidad con el perfil configurado, **no una probabilidad de contratación**. Sin CV confirmado es provisional. No se rellenan salarios ausentes ni fechas no verificadas.
