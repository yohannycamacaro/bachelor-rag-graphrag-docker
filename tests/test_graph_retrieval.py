from __future__ import annotations

import unittest

from rag_compare.graph_retrieval import GraphRagRetriever


class GraphRetrievalRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.retriever = GraphRagRetriever()

    def test_h010_covers_readiness_port_and_network_chain(self) -> None:
        question = (
            "A web service uses depends_on with service_healthy, but startup still "
            "fails because the database healthcheck probes the published host port "
            "and both services are on different networks. Trace the full failure "
            "chain and give the required corrections."
        )
        answer = str(self.retriever.answer(question, top_k=8)["answer"]).lower()

        for expected in (
            "service_healthy",
            "healthcheck",
            "container port",
            "service name",
            "share a network",
        ):
            self.assertIn(expected, answer)
        self.assertNotIn("scaled service has multiple host ports", answer)

    def test_scaled_service_question_keeps_replica_path(self) -> None:
        question = (
            "A scaled web service publishes dynamic host ports. Which command with "
            "--index identifies the host port for replica 2?"
        )
        answer = str(self.retriever.answer(question, top_k=8)["answer"]).lower()

        self.assertIn("docker compose port", answer)
        self.assertIn("replica", answer)
        self.assertIn("--index", answer)

    def test_recreated_service_keeps_dynamic_ip_path(self) -> None:
        question = (
            "After a service is recreated, why should clients reconnect through the "
            "service name rather than a cached container IP?"
        )
        answer = str(self.retriever.answer(question, top_k=8)["answer"]).lower()

        self.assertIn("container ip is dynamic", answer)
        self.assertIn("service name", answer)


if __name__ == "__main__":
    unittest.main()
