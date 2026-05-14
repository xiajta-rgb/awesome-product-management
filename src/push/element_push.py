from datetime import datetime


class ElementPushBuilder:

    def build_top10_elements(self, elements: list) -> dict:
        top_elements = elements[:10]
        formatted_elements = []
        for element in top_elements:
            formatted_elements.append(
                {
                    "description": element.get("description", ""),
                    "application_scene": element.get("application_scene", ""),
                    "matched_category": element.get("matched_category", ""),
                    "data_source": element.get("data_source", ""),
                    "standardized_tags": element.get("standardized_tags", []),
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
                    "visual_element": suggestion.get("visual_element", ""),
                    "differentiation_strategy": suggestion.get(
                        "differentiation_strategy", ""
                    ),
                    "reference_examples": suggestion.get("reference_examples", []),
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
