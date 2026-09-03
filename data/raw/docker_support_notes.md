# Docker Support Knowledge Notes

These notes are intentionally small and controlled. They are not a copy of the
Docker documentation. They paraphrase selected Docker support knowledge for the
Bachelorarbeit experiment.

## [daemon-connectivity] Docker daemon connectivity

Problem: A user runs a Docker command and receives a message similar to "Cannot
connect to the Docker daemon".

Relevant component: Docker client, Docker daemon, Docker host.

Typical causes:

- The Docker daemon is not running on the local machine.
- The Docker client is configured to reach another host via `DOCKER_HOST`.
- The remote Docker host is unreachable because of firewall, network, or service
  problems.

Useful diagnosis:

- Run `docker info` to check whether the client can talk to Docker.
- Check the operating system service status for Docker.
- Check whether `DOCKER_HOST` is set in the shell environment.
- If `DOCKER_HOST` is wrong, remove or correct it.

Expected solution pattern:

Start the Docker service if it is stopped. If the client points to a remote host,
verify the host, network path, firewall, and Docker service on that host.

Sources: docker-daemon-troubleshoot

## [compose-service-discovery] Compose service discovery

Problem: A container started by Docker Compose cannot reach another service by
service name, for example `db`.

Relevant component: Docker Compose default network, internal DNS, service names.

Typical causes:

- The two services are not connected to the same Compose network.
- A custom network configuration isolates one service from the other.
- The application uses an IP address instead of the service name.
- The application uses the host port instead of the container port for
  service-to-service communication.

Useful diagnosis:

- Inspect the generated Compose configuration.
- Verify that both services are attached to a shared network.
- Test connectivity from inside the container.
- Remember that Compose service-to-service communication should use the
  container port, not the host port.

Expected solution pattern:

Use the service name as hostname and the container port as target port. If custom
networks are used, connect both services to a shared network.

Sources: docker-compose-networking, docker-compose-networks-reference, docker-compose-services-reference

## [host-port-vs-container-port] Host port and container port confusion

Problem: A service works inside the Compose network, but the user cannot access
it correctly from the host, or another container uses the wrong port.

Relevant component: Compose port publishing, host port, container port.

Typical causes:

- The host tries to access a container port that was not published.
- A container tries to reach another container via the published host port.
- The application listens on a different port than the one configured in
  `ports`.

Useful diagnosis:

- Inspect port mappings with Docker or Compose commands.
- Distinguish host access from container-to-container access.
- Check which port the application actually listens on.

Expected solution pattern:

Use the host port only from outside Docker. Use the service name and container
port for communication between Compose services.

Sources: docker-compose-networking

## [compose-env-missing] Environment variable missing in container

Problem: An application inside a container cannot see an expected environment
variable.

Relevant component: Compose environment configuration, `.env` file,
interpolation, container environment.

Typical causes:

- The variable is only used for Compose file interpolation and was not passed
  into the container environment.
- The `.env` file is in the wrong directory.
- Another source has higher precedence and overrides the value.
- The service was not recreated after configuration changed.

Useful diagnosis:

- Check the final Compose model with `docker compose config`.
- Check variables used for interpolation with `docker compose config --environment`.
- Inspect the environment inside the running container.
- Recreate the service after changing environment configuration.

Expected solution pattern:

Define the variable explicitly in the service environment if the application
must read it at runtime. Keep interpolation and container runtime environment as
separate concepts.

Sources: docker-compose-env, docker-compose-env-interpolation

## [compose-env-precedence] Environment variable precedence confusion

Problem: Docker Compose uses an unexpected value for a variable.

Relevant component: shell environment, `.env`, `--env-file`, Compose
interpolation.

Typical causes:

- A shell variable overrides a value from an environment file.
- A specific `--env-file` is used instead of the default `.env`.
- Multiple environment files are read in order, and later values override
  earlier values.

Useful diagnosis:

- Print the final Compose configuration.
- Print the environment values used for interpolation.
- Check which environment files are loaded.

Expected solution pattern:

Make the source of the variable explicit and document the chosen precedence. Use
one predictable environment file strategy for the project.

Sources: docker-compose-env, docker-compose-env-interpolation

## [compose-env-precedence-runtime] Runtime environment value is overridden

Problem: A container receives an environment value different from the one the
user expected.

Relevant component: Compose environment precedence, CLI `--env`, service
`environment`, service `env_file`, image `ENV`.

