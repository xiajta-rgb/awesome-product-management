import json
import copy

from src.common.ontology import (
    CLOTHING_ONTOLOGY,
    CATEGORY_COLOR_MAPPING,
    COLOR_TAG_MAPPING,
    MATERIAL_TAG_MAPPING,
    DESIGN_TAG_MAPPING,
    FIT_TAG_MAPPING,
    VALID_STANDARDIZED_TAGS,
    GENDER_KEYWORDS,
    CATEGORY_KEYWORDS,
    SUB_CATEGORY_KEYWORDS,
)


class OntologyEngine:
    def __init__(self):
        self.ontology = copy.deepcopy(CLOTHING_ONTOLOGY)
        self.category_color_mapping = copy.deepcopy(CATEGORY_COLOR_MAPPING)
        self.color_tag_mapping = dict(COLOR_TAG_MAPPING)
        self.material_tag_mapping = dict(MATERIAL_TAG_MAPPING)
        self.design_tag_mapping = dict(DESIGN_TAG_MAPPING)
        self.fit_tag_mapping = dict(FIT_TAG_MAPPING)
        self.valid_standardized_tags = {
            "color": set(self.color_tag_mapping.values()),
            "material": set(self.material_tag_mapping.values()),
            "design": set(self.design_tag_mapping.values()),
            "fit": set(self.fit_tag_mapping.values()),
        }
        self.gender_keywords = dict(GENDER_KEYWORDS)
        self.category_keywords = dict(CATEGORY_KEYWORDS)
        self.sub_category_keywords = dict(SUB_CATEGORY_KEYWORDS)

    def _get_mapping_by_dimension(self, dimension):
        mappings = {
            "color": self.color_tag_mapping,
            "material": self.material_tag_mapping,
            "design": self.design_tag_mapping,
            "fit": self.fit_tag_mapping,
        }
        if dimension not in mappings:
            raise ValueError(f"Invalid dimension: {dimension}. Must be one of color, material, design, fit")
        return mappings[dimension]

    def standardize_tag(self, raw_tag, dimension):
        mapping = self._get_mapping_by_dimension(dimension)
        tag_lower = raw_tag.strip().lower()
        for key, value in mapping.items():
            if key.lower() == tag_lower:
                return value
        return raw_tag

    def standardize_tags(self, tags, dimension):
        return [self.standardize_tag(tag, dimension) for tag in tags]

    def get_category_hierarchy(self, gender):
        gender_map = {
            "男装": "Menswear",
            "男": "Menswear",
            "Menswear": "Menswear",
            "menswear": "Menswear",
            "女装": "Womenswear",
            "女": "Womenswear",
            "Womenswear": "Womenswear",
            "womenswear": "Womenswear",
        }
        key = gender_map.get(gender)
        if key is None:
            raise ValueError(f"Invalid gender: {gender}. Must be one of Menswear, Womenswear, 男装, 女装")
        return copy.deepcopy(self.ontology.get(key, {}))

    def match_category(self, product_title, features):
        result = {
            "gender": None,
            "category_main": None,
            "category_sub": None,
        }
        if not product_title:
            return result

        title_lower = product_title.lower()

        all_gender_matches = []
        for gender_key, keywords in self.gender_keywords.items():
            for kw in keywords:
                if kw.lower() in title_lower:
                    all_gender_matches.append((gender_key, len(kw)))
        all_gender_matches.sort(key=lambda x: x[1], reverse=True)
        if all_gender_matches:
            result["gender"] = all_gender_matches[0][0]

        if result["gender"] is None:
            if features and isinstance(features, dict):
                fit_tags = features.get("fit", [])
                if isinstance(fit_tags, list):
                    for tag in fit_tags:
                        tag_lower = tag.lower() if isinstance(tag, str) else ""
                        if tag_lower in ("high rise", "cropped", "stretch fit"):
                            result["gender"] = "Womenswear"
                            break
            if result["gender"] is None:
                result["gender"] = "Menswear"

        best_category = None
        best_score = 0
        for cat_key, keywords in self.category_keywords.items():
            score = 0
            for kw in keywords:
                if kw.lower() in title_lower:
                    score += 1
            if features and isinstance(features, dict):
                color_tags = features.get("color", [])
                if isinstance(color_tags, list) and cat_key in self.category_color_mapping:
                    valid_colors = self.category_color_mapping[cat_key]
                    for tag in color_tags:
                        if tag in valid_colors:
                            score += 1
            if score > best_score:
                best_score = score
                best_category = cat_key

        if best_category:
            result["category_main"] = best_category
        else:
            result["category_main"] = "Casual Sport"

        best_sub = None
        best_sub_score = 0
        if result["gender"] in self.ontology:
            gender_cats = self.ontology[result["gender"]]
            if result["category_main"] in gender_cats:
                subs = gender_cats[result["category_main"]]
                for sub in subs:
                    score = 0
                    if sub in self.sub_category_keywords:
                        for kw in self.sub_category_keywords[sub]:
                            if kw.lower() in title_lower:
                                score += 1
                    if sub.lower() in title_lower:
                        score += 2
                    if score > best_sub_score:
                        best_sub_score = score
                        best_sub = sub

        if best_sub:
            result["category_sub"] = best_sub
        else:
            if result["gender"] in self.ontology and result["category_main"] in self.ontology[result["gender"]]:
                subs = self.ontology[result["gender"]][result["category_main"]]
                result["category_sub"] = subs[0] if subs else None

        return result

    def validate_tag(self, standardized_tag, dimension):
        if dimension not in self.valid_standardized_tags:
            return False
        return standardized_tag in self.valid_standardized_tags[dimension]

    def add_tag_mapping(self, raw_tag, standardized_tag, dimension):
        mapping = self._get_mapping_by_dimension(dimension)
        mapping[raw_tag] = standardized_tag
        self.valid_standardized_tags[dimension].add(standardized_tag)

    def update_tag_mapping(self, raw_tag, new_standardized_tag, dimension):
        mapping = self._get_mapping_by_dimension(dimension)
        if raw_tag not in mapping:
            raise KeyError(f"Raw tag '{raw_tag}' not found in {dimension} mapping")
        old_standardized = mapping[raw_tag]
        mapping[raw_tag] = new_standardized_tag
        self.valid_standardized_tags[dimension].add(new_standardized_tag)
        still_used = any(v == old_standardized for v in mapping.values())
        if not still_used:
            self.valid_standardized_tags[dimension].discard(old_standardized)

    def remove_tag_mapping(self, raw_tag, dimension):
        mapping = self._get_mapping_by_dimension(dimension)
        if raw_tag not in mapping:
            raise KeyError(f"Raw tag '{raw_tag}' not found in {dimension} mapping")
        removed_standardized = mapping.pop(raw_tag)
        still_used = any(v == removed_standardized for v in mapping.values())
        if not still_used:
            self.valid_standardized_tags[dimension].discard(removed_standardized)

    def add_sub_category(self, gender, category_main, sub_name):
        gender_map = {
            "男装": "Menswear",
            "男": "Menswear",
            "Menswear": "Menswear",
            "menswear": "Menswear",
            "女装": "Womenswear",
            "女": "Womenswear",
            "Womenswear": "Womenswear",
            "womenswear": "Womenswear",
        }
        key = gender_map.get(gender, gender)
        if key not in self.ontology:
            raise ValueError(f"Invalid gender: {gender}")
        if category_main not in self.ontology[key]:
            raise ValueError(f"Invalid category_main: {category_main} for gender {key}")
        if sub_name not in self.ontology[key][category_main]:
            self.ontology[key][category_main].append(sub_name)

    def save_to_file(self, filepath):
        data = {
            "ontology": self.ontology,
            "category_color_mapping": self.category_color_mapping,
            "color_tag_mapping": self.color_tag_mapping,
            "material_tag_mapping": self.material_tag_mapping,
            "design_tag_mapping": self.design_tag_mapping,
            "fit_tag_mapping": self.fit_tag_mapping,
            "gender_keywords": self.gender_keywords,
            "category_keywords": self.category_keywords,
            "sub_category_keywords": self.sub_category_keywords,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ontology = data.get("ontology", self.ontology)
        self.category_color_mapping = data.get("category_color_mapping", self.category_color_mapping)
        self.color_tag_mapping = data.get("color_tag_mapping", self.color_tag_mapping)
        self.material_tag_mapping = data.get("material_tag_mapping", self.material_tag_mapping)
        self.design_tag_mapping = data.get("design_tag_mapping", self.design_tag_mapping)
        self.fit_tag_mapping = data.get("fit_tag_mapping", self.fit_tag_mapping)
        self.gender_keywords = data.get("gender_keywords", self.gender_keywords)
        self.category_keywords = data.get("category_keywords", self.category_keywords)
        self.sub_category_keywords = data.get("sub_category_keywords", self.sub_category_keywords)
        self.valid_standardized_tags = {
            "color": set(self.color_tag_mapping.values()),
            "material": set(self.material_tag_mapping.values()),
            "design": set(self.design_tag_mapping.values()),
            "fit": set(self.fit_tag_mapping.values()),
        }
