import unittest
import os
from unittest.mock import patch, MagicMock

# Import the modules under test
from skills import fetch_pictogram_by_keyword, generate_non_verbal_quiz
from agents import VisualBridgeAgent

class TestVisualBridgeSkills(unittest.TestCase):
    """
    Test suite for VisualBridge core skills in skills.py.
    """

    def test_fetch_pictogram_from_cache(self):
        """
        Verify that fetch_pictogram_by_keyword retrieves cached results successfully.
        """
        # Ensure 'hu:fa' is in our cache or mock the cache call
        res = fetch_pictogram_by_keyword("fa", locale="hu")
        self.assertIsNotNone(res)
        self.assertEqual(res["word"], "fa")
        self.assertTrue(res["success"])
        self.assertIsNotNone(res["image_url"])

    def test_fetch_pictogram_not_found(self):
        """
        Verify that fetch_pictogram_by_keyword handles non-existent words gracefully.
        """
        # A gibberish word that does not exist in ARASAAC
        res = fetch_pictogram_by_keyword("xyzpqrs12345", locale="hu")
        self.assertIsNotNone(res)
        self.assertFalse(res["success"])
        self.assertIsNone(res["image_url"])

    def test_generate_non_verbal_quiz_hu(self):
        """
        Verify quiz generation in Hungarian.
        """
        quiz = generate_non_verbal_quiz("víz", ["autó", "csokoládé"], locale="hu")
        self.assertEqual(quiz["question"], "Melyik a(z) víz?")
        self.assertGreater(len(quiz["options"]), 0)

        # Check that options contain the correct answer flagged as True
        correct_found = False
        for opt in quiz["options"]:
            if opt["word"] == "víz":
                self.assertTrue(opt["is_correct"])
                correct_found = True
        self.assertTrue(correct_found)

    def test_generate_non_verbal_quiz_en(self):
        """
        Verify quiz generation in English.
        """
        quiz = generate_non_verbal_quiz("water", ["car", "chocolate"], locale="en")
        self.assertEqual(quiz["question"], "Which one is water?")
        self.assertGreater(len(quiz["options"]), 0)

    def test_new_translations_loaded(self):
        """
        Verify that new navigation and simplifier translation keys are loaded and translated properly.
        """
        from i18n import TranslationManager
        mgr = TranslationManager()

        # Test in Hungarian
        mgr.set_language("hu")
        self.assertEqual(mgr.gettext("Text Simplifier"), "Szövegegyszerűsítő")
        self.assertEqual(mgr.gettext("🧭 Navigáció"), "🧭 Navigáció")

        # Test in English
        mgr.set_language("en")
        self.assertEqual(mgr.gettext("Text Simplifier"), "Text Simplifier")
        self.assertEqual(mgr.gettext("🧭 Navigáció"), "🧭 Navigation")


class TestVisualBridgeAgent(unittest.TestCase):
    """
    Test suite for VisualBridgeAgent in agents.py.
    """

    def setUp(self):
        self.agent = VisualBridgeAgent()

    def test_agent_is_mock_by_default(self):
        """
        Unless a real GEMINI_API_KEY is configured in the environment, the agent should default to mock mode.
        """
        # If running in environment without GEMINI_API_KEY, it must be mock
        if not os.getenv("GEMINI_API_KEY"):
            self.assertTrue(self.agent.is_mock)

    def test_simplify_text_mock_hu(self):
        """
        Verify mock text simplification for Hungarian.
        """
        res = self.agent.simplify_text("A tölgyfa hatalmas koronájával árnyékot ad. A tölgyfa vizet iszik.", lang="hu")
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertEqual(res[0], "A tölgyfa árnyékot ad.")

    def test_simplify_text_mock_vehicle_hu(self):
        """
        Verify mock text simplification for Hungarian vehicle story.
        """
        res = self.agent.simplify_text("A piros autó nagyon gyorsan száguld, a sárga busz pedig megáll.", lang="hu")
        self.assertIsInstance(res, list)
        self.assertEqual(res, ["Az autó megy.", "A busz megáll."])

    def test_simplify_text_mock_vehicle_en(self):
        """
        Verify mock text simplification for English vehicle story.
        """
        res = self.agent.simplify_text("The red car goes fast, but the yellow bus stops.", lang="en")
        self.assertIsInstance(res, list)
        self.assertEqual(res, ["The car goes.", "The bus stops."])

    def test_process_pipeline_mock_hu(self):
        """
        Verify the mock process pipeline output format.
        """
        res = self.agent.process_pipeline("A tölgyfa árnyékot ad. A tölgyfa vizet iszik.", lang="hu")
        self.assertIsNotNone(res)
        self.assertIn("processed_story", res)
        self.assertIsInstance(res["processed_story"], list)
        self.assertGreater(len(res["processed_story"]), 0)

        # Check structure of the first item
        item = res["processed_story"][0]
        self.assertIn("sentence", item)
        self.assertIn("tokens_with_pics", item)
        self.assertIsInstance(item["tokens_with_pics"], list)

    def test_simplify_text_mock_girl_hu(self):
        """
        Verify mock text simplification for Hungarian girl story.
        """
        res = self.agent.simplify_text("A kislány a szép babával játszik, miközben a pöttyös labda elgurul.", lang="hu")
        self.assertIsInstance(res, list)
        self.assertEqual(res, ["A kislány játszik.", "A baba szép.", "A labda elgurul."])

    def test_simplify_text_mock_girl_en(self):
        """
        Verify mock text simplification for English girl story.
        """
        res = self.agent.simplify_text("The little girl plays with the beautiful doll, while the polka dot ball rolls away.", lang="en")
        self.assertIsInstance(res, list)
        self.assertEqual(res, ["The girl plays.", "The doll is beautiful.", "The ball rolls away."])



if __name__ == "__main__":
    unittest.main()