Typical causes:

- A variable passed with `docker compose run -e` overrides values from the
  Compose file.
- A service `environment` value overrides a value from `env_file`.
- The container image defines an `ENV`, but Compose overrides it.
- The user expects the host `.env` file to automatically define the runtime
  container environment.

Useful diagnosis:

- Compare values from the shell, `.env`, `env_file`, and service
  `environment`.
- Run the container and inspect its environment.
- Use `docker compose config` to inspect the resolved Compose model.

Expected solution pattern:

Decide one authoritative source for runtime environment variables. Use service
`environment` or `env_file` intentionally, and document when CLI overrides are
used.

Sources: docker-compose-env-precedence, docker-compose-env

## [compose-project-name-confusion] Unexpected Compose project name

Problem: Docker Compose creates containers or networks with an unexpected
prefix.

Relevant component: Compose project name, `COMPOSE_PROJECT_NAME`, `-p`, top-level
`name`, project directory.

Typical causes:

- The current directory name is used as project name.
- `COMPOSE_PROJECT_NAME` is set in the environment.
- The `-p` flag overrides the project name.
- The Compose file contains a top-level `name`.

Useful diagnosis:

- Check the command line for `-p`.
- Check whether `COMPOSE_PROJECT_NAME` is set.
- Inspect the resolved Compose project name.
- Compare container and network names with the expected project name.

Expected solution pattern:

Set the project name deliberately with `-p`, `COMPOSE_PROJECT_NAME`, or top-level
`name`, and keep it consistent across commands.

Sources: docker-compose-predefined-env, docker-compose-networking

## [compose-file-path-confusion] Compose uses the wrong Compose file

Problem: A user changes `compose.yaml`, but Docker Compose appears to use a
different file or configuration.

Relevant component: Compose file discovery, `COMPOSE_FILE`, `-f`.

Typical causes:

- `COMPOSE_FILE` points to another file.
- The `-f` option selects another Compose file.
- The command is executed from a directory where Compose discovers a different
  file.
- Multiple Compose files are merged.

Useful diagnosis:

- Check the command line for `-f`.
- Check whether `COMPOSE_FILE` is set.
- Run `docker compose config` to see the resolved model.

Expected solution pattern:

Make the Compose file path explicit when necessary and clear conflicting
environment variables.

Sources: docker-compose-predefined-env, docker-compose-env-interpolation

## [compose-profile-not-started] Service does not start because profile is inactive

Problem: A service defined in the Compose file does not start when the user runs
`docker compose up`.

Relevant component: Compose profiles, `COMPOSE_PROFILES`, service profiles.

Typical causes:

- The service is assigned to a profile.
- The profile is not enabled.
- `COMPOSE_PROFILES` or `--profile` is missing or different from expected.

Useful diagnosis:

- Inspect the service definition for `profiles`.
- Check `COMPOSE_PROFILES`.
- Start Compose with the intended `--profile`.

Expected solution pattern:

Enable the required profile or remove the profile restriction if the service
should always start.

Sources: docker-compose-predefined-env, docker-compose-services-reference

## [compose-startup-order] Application starts before database is ready

Problem: A web application starts before its database is ready and fails during
startup.

Relevant component: `depends_on`, healthcheck, service readiness.

Typical causes:

- `depends_on` only controls creation order if no health condition is defined.
- The database container has started but is not yet ready to accept connections.
- The application does not retry failed database connections.

Useful diagnosis:

- Inspect `depends_on` configuration.
- Check whether the database service has a healthcheck.
- Check application logs for connection failures during startup.

Expected solution pattern:

Use a healthcheck and `depends_on` with `condition: service_healthy` when the
dependent service must wait for readiness. The application should also handle
retries.

Sources: docker-compose-startup-order, docker-compose-services-reference

## [healthcheck-wrong-signal] Service stays unhealthy

Problem: A container is running, but Docker marks it as unhealthy.

Relevant component: Docker/Compose healthcheck.

Typical causes:

- The healthcheck command tests the wrong endpoint or port.
- The healthcheck timeout, interval, retries, or start period are unsuitable.
- The image healthcheck is overridden or disabled unintentionally.

Useful diagnosis:

- Inspect the configured healthcheck.
- Check container logs and healthcheck output.
- Verify that the healthcheck command works inside the container.

Expected solution pattern:

