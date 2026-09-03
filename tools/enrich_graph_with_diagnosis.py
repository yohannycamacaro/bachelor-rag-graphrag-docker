from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = PROJECT_ROOT / "data" / "knowledge" / "docker_support_graph.json"


DIAGNOSIS_NODES = [
    {
        "id": "diagnosis.docker_info",
        "type": "diagnosis",
        "label": "Run docker info",
        "description": "Check whether the Docker client can communicate with the configured Docker daemon.",
        "keywords": ["docker info", "daemon", "client", "DOCKER_HOST", "connectivity"],
    },
    {
        "id": "diagnosis.compose_config",
        "type": "diagnosis",
        "label": "Inspect resolved Compose configuration",
        "description": "Use docker compose config to see the final Compose model after file selection, interpolation and merges.",
        "keywords": ["docker compose config", "resolved", "compose file", "configuration"],
    },
    {
        "id": "diagnosis.compose_config_environment",
        "type": "diagnosis",
        "label": "Inspect Compose interpolation environment",
        "description": "Use docker compose config --environment to inspect values used for Compose interpolation.",
        "keywords": [
            "docker compose config --environment",
            ".env",
            "interpolation",
            "environment values",
            "uses for interpolation",
            "check environment values",
        ],
    },
    {
        "id": "diagnosis.network_inspect",
        "type": "diagnosis",
        "label": "Inspect Docker network membership",
        "description": "Check whether the relevant services are attached to the same Docker network.",
        "keywords": ["docker network inspect", "network membership", "same network", "connectivity"],
    },
    {
        "id": "diagnosis.container_environment",
        "type": "diagnosis",
        "label": "Inspect runtime container environment",
        "description": "Inspect the environment variables that are actually visible inside the running container.",
        "keywords": ["container environment", "runtime environment", "printenv", "env"],
    },
    {
        "id": "diagnosis.healthcheck_logs",
        "type": "diagnosis",
        "label": "Inspect healthcheck and logs",
        "description": "Check the configured healthcheck, container logs and healthcheck output.",
        "keywords": ["healthcheck", "logs", "endpoint", "timeout", "retries"],
    },
    {
        "id": "diagnosis.mounts",
        "type": "diagnosis",
        "label": "Inspect mounts and volumes",
        "description": "Inspect configured mounts, target paths and Docker volumes.",
        "keywords": ["mounts", "volume", "bind mount", "docker inspect", "target path"],
    },
    {
        "id": "diagnosis.compose_profiles",
        "type": "diagnosis",
        "label": "Inspect Compose profiles",
        "description": "Check whether a service is assigned to a profile and whether that profile is enabled.",
        "keywords": ["profiles", "COMPOSE_PROFILES", "--profile", "inactive"],
    },
]


