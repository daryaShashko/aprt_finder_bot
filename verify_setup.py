import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add current dir to path so we can import modules
sys.path.append(os.getcwd())

import database
import scraper
import ai_agent

class TestApartmentHunter(unittest.TestCase):
    def test_database_init(self):
        """Test if database initializes without error."""
        try:
            database.init_db()
            print("✅ Database init successful")
        except Exception as e:
            self.fail(f"Database init failed: {e}")

    @patch('scraper.requests.get')
    def test_scraper_fetch_urls(self, mock_get):
        """Test URL fetching logic (mocked)."""
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.content = b'<html><a href="/d/oferta/test-ad-ID123.html">Test Ad</a></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        urls = scraper.fetch_ad_urls("http://mock-url")
        self.assertIn("https://www.olx.pl/d/oferta/test-ad-ID123.html", urls)
        print("✅ Scraper fetch URLs logic successful")

    @patch('ai_agent.genai.GenerativeModel')
    def test_ai_agent(self, mock_model_class):
        """Test AI agent JSON parsing (mocked)."""
        # Mock Gemini response
        mock_model = mock_model_class.return_value
        mock_response = MagicMock()
        mock_response.text = '```json\n{"total_cost": "2000 PLN", "deposit": "2000", "pets_allowed": true, "summary_ru": "Хорошая квартира."}\n```'
        mock_model.generate_content.return_value = mock_response
        
        # We need to set API key to bypass the check in analyze_ad, or mock os.getenv (but api_key is read at module level)
        # Re-import or set variable if possible. 
        # Since ai_agent reads env at top level, we might skip the API check if we mock the whole function, 
        # but let's try to mock the model interaction which happens inside.
        # Ensure we have a dummy key set in env for logic to pass
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "dummy"}):
            # Reload module to pick up env if needed, but it was already imported. 
            # let's just force the api_key global variable if possible or rely on the function checking it.
            # actually ai_agent.api_key is set at import time.
            
            # For test purpose, let's just set the module variable directly if not set
            if not ai_agent.api_key:
                ai_agent.api_key = "dummy_key_for_test"

            result = ai_agent.analyze_ad("some text")
            self.assertEqual(result['total_cost'], "2000 PLN")
            self.assertTrue(result['pets_allowed'])
            print("✅ AI Agent parsing logic successful")

if __name__ == '__main__':
    unittest.main()