Adjust the healthcheck command and timing to reflect the real readiness signal
of the service.

Sources: docker-compose-services-reference, docker-compose-startup-order

## [volume-data-disappears] Data disappears after container restart

Problem: A user expects data to persist, but it disappears after a container is
removed or recreated.

Relevant component: container writable layer, named volumes, bind mounts.

Typical causes:

- Data was written only into the container writable layer.
- No volume or bind mount was configured for the data directory.
- A different named volume or path is used than expected.

Useful diagnosis:

- Inspect the service mount configuration.
- Check Docker volumes on the host.
- Verify the application data directory.

Expected solution pattern:

Use a named volume or bind mount for data that must survive container
recreation. Verify that the application writes to the mounted path.

Sources: docker-storage-volumes

## [bind-mount-vs-volume] Confusion between bind mount and volume

Problem: A user is unsure whether to use a Docker volume or a bind mount.

Relevant component: Docker storage, managed volumes, host paths.

Typical causes:

- The user needs persistence but also wants to edit files directly from the host.
- The user assumes volumes and bind mounts behave identically.
- The application writes to a path that is not mounted.

Useful diagnosis:

- Identify whether the host must directly access the files.
- Identify whether the data should be managed by Docker.
- Check the mount target inside the container.

Expected solution pattern:

Use volumes for Docker-managed persistent data. Use bind mounts when files must
be shared directly between host and container.

Sources: docker-storage-overview, docker-storage-volumes

## [volume-mount-over-existing-data] Volume mount hides existing container files

Problem: Files that existed in the image seem to disappear after mounting a
volume.

Relevant component: volume mount target, existing data in image, container
filesystem.

Typical causes:

- A volume is mounted over a non-empty directory in the container.
- The mounted storage hides files that are present in the image at the same path.
- The user expects image files and mounted volume files to be merged.

Useful diagnosis:

- Check the mount target path.
- Start a container without the mount to compare contents.
- Inspect whether the volume was pre-populated.

Expected solution pattern:

Avoid mounting over paths where important image files are expected, or
initialize the volume deliberately.

Sources: docker-storage-volumes, docker-storage-overview

## [tmpfs-not-persistent] Data in tmpfs does not persist

Problem: Data written during container runtime disappears after the container or
host restarts.

Relevant component: tmpfs mount, memory-backed storage.

Typical causes:

- The data is stored in a tmpfs mount.
- The user expects tmpfs to behave like a persistent volume.
- The data is temporary by design.

Useful diagnosis:

- Check whether the path is mounted as tmpfs.
- Decide whether the data is temporary or must be kept.

Expected solution pattern:

Use tmpfs only for temporary data. Use a volume or bind mount for data that must
persist.

Sources: docker-storage-overview

## [dns-resolver-problems] DNS resolution problems in containers

Problem: A container cannot resolve external domain names or internal names.

Relevant component: Docker daemon DNS settings, container DNS, Compose internal
DNS, host resolver.

Typical causes:

- A host resolver configuration cannot be used by containers.
- Docker daemon DNS settings are missing or unsuitable.
- The target internal name is not registered on the same Docker network.

Useful diagnosis:

- Test DNS resolution from inside the container.
- Check whether the problem affects external domains or only service names.
- Inspect network membership and daemon DNS configuration.

Expected solution pattern:

For external DNS problems, configure suitable DNS servers for Docker. For
service-name problems, verify that services share a Docker network.

Sources: docker-daemon-troubleshoot, docker-compose-networking

## [external-network-missing] External Compose network not found

Problem: Docker Compose fails because an external network is referenced but not
available.

Relevant component: Compose external networks.

Typical causes:

- The Compose file marks a network as external.
- Docker Compose expects that network to already exist.
- The actual network name differs from the configured name.

Useful diagnosis:

- Check the `networks` section in the Compose file.
- List existing Docker networks.
- Compare the configured external network name with the real network name.

Expected solution pattern:

Create the external network before running Compose, or remove the `external`
setting if Compose should manage the network itself.

Sources: docker-compose-networking, docker-compose-networks-reference

## [network-mode-host-service-discovery] Host network mode and service discovery

Problem: A Compose service uses `network_mode: host` and another service name no
longer behaves like it does on the default Compose bridge network.

Relevant component: Compose `network_mode`, host networking, bridge networking,
service discovery.

Typical causes:

- The service shares the host network stack instead of joining the normal
  Compose bridge network.
