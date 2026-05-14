import json
import logging

import requests

from src.common.config import LLM_API_KEY

logger = logging.getLogger(__name__)


class LLMExtractor:

    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-4"

    def __init__(self):
        self.api_key = LLM_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def extract_features(self, product_description):
        if not product_description:
            return {
                "color": "",
                "material": "",
                "design": "",
                "fit": "",
                "scene": "",
            }
        try:
            prompt = self._build_prompt(product_description)
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a fashion product feature extraction assistant."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            }
            response = requests.post(
                self.API_URL, headers=self.headers, json=payload, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return self._parse_response(content)
        except Exception as e:
            logger.error("LLM extraction failed: %s", str(e))
            return {
                "color": "",
                "material": "",
                "design": "",
                "fit": "",
                "scene": "",
            }

    def batch_extract(self, descriptions):
        results = []
        for desc in descriptions:
            result = self.extract_features(desc)
            results.append(result)
        return results

    def _build_prompt(self, description):
        prompt = (
            "Extract the following fashion product features from the description below. "
            "Return the result as a JSON object with these exact keys: "
            '"color", "material", "design", "fit", "scene".\n\n'
            "Rules:\n"
            '- "color": Extract the main color(s) of the product.\n'
            '- "material": Extract the fabric/material information.\n'
            '- "design": Extract design highlights (e.g., patterns, collar style, pocket design).\n'
            '- "fit": Extract the fit type (e.g., slim, regular, loose, oversized).\n'
            '- "scene": Extract suitable scenarios (e.g., business casual, outdoor, sport, daily).\n\n'
            f"Product Description:\n{description}\n\n"
            "Return ONLY the JSON object, no other text."
        )
        return prompt

    def _parse_response(self, response):
        default = {
            "color": "",
            "material": "",
            "design": "",
            "fit": "",
            "scene": "",
        }
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])
            result = json.loads(cleaned)
            for key in default:
                if key not in result:
                    result[key] = ""
            return result
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON: %s", response[:200])
            return default
