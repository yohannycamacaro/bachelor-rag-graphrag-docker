# Catalogo de casos tecnicos Docker

Este catalogo resume los casos que usaremos para construir y evaluar la base de
conocimiento de soporte tecnico.

## Caso 1: Docker daemon no responde

- Problema: el usuario recibe `Cannot connect to the Docker daemon`.
- Componentes: Docker client, Docker daemon, Docker host.
- Posibles causas: daemon detenido, `DOCKER_HOST` incorrecto, host remoto no
  alcanzable.
- Diagnostico: `docker info`, estado del servicio, revisar `DOCKER_HOST`.
- Solucion esperada: iniciar el servicio o corregir la conexion al daemon.

## Caso 2: Un servicio no alcanza a otro por service name

- Problema: `web` no puede conectarse a `db` usando el nombre del servicio.
- Componentes: Compose network, internal DNS, service name.
- Posibles causas: servicios en redes distintas, red custom mal configurada,
  uso de IP en vez de service name.
- Diagnostico: `docker network inspect`, revisar `networks`, probar desde dentro
  del container.
- Solucion esperada: usar service name y asegurar red compartida.

## Caso 3: Confusion entre host port y container port

- Problema: desde el host funciona `localhost:8001`, pero desde otro container no.
- Componentes: host port, container port, Compose network.
- Posibles causas: usar el puerto publicado del host dentro de la red Docker.
- Diagnostico: `docker compose port`, revisar `ports`.
- Solucion esperada: entre servicios usar `service_name:container_port`.

## Caso 4: Variable `.env` no visible dentro del container

- Problema: una variable existe en `.env`, pero la aplicacion no la ve.
- Componentes: `.env`, interpolation, runtime container environment.
- Posibles causas: la variable solo se uso para interpolar el Compose file.
- Diagnostico: `docker compose config --environment`, inspeccionar variables
  dentro del container.
- Solucion esperada: definir la variable en `environment` o `env_file`.

## Caso 5: Valor de variable inesperado por precedencia

- Problema: Compose usa un valor distinto al esperado.
- Componentes: shell, `.env`, `--env-file`, `environment`, `env_file`, image
  `ENV`.
- Posibles causas: una fuente con mayor precedencia sobrescribe otra.
- Diagnostico: comparar fuentes y revisar el modelo resuelto.
- Solucion esperada: definir una fuente autoritativa y documentar la prioridad.

## Caso 6: Nombre de proyecto inesperado

- Problema: containers o networks tienen prefijos inesperados.
- Componentes: project name, `COMPOSE_PROJECT_NAME`, `-p`, top-level `name`.
- Posibles causas: directorio actual o variable de entorno cambia el nombre del
  proyecto.
- Diagnostico: revisar `-p`, `COMPOSE_PROJECT_NAME`, nombre del directorio.
- Solucion esperada: fijar el project name explicitamente.

## Caso 7: Compose usa otro archivo

- Problema: los cambios en `compose.yaml` no parecen aplicarse.
- Componentes: `COMPOSE_FILE`, opcion `-f`, file discovery.
- Posibles causas: otro archivo seleccionado o multiples archivos fusionados.
- Diagnostico: revisar `COMPOSE_FILE`, `-f`, `docker compose config`.
- Solucion esperada: hacer explicito el archivo usado.

## Caso 8: Servicio no inicia por profile

- Problema: un servicio esta definido pero no arranca.
- Componentes: Compose profiles, `COMPOSE_PROFILES`, `--profile`.
- Posibles causas: el profile requerido no esta activo.
- Diagnostico: revisar `profiles` y variables de Compose.
- Solucion esperada: habilitar el profile o quitar la restriccion.

## Caso 9: Aplicacion inicia antes que la base de datos

- Problema: `web` inicia antes de que `db` acepte conexiones.
- Componentes: `depends_on`, healthcheck, service readiness.
- Posibles causas: el container esta iniciado pero no sano/listo.
- Diagnostico: logs, healthcheck, configuracion `depends_on`.
- Solucion esperada: usar healthcheck y `condition: service_healthy`.

## Caso 10: Container marcado como unhealthy

- Problema: el proceso corre, pero Docker marca el container como `unhealthy`.
- Componentes: healthcheck command, endpoint, port, timeout, retries.
- Posibles causas: healthcheck prueba el endpoint incorrecto o tiene timing malo.
- Diagnostico: logs y salida del healthcheck.
- Solucion esperada: ajustar comando y tiempos del healthcheck.

## Caso 11: Datos desaparecen al recrear container

- Problema: los datos se pierden despues de recrear el container.
- Componentes: writable layer, named volume, bind mount.
- Posibles causas: datos escritos solo dentro del container.
- Diagnostico: revisar mounts y ruta donde escribe la aplicacion.
- Solucion esperada: usar volume o bind mount persistente.

## Caso 12: Elegir entre bind mount y volume

- Problema: no esta claro que tipo de storage usar.
- Componentes: host path, Docker-managed volume.
- Posibles causas: se mezclan necesidades de persistencia y acceso desde host.
- Diagnostico: decidir si el host debe editar/acceder directamente a archivos.
- Solucion esperada: bind mount para acceso directo desde host; volume para datos
  gestionados por Docker.

