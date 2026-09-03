from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = PROJECT_ROOT / "data" / "sources.json"
QUESTIONS_PATH = PROJECT_ROOT / "data" / "questions" / "docker_support_questions.jsonl"
GRAPH_PATH = PROJECT_ROOT / "data" / "knowledge" / "docker_support_graph.json"


NEW_SOURCE = {
    "id": "docker-compose-volumes-reference",
    "title": "Define and manage volumes in Docker Compose",
    "url": "https://docs.docker.com/reference/compose-file/volumes/",
    "area": "Compose file reference",
    "planned_usage": "Top-level volumes, reusable named volumes, external volumes, driver options",
}


NEW_NODES = [
    {
        "id": "document.docker_daemon_troubleshoot",
        "type": "document",
        "label": "Docker Docs: daemon troubleshooting",
        "description": "Official Docker documentation page about debugging Docker daemon issues.",
        "keywords": ["daemon", "DOCKER_HOST", "docker info", "dns", "troubleshooting"],
    },
    {
        "id": "document.compose_networking",
        "type": "document",
        "label": "Docker Docs: Compose networking",
        "description": "Official Docker documentation page about Compose networks, service discovery, ports, external networks and connectivity debugging.",
        "keywords": ["compose", "networking", "service name", "host port", "container port", "external network", "extra_hosts"],
    },
    {
        "id": "document.compose_startup_order",
        "type": "document",
        "label": "Docker Docs: Compose startup order",
        "description": "Official Docker documentation page about depends_on, healthcheck and service readiness.",
        "keywords": ["depends_on", "healthcheck", "service_healthy", "startup order", "readiness"],
    },
    {
        "id": "document.compose_env_interpolation",
        "type": "document",
        "label": "Docker Docs: variable interpolation",
        "description": "Official Docker documentation page about interpolation syntax, .env files and docker compose config --environment.",
        "keywords": ["interpolation", ".env", "env-file", "docker compose config --environment", "required variable"],
    },
    {
        "id": "document.compose_env_precedence",
        "type": "document",
        "label": "Docker Docs: environment precedence",
        "description": "Official Docker documentation page about precedence of CLI, environment, env_file and image ENV values.",
        "keywords": ["precedence", "environment", "env_file", "docker compose run -e", "image ENV"],
    },
    {
        "id": "document.compose_predefined_env",
        "type": "document",
        "label": "Docker Docs: predefined Compose variables",
        "description": "Official Docker documentation page about COMPOSE_PROJECT_NAME, COMPOSE_FILE and COMPOSE_PROFILES.",
        "keywords": ["COMPOSE_PROJECT_NAME", "COMPOSE_FILE", "COMPOSE_PROFILES", "project directory"],
    },
    {
        "id": "document.storage_volumes",
        "type": "document",
        "label": "Docker Docs: volumes",
        "description": "Official Docker documentation page about persistent volumes, lifecycle and mounting over existing data.",
        "keywords": ["volume", "persistent", "mount", "bind mount", "tmpfs", "existing data"],
    },
    {
        "id": "document.compose_volumes_reference",
        "type": "document",
        "label": "Docker Docs: Compose volumes reference",
        "description": "Official Compose reference for declaring reusable named volumes and external volumes.",
        "keywords": ["compose volumes", "top-level volumes", "external volume", "named volume", "reusable volume"],
    },
    {
        "id": "document.compose_services_reference",
        "type": "document",
        "label": "Docker Docs: Compose services reference",
        "description": "Official Compose reference for service attributes such as depends_on, healthcheck, extra_hosts, profiles, ports and network_mode.",
        "keywords": ["services", "depends_on", "healthcheck", "extra_hosts", "profiles", "ports", "network_mode"],
    },
    {
        "id": "component.network_mode",
        "type": "component",
        "label": "Compose network_mode",
        "description": "Service setting that changes how a container uses networking, including host networking or sharing another service network namespace.",
        "keywords": ["network_mode", "host", "service", "container networking"],
    },
    {
        "id": "problem.host_network_no_service_dns",
        "type": "problem",
        "label": "Service DNS fails with host network mode",
        "description": "A service using host network mode does not get the normal Compose service-name DNS behavior.",
        "keywords": ["network_mode host", "service name", "dns", "ports", "host network"],
    },
    {
        "id": "cause.host_network_bypasses_compose_dns",
        "type": "cause",
        "label": "Host network bypasses Compose DNS",
        "description": "Host network mode shares the host networking stack and does not use the normal Compose bridge network service discovery.",
        "keywords": ["host network", "bridge network", "service discovery", "no port mapping"],
    },
    {
        "id": "solution.use_bridge_or_explicit_host_access",
        "type": "solution",
        "label": "Use bridge network or explicit host access",
        "description": "Keep services on a Compose bridge network for service discovery, or use explicit host access only when host networking is required.",
        "keywords": ["bridge network", "service name", "host.docker.internal", "host-gateway"],
    },
    {
        "id": "diagnosis.compose_network_mode",
        "type": "diagnosis",
        "label": "Inspect network_mode",
        "description": "Check whether a service uses network_mode and whether that changes expected Compose DNS or port behavior.",
        "keywords": ["network_mode", "docker compose config", "host"],
    },
    {
        "id": "problem.container_ip_changed",
        "type": "problem",
        "label": "Connection uses old container IP",
        "description": "A connection fails after Compose recreates a service because the old container IP address changed.",
        "keywords": ["old IP", "container recreated", "dynamic IP", "service name"],
    },
    {
        "id": "cause.dynamic_container_ip",
        "type": "cause",
        "label": "Container IP is dynamic",
        "description": "Compose service names stay stable, but container IP addresses can change when containers are recreated.",
        "keywords": ["dynamic IP", "service name stable", "recreate", "restart"],
    },
    {
        "id": "solution.reconnect_by_service_name",
        "type": "solution",
        "label": "Reconnect using service name",
        "description": "Use the service name instead of fixed IP addresses and make the application reconnect after old connections close.",
        "keywords": ["service name", "reconnect", "avoid fixed IP", "new IP"],
    },
    {
        "id": "problem.scaled_service_port_ambiguous",
        "type": "problem",
        "label": "Scaled service has multiple host ports",
        "description": "A scaled Compose service may expose different dynamic host ports per replica.",
        "keywords": ["scale", "replica", "dynamic host port", "docker compose port --index"],
    },
    {
        "id": "cause.replica_dynamic_host_ports",
        "type": "cause",
        "label": "Each replica has its own host port",
        "description": "When a service is scaled and host ports are dynamic, each replica can receive a different published host port.",
        "keywords": ["replica", "dynamic port", "host port", "index"],
    },
    {
        "id": "solution.inspect_port_with_index",
        "type": "solution",
        "label": "Inspect host port with --index",
        "description": "Use docker compose port with --index to identify the published host port for a specific replica.",
        "keywords": ["docker compose port", "--index", "host port", "replica"],
    },
    {
        "id": "diagnosis.compose_port",
        "type": "diagnosis",
        "label": "Run docker compose port",
        "description": "Inspect which host port maps to a service container port, including a specific replica index when scaled.",
        "keywords": ["docker compose port", "host port", "container port", "--index"],
    },
    {
        "id": "component.internal_network",
        "type": "component",
        "label": "Compose internal network",
        "description": "A Compose network marked as internal has no default external connectivity.",
        "keywords": ["internal network", "internal: true", "gateway", "internet"],
    },
    {
        "id": "problem.internal_network_no_internet",
        "type": "problem",
        "label": "Service on internal network cannot reach internet",
        "description": "A service attached only to an internal Compose network cannot reach external network targets.",
        "keywords": ["internal network", "internet", "no gateway", "external connectivity"],
    },
    {
        "id": "cause.internal_network_no_gateway",
        "type": "cause",
        "label": "Internal network has no external gateway",
        "description": "An internal Compose network is isolated from external connectivity and has no default gateway to the outside.",
        "keywords": ["internal: true", "no gateway", "isolated", "external connectivity"],
    },
    {
        "id": "solution.attach_service_to_public_network",
        "type": "solution",
        "label": "Attach service to a non-internal network",
        "description": "Attach the service that needs internet access to a non-internal network while keeping private services isolated.",
        "keywords": ["public network", "non-internal", "multiple networks", "isolation"],
    },
    {
        "id": "component.extra_hosts",
        "type": "component",
        "label": "Compose extra_hosts",
        "description": "Service attribute that writes custom hostname mappings into a container hosts file.",
        "keywords": ["extra_hosts", "host-gateway", "host.docker.internal", "/etc/hosts"],
    },
    {
        "id": "problem.custom_hostname_unresolved",
        "type": "problem",
        "label": "Custom hostname cannot be resolved",
        "description": "A container cannot resolve a custom host name that is not registered by Compose internal DNS.",
        "keywords": ["custom hostname", "extra_hosts", "host.docker.internal", "host-gateway"],
    },
    {
        "id": "cause.hostname_not_registered_in_dns",
        "type": "cause",
        "label": "Hostname is not registered in Docker DNS",
        "description": "Compose DNS knows service names on the network, but not arbitrary external or custom names unless configured.",
        "keywords": ["custom hostname", "not in DNS", "service name", "extra_hosts"],
    },
    {
        "id": "solution.add_extra_hosts_mapping",
        "type": "solution",
        "label": "Add extra_hosts mapping",
        "description": "Add an extra_hosts entry, for example with host-gateway, when a custom name should resolve inside a container.",
        "keywords": ["extra_hosts", "host-gateway", "host.docker.internal", "/etc/hosts"],
    },
    {
        "id": "diagnosis.inspect_hosts_file",
        "type": "diagnosis",
        "label": "Inspect container hosts file",
        "description": "Inspect /etc/hosts inside the container to verify custom mappings created by extra_hosts.",
        "keywords": ["/etc/hosts", "docker compose exec", "extra_hosts"],
    },
    {
        "id": "component.runtime_container_environment",
        "type": "component",
        "label": "Runtime container environment",
        "description": "Environment variables visible to the process running inside the container.",
        "keywords": ["runtime environment", "container environment", "env_file", "environment"],
    },
    {
        "id": "problem.required_interpolation_missing",
        "type": "problem",
        "label": "Required interpolation variable missing",
        "description": "Compose stops because a variable expression marks a value as required but the variable is not set.",
        "keywords": ["required variable", "${VAR:?error}", "interpolation", "missing"],
    },
    {
        "id": "cause.required_variable_not_set",
        "type": "cause",
        "label": "Required variable is not set",
        "description": "A required interpolation expression fails before the final Compose model is created.",
        "keywords": ["required", "not set", "interpolation", ".env"],
    },
    {
        "id": "solution.set_required_variable_or_default",
        "type": "solution",
        "label": "Set required variable or define default",
        "description": "Set the required variable through the shell or env file, or use an interpolation default if that is intended.",
        "keywords": ["set variable", "default value", "${VAR:-default}", "env-file"],
    },
]


