# Setup

Requiere Python 3.9 o posterior con base de zonas horarias (GitHub usa Python 3.12). No requiere paquetes de terceros ni claves de búsqueda. No hay servicio que opere hasta publicar y habilitar el workflow.

1. Publicar estos archivos en un repositorio `vermedinam/jobs.daily.finder`. Preferir privado si se conservará historial de aplicaciones; en público todos pueden leer `data/` y los reportes.
2. Revisar `config/sources.json`. Confirmar el slug en la página oficial de cada empresa, y agregar el dominio exacto de destino si usa una página propia. No autorizar dominios de agregadores como fuentes oficiales.
3. Editar las habilidades de `config/profile.json` y marcar `confirmed` true tras revisar el perfil. El algoritmo solo usa esas habilidades y el título; no infiere años de experiencia.
4. Importar aplicaciones previas en `data/applied.json`, usando ID y/o URL oficial. No poner nombres personales, contactos, notas privadas o CV.
5. En Settings → Actions habilitar workflows y permitir el permiso `contents: write` del workflow. Si la rama está protegida, proporcionar un mecanismo aprobado de commit/PR; este workflow no evita protecciones.
6. Abrir Actions → Daily job finder → Run workflow. Revisar el commit, README y `reports/`. La ejecución automática funciona sobre la rama por defecto.
7. Revisar los fallos de fuentes y agregar empresas regularmente. GitHub puede retrasar/omitir ejecuciones por carga y deshabilitar workflows programados en repositorios públicos sin actividad durante 60 días. Revisar Actions si un reporte falta.

Programación: `cron: '0 17 * * *'` más `timezone: America/Los_Angeles`. Mantiene las 17:00 durante PST/PDT. Las vacantes posteriores a esa hora quedan fuera; una ejecución manual posterior amplía el mismo reporte del día. Un run retrasado a otro día usa la fecha real local y nunca atribuye resultados al día anterior.

Para marcar aplicado desde tu copia: ejecutar el comando del README, revisar el archivo y subirlo con un commit. Para hacerlo en GitHub: editar `data/applied.json` con este formato (ejemplo ficticio, no una vacante):

```json
[{"id":"greenhouse:empresa:12345", "official_url":"https://job-boards.greenhouse.io/empresa/jobs/12345", "status":"Applied"}]
```

Para desmarcar, eliminar la entrada. Para usar únicamente URL, omitir ID. Cualquier entrada de este archivo se excluye sin importar la etiqueta `status`; no mezclar pendientes en él.

## Publicar desde una terminal autorizada

```sh
gh auth login
gh repo create vermedinam/jobs.daily.finder --private --source=. --remote=origin --push
gh workflow run daily.yml --repo vermedinam/jobs.daily.finder
```

El comando de creación requiere que esta carpeta tenga un commit Git. Si el repositorio ya existe, revisar su contenido antes de integrar los archivos; no sobrescribir trabajo previo. No copiar un token en el chat ni incluirlo en archivos.