## Caso 13: Mount oculta archivos del image

- Problema: archivos del image desaparecen al montar un volume en la misma ruta.
- Componentes: mount target, image filesystem, volume.
- Posibles causas: el mount cubre un directorio que ya tenia contenido.
- Diagnostico: comparar container con y sin mount.
- Solucion esperada: cambiar target path o inicializar el volume.

## Caso 14: tmpfs no persiste

- Problema: datos guardados en tmpfs desaparecen.
- Componentes: tmpfs mount, memoria, storage temporal.
- Posibles causas: tmpfs es efimero por diseno.
- Diagnostico: revisar tipo de mount.
- Solucion esperada: usar volume o bind mount si los datos deben persistir.

## Caso 15: Diferenciar DNS externo y service discovery

- Problema: fallan nombres dentro del container.
- Componentes: daemon DNS, Compose internal DNS, network membership.
- Posibles causas: DNS externo mal configurado o servicios en redes distintas.
- Diagnostico: probar dominio externo y service name por separado.
- Solucion esperada: configurar DNS del daemon para dominios externos o corregir
  red compartida para service names.

## Caso 16: External network no existe

- Problema: Compose falla porque referencia una red externa inexistente.
- Componentes: external network, Compose networks.
- Posibles causas: la red esta marcada como `external`, pero no fue creada antes.
- Diagnostico: revisar `networks`, listar redes Docker, comparar nombres.
- Solucion esperada: crear la red con `docker network create` o dejar que Compose
  la gestione.

## Caso 17: Mismo setup cambia al ejecutarse desde otro directorio

- Problema: el mismo proyecto Compose se comporta distinto desde otra carpeta.
- Componentes: project directory, `.env`, `COMPOSE_FILE`, project name.
- Posibles causas: Compose encuentra otra configuracion, otra `.env` o usa otro
  nombre de proyecto.
- Diagnostico: revisar directorio actual, `COMPOSE_FILE`, `.env`,
  `docker compose config`.
- Solucion esperada: fijar archivo, project name y entorno de ejecucion de forma
  explicita.

## Caso 18: `network_mode: host` rompe expectativas de service discovery

- Problema: un servicio con `network_mode: host` no se comporta como un servicio
  normal dentro de la red bridge de Compose.
- Componentes: `network_mode`, host networking, bridge network, service name.
- Posibles causas: el servicio comparte la red del host y no sigue el flujo
  normal de DNS interno de Compose.
- Diagnostico: revisar `docker compose config` y comparar con servicios que si
  estan conectados a redes Compose normales.
- Solucion esperada: usar red bridge normal para comunicacion por service name o
  acceso al host solo cuando sea realmente necesario.

## Caso 19: Conexion rota por IP antigua del container

- Problema: la aplicacion guarda una IP de container y falla despues de recrear
  el servicio.
- Componentes: Compose network, service name, container IP.
- Posibles causas: la IP cambia al recrear el container, mientras el service
  name permanece estable.
- Diagnostico: inspeccionar la red antes/despues y revisar si la aplicacion
  guarda IPs.
- Solucion esperada: usar service name y soportar reconexion.

## Caso 20: Puertos dinamicos en servicios escalados

- Problema: un servicio escalado tiene varios host ports y no esta claro cual
  corresponde a cada replica.
- Componentes: scaled service, host port, container port, `docker compose port`.
- Posibles causas: Compose asigna puertos publicados dinamicamente por replica.
- Diagnostico: usar `docker compose port --index`.
- Solucion esperada: desde el host consultar el puerto de la replica concreta;
  desde otros containers usar service name y container port.

## Caso 21: Servicio en red interna sin internet

- Problema: un worker conectado solo a una red interna no alcanza destinos
  externos.
- Componentes: internal network, gateway, multi-network service.
- Posibles causas: `internal: true` elimina conectividad externa.
- Diagnostico: revisar redes del servicio y comparar con uno que tenga acceso
  externo.
- Solucion esperada: mantener servicios privados aislados y conectar el servicio
  que necesita internet a una red no interna.

## Caso 22: Hostname custom no resuelve en container

- Problema: un hostname custom no es conocido dentro del container.
- Componentes: `extra_hosts`, `/etc/hosts`, internal DNS, `host-gateway`.
- Posibles causas: el nombre no es un service name de Compose ni fue definido
  con `extra_hosts`.
- Diagnostico: revisar `extra_hosts` e inspeccionar `/etc/hosts` dentro del
  container.
- Solucion esperada: agregar mapping con `extra_hosts`, por ejemplo usando
  `host-gateway`.

## Caso 23: Variable obligatoria de interpolacion falta

- Problema: Compose se detiene porque una expresion como `${VAR:?error}` no
  encuentra la variable.
- Componentes: interpolation, `.env`, shell, `--env-file`, image `ENV`.
- Posibles causas: la variable no esta en el shell ni en el env file usado; el
  usuario confunde interpolation con runtime env.
- Diagnostico: usar `docker compose config --environment` y revisar fuentes de
  variables.
- Solucion esperada: definir la variable requerida o usar un valor por defecto
  si corresponde.