NEW_EDGES = [
    # Source traceability for existing core cases.
    ("problem.daemon_unreachable", "documented_in", "document.docker_daemon_troubleshoot", "The daemon connection error and DOCKER_HOST checks are described in Docker daemon troubleshooting.", ["docker-daemon-troubleshoot"]),
    ("cause.wrong_docker_host", "documented_in", "document.docker_daemon_troubleshoot", "Docker documents DOCKER_HOST as a way the client may point to another daemon host.", ["docker-daemon-troubleshoot"]),
    ("problem.service_name_unreachable", "documented_in", "document.compose_networking", "Compose networking documents service discovery by service name on shared networks.", ["docker-compose-networking"]),
    ("cause.wrong_port_context", "documented_in", "document.compose_networking", "Compose networking distinguishes host ports from container ports for service-to-service communication.", ["docker-compose-networking"]),
    ("problem.env_missing", "documented_in", "document.compose_env_interpolation", "Variable interpolation and .env behavior are documented in the Compose environment variable guide.", ["docker-compose-env-interpolation"]),
    ("cause.value_overridden", "documented_in", "document.compose_env_precedence", "Compose environment precedence rules explain which value wins when multiple sources define the same variable.", ["docker-compose-env-precedence"]),
    ("problem.unexpected_project_name", "documented_in", "document.compose_predefined_env", "Predefined Compose variables document COMPOSE_PROJECT_NAME and project naming precedence.", ["docker-compose-predefined-env"]),
    ("problem.wrong_compose_file", "documented_in", "document.compose_predefined_env", "Predefined Compose variables document COMPOSE_FILE and file discovery behavior.", ["docker-compose-predefined-env"]),
    ("problem.profile_service_inactive", "documented_in", "document.compose_predefined_env", "Predefined Compose variables document COMPOSE_PROFILES and profile activation.", ["docker-compose-predefined-env"]),
    ("problem.database_not_ready", "documented_in", "document.compose_startup_order", "Docker documents that startup order does not always mean readiness unless a health condition is used.", ["docker-compose-startup-order"]),
    ("problem.unhealthy_container", "documented_in", "document.compose_services_reference", "The services reference documents healthcheck configuration as a service attribute.", ["docker-compose-services-reference"]),
    ("problem.data_not_persistent", "documented_in", "document.storage_volumes", "Docker volumes documentation explains that volumes persist outside a container lifecycle.", ["docker-storage-volumes"]),
    ("solution.use_named_volume", "documented_in", "document.compose_volumes_reference", "The Compose volumes reference explains how services can use reusable named volumes.", ["docker-compose-volumes-reference"]),
    ("problem.files_hidden_by_mount", "documented_in", "document.storage_volumes", "Docker volumes documentation explains the effect of mounting over existing container data.", ["docker-storage-volumes"]),
    ("problem.external_network_missing", "documented_in", "document.compose_networking", "Compose networking explains that external networks must exist before Compose uses them.", ["docker-compose-networking", "docker-compose-networks-reference"]),

    # Relation enrichment for existing cases.
    ("solution.use_service_name_container_port", "requires", "component.compose_default_network", "Service-name connectivity requires that the services share a Compose network.", ["docker-compose-networking"]),
    ("solution.use_healthcheck_depends_on", "requires", "component.healthcheck", "The service_healthy condition requires a healthcheck that defines readiness.", ["docker-compose-startup-order", "docker-compose-services-reference"]),
    ("solution.inspect_resolved_env", "requires", "diagnosis.compose_config_environment", "docker compose config --environment shows which values are used for interpolation.", ["docker-compose-env-interpolation"]),
    ("component.compose_interpolation", "distinguished_from", "component.runtime_container_environment", "Interpolation values used while building the Compose model are not automatically the runtime variables inside a container.", ["docker-compose-env-interpolation", "docker-compose-env"]),
    ("cause.interpolation_not_runtime_env", "affects", "component.runtime_container_environment", "An application can miss a variable when the value was only used for interpolation and not passed to the container.", ["docker-compose-env-interpolation", "docker-compose-env"]),
    ("solution.define_service_environment", "requires", "component.runtime_container_environment", "A variable needed by the application must be defined in the container runtime environment.", ["docker-compose-env", "docker-compose-env-precedence"]),
    ("cause.value_overridden", "conflicts_with", "cause.interpolation_not_runtime_env", "A wrong value can come either from runtime precedence or from confusing interpolation with runtime variables.", ["docker-compose-env-precedence", "docker-compose-env-interpolation"]),
    ("solution.create_external_network", "requires", "component.compose_default_network", "An external Compose network must be available before services can attach to it.", ["docker-compose-networking", "docker-compose-networks-reference"]),
    ("solution.use_named_volume", "requires", "component.docker_volume", "Persistent container data requires a persistent mount such as a volume or bind mount.", ["docker-storage-volumes"]),
    ("solution.choose_bind_or_volume", "requires", "component.bind_mount", "Bind mounts are appropriate when files must be accessed directly from the host.", ["docker-storage-overview", "docker-storage-volumes"]),
    ("solution.choose_bind_or_volume", "requires", "component.docker_volume", "Docker-managed volumes are appropriate for persistent data managed by Docker.", ["docker-storage-overview", "docker-storage-volumes"]),

    # New network-mode case.
    ("problem.host_network_no_service_dns", "affects", "component.network_mode", "The problem is caused by a network mode that changes normal Compose networking behavior.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("problem.host_network_no_service_dns", "may_be_caused_by", "cause.host_network_bypasses_compose_dns", "Host networking shares the host stack and does not provide normal service-name DNS resolution.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("problem.host_network_no_service_dns", "diagnosed_by", "diagnosis.compose_network_mode", "Inspect the resolved Compose model to see whether network_mode is set.", ["docker-compose-services-reference"]),
    ("cause.host_network_bypasses_compose_dns", "solved_by", "solution.use_bridge_or_explicit_host_access", "Use the normal bridge network for service discovery unless host networking is explicitly required.", ["docker-compose-networking"]),
    ("solution.use_bridge_or_explicit_host_access", "requires", "component.compose_default_network", "Service discovery by service name requires normal Compose networking.", ["docker-compose-networking"]),
    ("problem.host_network_no_service_dns", "documented_in", "document.compose_networking", "Compose networking documents how network_mode changes networking behavior.", ["docker-compose-networking"]),

    # New dynamic-IP case.
    ("problem.container_ip_changed", "affects", "component.compose_default_network", "The connection problem appears in Compose service networking after recreation.", ["docker-compose-networking"]),
    ("problem.container_ip_changed", "may_be_caused_by", "cause.dynamic_container_ip", "Containers can receive a new IP address when recreated while the service name remains stable.", ["docker-compose-networking"]),
    ("cause.dynamic_container_ip", "solved_by", "solution.reconnect_by_service_name", "Applications should use the service name and reconnect when an old connection closes.", ["docker-compose-networking"]),
    ("problem.container_ip_changed", "diagnosed_by", "diagnosis.network_inspect", "Inspect network membership and avoid depending on the old container IP.", ["docker-compose-networking"]),
    ("problem.container_ip_changed", "documented_in", "document.compose_networking", "Compose networking documents container IP changes after recreation.", ["docker-compose-networking"]),

    # New scaled-port case.
    ("problem.scaled_service_port_ambiguous", "affects", "component.compose_default_network", "Port ambiguity appears when scaled services publish dynamic host ports.", ["docker-compose-networking"]),
    ("problem.scaled_service_port_ambiguous", "may_be_caused_by", "cause.replica_dynamic_host_ports", "Each scaled replica can have a different dynamically assigned host port.", ["docker-compose-networking"]),
    ("problem.scaled_service_port_ambiguous", "diagnosed_by", "diagnosis.compose_port", "docker compose port with --index can show a specific replica's published host port.", ["docker-compose-networking"]),
    ("cause.replica_dynamic_host_ports", "solved_by", "solution.inspect_port_with_index", "Use --index when inspecting the published port of a scaled replica.", ["docker-compose-networking"]),
    ("solution.inspect_port_with_index", "requires", "diagnosis.compose_port", "The command output is the evidence for the selected replica's host port.", ["docker-compose-networking"]),
    ("problem.scaled_service_port_ambiguous", "documented_in", "document.compose_networking", "Compose networking documents dynamic port inspection and scaled replica indexes.", ["docker-compose-networking"]),

    # New internal network case.
    ("problem.internal_network_no_internet", "affects", "component.internal_network", "The service is attached only to an internal network.", ["docker-compose-networking"]),
    ("problem.internal_network_no_internet", "may_be_caused_by", "cause.internal_network_no_gateway", "An internal network has no external connectivity gateway.", ["docker-compose-networking"]),
    ("problem.internal_network_no_internet", "diagnosed_by", "diagnosis.network_inspect", "Network inspection can show whether the service is attached only to internal networks.", ["docker-compose-networking"]),
    ("cause.internal_network_no_gateway", "solved_by", "solution.attach_service_to_public_network", "Attach the service to a non-internal network if it needs external access.", ["docker-compose-networking"]),
    ("solution.attach_service_to_public_network", "requires", "component.internal_network", "Keep private services on the internal network while exposing only services that need external access.", ["docker-compose-networking"]),
    ("problem.internal_network_no_internet", "documented_in", "document.compose_networking", "Compose networking documents internal networks and hybrid networking.", ["docker-compose-networking"]),

    # New extra_hosts case.
    ("problem.custom_hostname_unresolved", "affects", "component.extra_hosts", "The unresolved name is a custom hostname rather than a Compose service name.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("problem.custom_hostname_unresolved", "may_be_caused_by", "cause.hostname_not_registered_in_dns", "Compose internal DNS does not automatically know arbitrary custom hostnames.", ["docker-compose-networking"]),
    ("problem.custom_hostname_unresolved", "diagnosed_by", "diagnosis.inspect_hosts_file", "Inspect /etc/hosts to check whether extra_hosts produced the expected mapping.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("cause.hostname_not_registered_in_dns", "solved_by", "solution.add_extra_hosts_mapping", "Add an extra_hosts entry for a custom hostname or host-gateway mapping.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("solution.add_extra_hosts_mapping", "requires", "component.extra_hosts", "The custom hostname is made visible inside the container through extra_hosts.", ["docker-compose-networking", "docker-compose-services-reference"]),
    ("problem.custom_hostname_unresolved", "documented_in", "document.compose_networking", "Compose networking documents custom DNS with extra_hosts.", ["docker-compose-networking"]),

    # New required interpolation case.
    ("problem.required_interpolation_missing", "affects", "component.compose_interpolation", "The failure happens while Compose interpolates the Compose model.", ["docker-compose-env-interpolation"]),
    ("problem.required_interpolation_missing", "may_be_caused_by", "cause.required_variable_not_set", "A required interpolation variable fails when it is unset or empty, depending on the expression.", ["docker-compose-env-interpolation"]),
    ("problem.required_interpolation_missing", "diagnosed_by", "diagnosis.compose_config_environment", "Inspect interpolation values before running the application.", ["docker-compose-env-interpolation"]),
    ("cause.required_variable_not_set", "solved_by", "solution.set_required_variable_or_default", "Set the missing variable or define a default interpolation expression.", ["docker-compose-env-interpolation"]),
    ("solution.set_required_variable_or_default", "requires", "component.compose_interpolation", "Required and default syntax are interpolation features of Compose.", ["docker-compose-env-interpolation"]),
    ("problem.required_interpolation_missing", "documented_in", "document.compose_env_interpolation", "Compose variable interpolation documents required and default expressions.", ["docker-compose-env-interpolation"]),
]


NEW_QUESTIONS = [
    {
        "id": "Q031",
        "difficulty": "simple",
        "category": "factual_simple",
        "category_label": "Einfache Faktenfrage",
        "expected_relation_hops": 1,
        "question": "What does network_mode: host change in Docker Compose networking?",
        "question_de": "Was veraendert network_mode: host im Docker-Compose-Networking?",
        "expected_keywords": ["network_mode", "host", "service name", "port mapping"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-services-reference"],
        "origin_note": "Manually derived from Docker Compose networking and service reference documentation.",
    },
    {
        "id": "Q032",
        "difficulty": "simple",
        "category": "factual_simple",
        "category_label": "Einfache Faktenfrage",
        "expected_relation_hops": 1,
        "question": "What command can show which host port maps to a container port in Compose?",
        "question_de": "Welcher Befehl zeigt, welcher Host-Port auf einen Container-Port in Compose abgebildet wird?",
        "expected_keywords": ["docker compose port", "host port", "container port"],
        "relevant_sources": ["docker-compose-networking"],
        "origin_note": "Manually derived from Docker Compose networking debugging documentation.",
    },
    {
        "id": "Q033",
        "difficulty": "procedural",
        "category": "procedural",
        "category_label": "Prozedurale Frage",
        "expected_relation_hops": 2,
        "question": "How can I verify that a Compose service is attached to the expected network?",
        "question_de": "Wie kann ich pruefen, ob ein Compose-Service mit dem erwarteten Netzwerk verbunden ist?",
        "expected_keywords": ["docker network inspect", "network membership", "Compose", "service"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-networks-reference"],
        "origin_note": "Manually derived from Docker Compose networking debugging documentation.",
    },
    {
        "id": "Q034",
        "difficulty": "procedural",
        "category": "procedural",
        "category_label": "Prozedurale Frage",
        "expected_relation_hops": 2,
        "question": "How can I make Docker Compose fail early when a required interpolation variable is missing?",
        "question_de": "Wie kann ich Docker Compose frueh abbrechen lassen, wenn eine erforderliche Interpolationsvariable fehlt?",
        "expected_keywords": ["${VAR:?error}", "required", "interpolation", "env file"],
        "relevant_sources": ["docker-compose-env-interpolation"],
        "origin_note": "Manually derived from Docker Compose interpolation syntax documentation.",
    },
    {
        "id": "Q035",
        "difficulty": "procedural",
        "category": "procedural",
        "category_label": "Prozedurale Frage",
        "expected_relation_hops": 2,
        "question": "How can I add a custom hostname mapping such as host.docker.internal to a Compose service?",
        "question_de": "Wie kann ich einem Compose-Service ein eigenes Hostname-Mapping wie host.docker.internal hinzufuegen?",
        "expected_keywords": ["extra_hosts", "host-gateway", "host.docker.internal", "Compose"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-services-reference"],
        "origin_note": "Manually derived from Docker Compose custom DNS and extra_hosts documentation.",
    },
    {
        "id": "Q036",
        "difficulty": "procedural",
        "category": "procedural",
        "category_label": "Prozedurale Frage",
        "expected_relation_hops": 2,
        "question": "How can I check whether extra_hosts changed the hosts file inside my container?",
        "question_de": "Wie kann ich pruefen, ob extra_hosts die hosts-Datei im Container veraendert hat?",
        "expected_keywords": ["docker compose exec", "/etc/hosts", "extra_hosts"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-services-reference"],
        "origin_note": "Manually derived from Docker Compose custom DNS documentation.",
    },
    {
        "id": "Q037",
        "difficulty": "relational",
        "category": "relational_troubleshooting",
        "category_label": "Relationale Troubleshooting-Frage",
        "expected_relation_hops": 3,
        "question": "Why does service-name DNS fail when my Compose service uses network_mode: host?",
        "question_de": "Warum funktioniert die DNS-Aufloesung per Servicename nicht, wenn mein Compose-Service network_mode: host nutzt?",
        "expected_keywords": ["network_mode", "host", "service name", "Compose network"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-services-reference"],
        "origin_note": "Manually derived from Docker Compose network_mode behavior.",
    },
    {
        "id": "Q038",
        "difficulty": "relational",
        "category": "relational_troubleshooting",
        "category_label": "Relationale Troubleshooting-Frage",
        "expected_relation_hops": 3,
        "question": "Why does a connection break after Compose recreates a service if my app stored the old container IP?",
        "question_de": "Warum bricht eine Verbindung nach dem Neuerstellen eines Compose-Services ab, wenn meine App die alte Container-IP gespeichert hat?",
        "expected_keywords": ["container IP", "service name", "recreate", "reconnect"],
        "relevant_sources": ["docker-compose-networking"],
        "origin_note": "Manually derived from Docker Compose container update and service discovery documentation.",
    },
    {
        "id": "Q039",
        "difficulty": "relational",
        "category": "relational_troubleshooting",
        "category_label": "Relationale Troubleshooting-Frage",
        "expected_relation_hops": 3,
        "question": "Why can a worker connected only to an internal Compose network not reach the internet?",
        "question_de": "Warum kann ein Worker, der nur mit einem internen Compose-Netzwerk verbunden ist, das Internet nicht erreichen?",
        "expected_keywords": ["internal", "network", "external connectivity", "gateway"],
        "relevant_sources": ["docker-compose-networking"],
        "origin_note": "Manually derived from Docker Compose internal network documentation.",
    },
    {
        "id": "Q040",
        "difficulty": "multi_hop",
        "category": "multi_hop",
        "category_label": "Multi-Hop-Frage",
        "expected_relation_hops": 4,
        "question": "What should I check if a Compose project behaves differently after I run it from another directory with another .env file?",
        "question_de": "Was sollte ich pruefen, wenn sich ein Compose-Projekt anders verhaelt, nachdem ich es aus einem anderen Verzeichnis mit anderer .env-Datei starte?",
        "expected_keywords": ["project directory", ".env", "COMPOSE_FILE", "docker compose config"],
        "relevant_sources": ["docker-compose-env-interpolation", "docker-compose-predefined-env"],
        "origin_note": "Manually derived from Compose project directory, COMPOSE_FILE and .env documentation.",
    },
    {
        "id": "Q041",
        "difficulty": "multi_hop",
        "category": "multi_hop",
        "category_label": "Multi-Hop-Frage",
        "expected_relation_hops": 4,
        "question": "When a scaled Compose web service uses dynamic host ports, how do I find the port for replica 2 and what should other containers use?",
        "question_de": "Wie finde ich bei einem skalierten Compose-Webservice mit dynamischen Host-Ports den Port fuer Replica 2, und was sollten andere Container verwenden?",
        "expected_keywords": ["docker compose port", "--index", "host port", "service name", "container port"],
        "relevant_sources": ["docker-compose-networking"],
        "origin_note": "Manually derived from Docker Compose port inspection and scaled service documentation.",
    },
    {
        "id": "Q042",
        "difficulty": "relational",
        "category": "configuration_conflict",
        "category_label": "Konfigurationskonflikt",
        "expected_relation_hops": 3,
        "question": "Why does ${TAG:?missing} stop Docker Compose although my image defines ENV TAG?",
        "question_de": "Warum stoppt ${TAG:?missing} Docker Compose, obwohl mein Image ENV TAG definiert?",
        "expected_keywords": ["interpolation", "required", "image ENV", "Compose model"],
        "relevant_sources": ["docker-compose-env-interpolation", "docker-compose-env-precedence"],
        "origin_note": "Manually derived from Compose interpolation and environment precedence documentation.",
    },
    {
        "id": "Q043",
        "difficulty": "relational",
        "category": "configuration_conflict",
        "category_label": "Konfigurationskonflikt",
        "expected_relation_hops": 3,
        "question": "Why is my env_file value ignored when environment and docker compose run -e also set the same variable?",
        "question_de": "Warum wird mein env_file-Wert ignoriert, wenn environment und docker compose run -e dieselbe Variable ebenfalls setzen?",
        "expected_keywords": ["docker compose run -e", "environment", "env_file", "precedence"],
        "relevant_sources": ["docker-compose-env-precedence"],
        "origin_note": "Manually derived from Compose environment precedence documentation.",
    },
    {
        "id": "Q044",
        "difficulty": "traceability",
        "category": "traceability",
        "category_label": "Nachvollziehbarkeit",
        "expected_relation_hops": 3,
        "question": "Why is a Compose service name more reliable than a container IP after service recreation?",
        "question_de": "Warum ist ein Compose-Servicename nach dem Neuerstellen eines Services verlaesslicher als eine Container-IP?",
        "expected_keywords": ["service name", "container IP", "recreated", "stable"],
        "relevant_sources": ["docker-compose-networking"],
        "origin_note": "Manually derived from Docker Compose service discovery and update documentation.",
    },
    {
        "id": "Q045",
        "difficulty": "traceability",
        "category": "traceability",
        "category_label": "Nachvollziehbarkeit",
        "expected_relation_hops": 3,
        "question": "Why must an external Compose network exist before docker compose up?",
        "question_de": "Warum muss ein externes Compose-Netzwerk bereits existieren, bevor docker compose up ausgefuehrt wird?",
        "expected_keywords": ["external", "network", "exist", "docker network create"],
        "relevant_sources": ["docker-compose-networking", "docker-compose-networks-reference"],
        "origin_note": "Manually derived from Docker Compose external network documentation.",
    },
    {
        "id": "Q046",
        "difficulty": "traceability",
        "category": "traceability",
        "category_label": "Nachvollziehbarkeit",
        "expected_relation_hops": 3,
        "question": "Why does a .env variable not automatically become a runtime variable inside the container?",
        "question_de": "Warum wird eine .env-Variable nicht automatisch zu einer Runtime-Variable im Container?",
        "expected_keywords": [".env", "interpolation", "container environment", "environment"],
        "relevant_sources": ["docker-compose-env-interpolation", "docker-compose-env"],
        "origin_note": "Manually derived from Docker Compose interpolation and runtime environment documentation.",
    },
    {
        "id": "Q047",
        "difficulty": "traceability",
        "category": "traceability",
        "category_label": "Nachvollziehbarkeit",
        "expected_relation_hops": 3,
        "question": "Why is depends_on alone not enough to prove that a database is ready?",
        "question_de": "Warum reicht depends_on allein nicht aus, um zu beweisen, dass eine Datenbank bereit ist?",
        "expected_keywords": ["depends_on", "running", "ready", "healthcheck", "service_healthy"],
        "relevant_sources": ["docker-compose-startup-order", "docker-compose-services-reference"],
        "origin_note": "Manually derived from Docker Compose startup order and healthcheck documentation.",
    },
    {
        "id": "Q048",
        "difficulty": "traceability",
        "category": "traceability",
        "category_label": "Nachvollziehbarkeit",
        "expected_relation_hops": 3,
        "question": "Why can mounting a volume over an image directory hide existing image files instead of merging them?",
        "question_de": "Warum kann ein Volume-Mount ueber einem Image-Verzeichnis vorhandene Image-Dateien verdecken, statt sie zusammenzufuehren?",
        "expected_keywords": ["mount", "existing data", "volume", "hide", "image files"],
        "relevant_sources": ["docker-storage-volumes", "docker-storage-overview"],
        "origin_note": "Manually derived from Docker volume mount behavior documentation.",
    },
]


def add_source() -> None:
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    by_id = {source["id"]: source for source in sources}
    by_id[NEW_SOURCE["id"]] = NEW_SOURCE
    sources = sorted(by_id.values(), key=lambda item: item["id"])
    SOURCES_PATH.write_text(
        json.dumps(sources, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_graph_items() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))

    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    for node in NEW_NODES:
        nodes_by_id[node["id"]] = node
    graph["nodes"] = list(nodes_by_id.values())

    def edge_key(edge: dict[str, object]) -> tuple[str, str, str]:
        return (
            str(edge["source"]),
            str(edge["relation"]),
            str(edge["target"]),
        )

    edges_by_key = {edge_key(edge): edge for edge in graph["edges"]}
    for source, relation, target, evidence, source_ids in NEW_EDGES:
        edges_by_key[(source, relation, target)] = {
            "source": source,
            "relation": relation,
            "target": target,
            "evidence": evidence,
            "source_ids": source_ids,
        }
    graph["edges"] = list(edges_by_key.values())

    GRAPH_PATH.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def add_questions() -> None:
    questions = []
    if QUESTIONS_PATH.exists():
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                questions.append(json.loads(line))

    by_id = {question["id"]: question for question in questions}
    for question in NEW_QUESTIONS:
        by_id[question["id"]] = question

    for question in by_id.values():
        if not question.get("origin_note"):
            sources = ", ".join(question.get("relevant_sources", []))
            question["origin_note"] = (
                "Manually derived from official Docker documentation and the "
                f"controlled troubleshooting case catalog. Relevant sources: {sources}."
            )

    ordered = sorted(by_id.values(), key=lambda item: item["id"])
    QUESTIONS_PATH.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in ordered) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    add_source()
    add_graph_items()
    add_questions()
    print("Dataset expanded after meeting feedback.")
    print(f"- Added/updated source: {NEW_SOURCE['id']}")
    print(f"- Added/updated nodes: {len(NEW_NODES)}")
    print(f"- Added/updated edges: {len(NEW_EDGES)}")
    print(f"- Added/updated questions: {len(NEW_QUESTIONS)}")


if __name__ == "__main__":
    main()