- Normal service-name DNS expectations are applied to a service that is not
  using the normal Compose network path.
- The user expects port publishing to behave the same with host networking.

Useful diagnosis:

- Run `docker compose config` and check whether `network_mode: host` is set.
- Compare the affected service with services attached to normal Compose
  networks.
- Decide whether host networking is truly required.

Expected solution pattern:

Use the normal Compose bridge network when services should discover each other
by service name. Use explicit host access only when host networking is needed.

Sources: docker-compose-networking, docker-compose-services-reference

## [container-ip-changes] Container IP changes after service recreation

Problem: An application stores or uses a container IP address and the connection
breaks after Compose recreates the service.

Relevant component: Compose default network, internal DNS, service name,
container IP address.

Typical causes:

- Compose recreates a service and assigns a new container IP address.
- The service name stays stable, but a stored IP address becomes stale.
- Existing connections to the removed container are closed and the application
  does not reconnect.

Useful diagnosis:

- Inspect the network before and after service recreation.
- Check whether the application stores IP addresses instead of hostnames.
- Verify whether the application reconnects through the service name.

Expected solution pattern:

Use the service name instead of a fixed container IP address. The application
should handle reconnecting when a service container is replaced.

Sources: docker-compose-networking

## [scaled-service-dynamic-ports] Scaled service with dynamic host ports

Problem: A scaled service exposes dynamic host ports and the user does not know
which host port belongs to which replica.

Relevant component: Compose port publishing, scaled services, host port,
container port.

Typical causes:

- The Compose file publishes a container port without a fixed host port.
- Multiple service replicas each receive their own host port.
- The user confuses host access with service-to-service access inside the
  Compose network.

Useful diagnosis:

- Run `docker compose port` to inspect a published port.
- Use `--index` to inspect a specific replica.
- Distinguish host access from service-to-service access.

Expected solution pattern:

Use `docker compose port --index` when the host needs to reach a specific
replica. Other containers should normally use the service name and container
port through the Compose network.

Sources: docker-compose-networking

## [internal-network-no-internet] Internal network blocks external access

Problem: A service attached only to an internal Compose network cannot reach
external targets.

Relevant component: Compose internal network, external connectivity, gateway,
multi-network services.

Typical causes:

- The network is configured with `internal: true`.
- The affected service is not attached to any non-internal network.
- The design intentionally isolates private services, but the wrong service was
  isolated.

Useful diagnosis:

- Inspect the network configuration in the Compose file.
- Check which networks the affected service joins.
- Compare the affected service with a service that has internet access.

Expected solution pattern:

Keep private services on the internal network. Attach services that require
external access to a non-internal or public network as well.

Sources: docker-compose-networking

## [extra-hosts-custom-hostname] Custom hostname not resolved inside container

Problem: A container needs to resolve a custom hostname that is not a Compose
service name.

Relevant component: Compose `extra_hosts`, container `/etc/hosts`, internal DNS,
host-gateway.

Typical causes:

- Compose internal DNS only provides service discovery for services on the
  network.
- A custom hostname was not added through `extra_hosts`.
- The user expects host machine names to work automatically in every
  environment.

Useful diagnosis:

- Inspect the service definition for `extra_hosts`.
- Inspect `/etc/hosts` from inside the running container.
- Test whether the target should be a Compose service name or a custom host
  mapping.

Expected solution pattern:

Use `extra_hosts` for custom hostname mappings. Use `host-gateway` when a
container needs a stable mapping to the Docker host.

Sources: docker-compose-networking, docker-compose-services-reference

## [required-interpolation-variable] Required interpolation variable missing

Problem: Docker Compose stops because an interpolation expression marks a
variable as required.

Relevant component: Compose interpolation, `.env`, shell environment,
`--env-file`, Compose model.

Typical causes:

- A required interpolation expression such as `${VAR:?error}` is used.
- The variable is missing from the shell and the selected environment file.
- The user expects an image `ENV` value to satisfy Compose interpolation.

Useful diagnosis:

- Run `docker compose config --environment` to inspect interpolation values.
- Check the shell environment and selected env files.
- Separate Compose interpolation from the runtime container environment.

Expected solution pattern:

Set the required variable before running Compose, provide it through the
intended env file, or use a default interpolation expression if a fallback is
acceptable.

Sources: docker-compose-env-interpolation, docker-compose-env-precedence
