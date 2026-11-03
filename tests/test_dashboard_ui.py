from __future__ import annotations

import unittest

from tools.serve_dashboard import DASHBOARD_HTML, STATE


class DashboardUiTests(unittest.TestCase):
    def test_catalog_exposes_all_questions_with_german_display_text(self) -> None:
        questions = STATE.question_list()

        self.assertEqual(48, len(questions))
        self.assertTrue(all(question["question_de"] for question in questions))
        self.assertTrue(all("difficulty" in question for question in questions))
        self.assertTrue(
            all("expected_relation_hops" in question for question in questions)
        )

    def test_catalog_question_runs_both_methods_without_manual_text(self) -> None:
        question = STATE.question_by_id("Q002")
        self.assertIsNotNone(question)

        result = STATE.ask_both(str(question["question"]), "Q002")

        self.assertEqual("classic", result["classic"]["method"])
        self.assertEqual("graph", result["graph"]["method"])
        self.assertTrue(result["reference"]["reference_answer"])

    def test_visible_interface_labels_are_german(self) -> None:
        for expected in (
            "Katalogfrage auswählen",
            "Beide Methoden vergleichen",
            "Vollständiger Fragenkatalog",
            "Vergleichsergebnis",
            "Abgerufene Evidenz",
        ):
            self.assertIn(expected, DASHBOARD_HTML)

        for unexpected in (
            "Pregunta",
            "Comparar",
            "Categorías",
            "Respuesta de referencia",
            "Sin evidencias",
        ):
            self.assertNotIn(unexpected, DASHBOARD_HTML)


if __name__ == "__main__":
    unittest.main()
