import logging

import requests

from src.common.config import IMAGE_RECOGNITION_API_KEY

logger = logging.getLogger(__name__)


class ImageRecognizer:

    API_URL = "https://api.imagerecognition.com/v1/recognize"

    def __init__(self):
        self.api_key = IMAGE_RECOGNITION_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def recognize_clothing_details(self, image_url):
        if not image_url:
            return {
                "collar_type": "",
                "sleeve_length": "",
                "zipper_position": "",
                "pocket_design": "",
                "stitching_type": "",
            }
        try:
            api_result = self._call_api(image_url)
            return self._parse_clothing_result(api_result)
        except Exception as e:
            logger.error("Image recognition failed for %s: %s", image_url, str(e))
            return {
                "collar_type": "",
                "sleeve_length": "",
                "zipper_position": "",
                "pocket_design": "",
                "stitching_type": "",
            }

    def batch_recognize(self, image_urls):
        results = []
        for url in image_urls:
            result = self.recognize_clothing_details(url)
            results.append(result)
        return results

    def _call_api(self, image_url):
        payload = {
            "image_url": image_url,
            "categories": [
                "collar_type",
                "sleeve_length",
                "zipper_position",
                "pocket_design",
                "stitching_type",
            ],
        }
        response = requests.post(
            self.API_URL, headers=self.headers, json=payload, timeout=60
        )
        response.raise_for_status()
        return response.json()

    def _parse_clothing_result(self, api_result):
        default = {
            "collar_type": "",
            "sleeve_length": "",
            "zipper_position": "",
            "pocket_design": "",
            "stitching_type": "",
        }
        if not api_result or not isinstance(api_result, dict):
            return default

        results = api_result.get("results", {})
        if isinstance(results, dict):
            for key in default:
                if key in results:
                    value = results[key]
                    if isinstance(value, dict):
                        default[key] = value.get("value", "")
                    elif isinstance(value, str):
                        default[key] = value
                    elif isinstance(value, list) and value:
                        default[key] = str(value[0])
        return default
