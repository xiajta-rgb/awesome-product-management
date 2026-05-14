from datetime import datetime


class ElementPushBuilder:

    def build_top10_elements(self, elements: list) -> dict:
        top_elements = elements[:10]
        formatted_elements = []
        for element in top_elements:
            formatted_elements.append(
                {
                    "element": element.get("element", ""),
                    "frequency": element.get("frequency", 0),
                    "is_core": element.get("is_core", False),
                    "margin": element.get("margin", 0),
                    "recommendation_weight": element.get("recommendation_weight", 1.0),
                    "margin_penalty_applied": element.get("margin_penalty_applied", False),
                }
            )
        return {
            "push_type": "top10_elements",
            "title": "Top10核心爆品元素推送",
            "elements": formatted_elements,
        }

    def build_element_matching_suggestions(self, elements: list) -> dict:
        suggestions = []
        for element in elements:
            suggestion = {
                "category": element.get("matched_category", ""),
                "combination": element.get("combination", ""),
                "target_audience": element.get("target_audience", ""),
                "description": element.get("description", ""),
                "data_source": element.get("data_source", ""),
            }
            suggestions.append(suggestion)
        return {
            "push_type": "element_matching_suggestions",
            "title": "元素搭配建议推送",
            "suggestions": suggestions,
        }

    def build_visual_diff_suggestions(self, suggestions: list) -> dict:
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append(
                {
                    "element": suggestion.get("element", ""),
                    "suggestion_type": suggestion.get("suggestion_type", ""),
                    "description": suggestion.get("description", ""),
                    "data_source": suggestion.get("data_source", ""),
                }
            )
        return {
            "push_type": "visual_diff_suggestions",
            "title": "视觉差异化建议推送",
            "suggestions": formatted_suggestions,
        }

    def build_weekly_element_report(
        self,
        elements: list,
        suggestions: list,
        visual_suggestions: list,
    ) -> dict:
        top10 = self.build_top10_elements(elements)
        matching = self.build_element_matching_suggestions(suggestions)
        visual = self.build_visual_diff_suggestions(visual_suggestions)
        return {
            "push_type": "weekly_element_report",
            "title": "每周爆品元素推荐推送",
            "top10_elements": top10,
            "matching_suggestions": matching,
            "visual_suggestions": visual,
            "generated_at": datetime.now().isoformat(),
        }
