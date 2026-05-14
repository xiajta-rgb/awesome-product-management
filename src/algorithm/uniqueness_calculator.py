import math


class UniquenessCalculator:
    def calculate(self, product, user_products):
        if not user_products:
            return 0.0
        product_vector = self._extract_feature_vector(product)
        if not product_vector:
            return 0.0
        max_similarity = 0.0
        for user_product in user_products:
            user_vector = self._extract_feature_vector(user_product)
            if not user_vector:
                continue
            similarity = self._cosine_similarity(product_vector, user_vector)
            if similarity > max_similarity:
                max_similarity = similarity
        return round(max_similarity, 4)

    def _extract_feature_vector(self, product):
        features = product.get("standardized_features", {})
        category_main = product.get("category_main", "")
        category_sub = product.get("category_sub", "")
        dimensions = ["color", "material", "design", "fit"]
        all_tags = set()
        if isinstance(features, dict):
            for dim in dimensions:
                tags = features.get(dim, [])
                if isinstance(tags, list):
                    all_tags.update(tags)
                elif isinstance(tags, str):
                    all_tags.add(tags)
        if category_main:
            all_tags.add(f"cat_{category_main}")
        if category_sub:
            all_tags.add(f"sub_{category_sub}")
        vector = sorted(list(all_tags))
        return vector

    def _cosine_similarity(self, vec1, vec2):
        if not vec1 or not vec2:
            return 0.0
        set1 = set(vec1)
        set2 = set(vec2)
        intersection = set1 & set2
        if not intersection:
            return 0.0
        magnitude1 = math.sqrt(len(set1))
        magnitude2 = math.sqrt(len(set2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return len(intersection) / (magnitude1 * magnitude2)

    def filter_by_uniqueness(self, products, user_products, threshold=0.7):
        filtered = []
        for product in products:
            similarity = self.calculate(product, user_products)
            if similarity < threshold:
                product["uniqueness_score"] = 1.0 - similarity
                filtered.append(product)
        return filtered