DIAGNOSIS_EDGES = [
    {
        "source": "problem.daemon_unreachable",
        "relation": "diagnosed_by",
        "target": "diagnosis.docker_info",
        "evidence": "Use docker info and DOCKER_HOST checks to verify whether the Docker client reaches the intended daemon.",
        "source_ids": ["docker-daemon-troubleshoot"],
    },
    {
        "source": "problem.service_name_unreachable",
        "relation": "diagnosed_by",
        "target": "diagnosis.network_inspect",
        "evidence": "Inspect network membership to confirm that both Compose services share a network.",
        "source_ids": ["docker-compose-networking", "docker-compose-networks-reference"],
    },
    {
        "source": "cause.wrong_port_context",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_config",
        "evidence": "Inspect the resolved Compose configuration to distinguish host ports from container ports.",
        "source_ids": ["docker-compose-networking"],
    },
    {
        "source": "problem.env_missing",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_config_environment",
        "evidence": "Use docker compose config --environment to inspect interpolation values from environment sources.",
        "source_ids": ["docker-compose-env-interpolation"],
    },
    {
        "source": "problem.env_missing",
        "relation": "diagnosed_by",
        "target": "diagnosis.container_environment",
        "evidence": "Inspect the runtime container environment to check which variables the application can actually read.",
        "source_ids": ["docker-compose-env"],
    },
    {
        "source": "cause.value_overridden",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_config",
        "evidence": "The resolved Compose model helps identify which configuration source supplied the active value.",
        "source_ids": ["docker-compose-env-precedence", "docker-compose-env-interpolation"],
    },
    {
        "source": "problem.unexpected_project_name",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_config",
        "evidence": "The resolved Compose model and project settings help explain generated name prefixes.",
        "source_ids": ["docker-compose-predefined-env", "docker-compose-networking"],
    },
    {
        "source": "problem.wrong_compose_file",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_config",
        "evidence": "The resolved Compose model reveals which Compose file and merged configuration are active.",
        "source_ids": ["docker-compose-predefined-env", "docker-compose-env-interpolation"],
    },
    {
        "source": "problem.profile_service_inactive",
        "relation": "diagnosed_by",
        "target": "diagnosis.compose_profiles",
        "evidence": "Check profiles in the service definition and verify COMPOSE_PROFILES or --profile.",
        "source_ids": ["docker-compose-predefined-env", "docker-compose-services-reference"],
    },
    {
        "source": "problem.database_not_ready",
        "relation": "diagnosed_by",
        "target": "diagnosis.healthcheck_logs",
        "evidence": "Healthcheck configuration and logs show whether a dependency is merely started or actually ready.",
        "source_ids": ["docker-compose-startup-order", "docker-compose-services-reference"],
    },
    {
        "source": "problem.unhealthy_container",
        "relation": "diagnosed_by",
        "target": "diagnosis.healthcheck_logs",
        "evidence": "Healthcheck output and logs help determine why a running container is marked unhealthy.",
        "source_ids": ["docker-compose-services-reference", "docker-compose-startup-order"],
    },
    {
        "source": "problem.data_not_persistent",
        "relation": "diagnosed_by",
        "target": "diagnosis.mounts",
        "evidence": "Mount inspection shows whether persistent storage is attached to the path used by the application.",
        "source_ids": ["docker-storage-volumes"],
    },
    {
        "source": "problem.bind_or_volume_confusion",
        "relation": "diagnosed_by",
        "target": "diagnosis.mounts",
        "evidence": "Mount inspection helps decide whether direct host access or Docker-managed storage is needed.",
        "source_ids": ["docker-storage-overview", "docker-storage-volumes"],
    },
    {
        "source": "problem.files_hidden_by_mount",
        "relation": "diagnosed_by",
        "target": "diagnosis.mounts",
        "evidence": "Inspect mount target paths when files from the image appear to be hidden.",
        "source_ids": ["docker-storage-volumes", "docker-storage-overview"],
    },
    {
        "source": "problem.external_dns_fails",
        "relation": "diagnosed_by",
        "target": "diagnosis.docker_info",
        "evidence": "Check daemon and resolver configuration when external DNS fails inside containers.",
        "source_ids": ["docker-daemon-troubleshoot"],
    },
    {
        "source": "problem.external_network_missing",
        "relation": "diagnosed_by",
        "target": "diagnosis.network_inspect",
        "evidence": "List and inspect Docker networks to verify whether an external network exists before Compose starts.",
        "source_ids": ["docker-compose-networking", "docker-compose-networks-reference"],
    },
]


def main() -> None:
    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph = json.load(file)

    existing_node_ids = {node["id"] for node in graph["nodes"]}
    for node in DIAGNOSIS_NODES:
        if node["id"] not in existing_node_ids:
            graph["nodes"].append(node)
            existing_node_ids.add(node["id"])

    existing_edges = {
        (edge["source"], edge["relation"], edge["target"])
        for edge in graph["edges"]
    }
    for edge in DIAGNOSIS_EDGES:
        edge_key = (edge["source"], edge["relation"], edge["target"])
        if edge_key not in existing_edges:
            graph["edges"].append(edge)
            existing_edges.add(edge_key)

    with GRAPH_PATH.open("w", encoding="utf-8") as file:
        json.dump(graph, file, indent=2, ensure_ascii=False)
        file.write("\n")

    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Relations: {len(graph['edges'])}")


if __name__ == "__main__":
    main()
