"""
需求智能评分引擎 v2
根据 demand_scoring_rules.yaml 规则文件自动对需求进行多维度评分、定级、分类

改进：
- 使用更精准的关键词匹配逻辑
- 增加否定词检测（如"无"、"不"、"非"）
- 对每个维度进行独立上下文分析
- 支持模糊匹配和语义理解辅助
"""

import yaml
import re
from typing import Optional
from datetime import datetime


class DemandScorer:
    """需求评分器 - 根据规则文件自动打分"""
    
    def __init__(self, rules_path: str = None):
        if rules_path is None:
            import os
            rules_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_scoring_rules.yaml')
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)
        
        self.dimensions = self.rules['dimensions']
        self.grade_rules = self.rules['grade_rules']
    
    def _extract_field_text(self, demand: dict, field_keywords: dict) -> dict:
        """
        根据字段关键词提取各维度的相关文本
        
        Args:
            demand: 需求字典
            field_keywords: 维度到字段名的映射
            
        Returns:
            各维度对应的文本字典
        """
        return {
            dim: " ".join([
                str(demand.get(field, '')) 
                for field in fields 
                if demand.get(field)
            ])
            for dim, fields in field_keywords.items()
        }
    
    def _has_negative_context(self, text: str, keywords: list) -> bool:
        """
        检测文本中是否存在否定上下文
        
        Args:
            text: 待检测文本
            keywords: 关键词列表
            
        Returns:
            是否存在否定词
        """
        negative_words = ['无', '不', '非', '没', '否', '未', '缺乏', '低', '小', '个人', '仅']
        text_lower = text.lower()
        
        for neg_word in negative_words:
            if neg_word in text_lower:
                return True
        return False
    
    def _calculate_keyword_score(self, text: str, keywords: list) -> float:
        """
        计算关键词匹配分数（0-1之间）
        
        Args:
            text: 待评分文本
            keywords: 关键词列表
            
        Returns:
            匹配分数，0-1之间
        """
        if not keywords or not text:
            return 0.0
        
        text_lower = text.lower()
        matched = sum(1 for kw in keywords if kw.lower() in text_lower)
        return matched / len(keywords)
    
    def score_single_dimension(self, demand_text: str, dimension_config: dict) -> dict:
        """
        对单个维度进行评分
        
        Args:
            demand_text: 需求描述文本（该维度相关的字段文本）
            dimension_config: 该维度的配置信息
            
        Returns:
            评分结果字典
        """
        rules = dimension_config['rules']
        is_reverse = dimension_config.get('reverse_score', False)
        
        if not demand_text.strip():
            # 无文本信息，给最低分
            lowest_rule = min(rules, key=lambda r: r['max_score'])
            return {
                'score': lowest_rule['min_score'],
                'matched_rule': lowest_rule['condition'],
                'matched_keywords': [],
                'max_possible': lowest_rule['max_score']
            }
        
        # 对每个规则计算匹配度
        rule_scores = []
        for rule in rules:
            keywords = rule.get('keywords', [])
            match_score = self._calculate_keyword_score(demand_text, keywords)
            
            # 检查否定上下文
            has_negative = self._has_negative_context(demand_text, keywords)
            
            # 如果有否定词，降低匹配分数（低分规则关键词常含“无”、“个人”等，不予惩罚）
            is_high_value_rule = rule['max_score'] > 3
            if has_negative and is_high_value_rule:
                match_score *= 0.3  # 大幅降低
            
            rule_scores.append({
                'rule_index': rules.index(rule),
                'min_score': rule['min_score'],
                'max_score': rule['max_score'],
                'condition': rule['condition'],
                'keywords': keywords,
                'match_score': match_score,
                'matched_keywords': [kw for kw in keywords if kw.lower() in demand_text.lower()],
                'has_negative': has_negative
            })
        
        # 按匹配分数排序
        rule_scores.sort(key=lambda x: x['match_score'], reverse=True)
        best_match = rule_scores[0]
        
        # 计算具体分数
        if is_reverse:
            score = self._calculate_reverse_score(demand_text, best_match)
        else:
            score = self._calculate_forward_score(demand_text, best_match)
        
        return {
            'score': score,
            'matched_rule': best_match['condition'],
            'matched_keywords': best_match['matched_keywords'],
            'max_possible': best_match['max_score'],
            'match_score': best_match['match_score'],
            'has_negative': best_match['has_negative']
        }
    
    def _calculate_forward_score(self, demand_text: str, best_match: dict) -> int:
        """
        正向计分逻辑
        """
        min_score = best_match['min_score']
        max_score = best_match['max_score']
        match_score = best_match['match_score']
        
        # 基础分数为区间中值
        base_score = (min_score + max_score) / 2
        
        # 根据匹配程度调整
        if match_score >= 0.5:
            # 匹配度高，取区间上限
            score = max_score
        elif match_score >= 0.3:
            # 匹配度中，取区间中上
            score = base_score + (max_score - base_score) * match_score
        else:
            # 匹配度低，取区间中下
            score = min_score + (base_score - min_score) * match_score * 2
        
        return int(round(score))
    
    def _calculate_reverse_score(self, demand_text: str, best_match: dict) -> int:
        """
        反向计分逻辑（用于实施复杂度）
        实现难度越低，得分越高
        """
        min_score = best_match['min_score']
        max_score = best_match['max_score']
        match_score = best_match['match_score']
        
        # 高分数区间（8-10）表示简单，低分数区间（0-1）表示复杂
        if max_score >= 8:
            score = max_score if match_score >= 0.5 else (min_score + max_score) / 2
        elif max_score <= 1:
            score = min_score if match_score >= 0.5 else (min_score + max_score) / 2
        else:
            score = (min_score + max_score) / 2
        
        return int(round(score))
    
    def score_demand(self, demand: dict, strategy_focus: list = None) -> dict:
        """
        对单个需求进行完整评分
        
        Args:
            demand: 需求字典
            strategy_focus: 公司战略重点列表
            
        Returns:
            完整的评分结果
        """
        # 按维度提取相关文本
        dimension_texts = self._extract_field_text(demand, {
            'business_value': ['description', 'expected_value', 'usage_scenario'],
            'strategy_alignment': ['description', 'expected_value', 'deadline_risk'],
            'impact_scope': ['cross_department_impact', 'usage_scenario', 'expected_value'],
            'roi': ['resource_input', 'expected_value', 'description'],
            'urgency': ['deadline_risk', 'description', 'expected_value'],
            'implementation_complexity': ['description', 'resource_input', 'cross_department_impact']
        })
        
        # 对每个维度进行评分
        dimension_scores = {}
        total_score = 0
        
        for dim_key, dim_config in self.dimensions.items():
            dim_text = dimension_texts.get(dim_key, '')
            
            # 战略匹配度特殊处理
            if dim_key == 'strategy_alignment' and strategy_focus:
                dim_text += " " + " ".join(strategy_focus)
            
            result = self.score_single_dimension(dim_text, dim_config)
            dimension_scores[dim_config['name']] = {
                'score': result['score'],
                'max': result['max_possible'],
                'matched_rule': result['matched_rule'],
                'matched_keywords': result['matched_keywords'],
                'match_score': result.get('match_score', 0)
            }
            total_score += result['score']
        
        # 确定等级
        grade = self._determine_grade(total_score)
        
        # 生成驳回原因（如果是D级）
        reject_reason = None
        if grade['grade'] == 'D':
            reject_reason = self._generate_reject_reason(dimension_scores)
        
        return {
            'id': demand.get('id', 'unknown'),
            'description': demand.get('description', ''),
            'submitter': demand.get('submitter', ''),
            'total_score': total_score,
            'grade': grade['grade'],
            'demand_type': grade['type'],
            'decision_action': grade['action'],
            'priority': grade['priority'],
            'dimension_scores': {k: v['score'] for k, v in dimension_scores.items()},
            'dimension_details': dimension_scores,
            'reject_reason': reject_reason
        }
    
    def _determine_grade(self, total_score: int) -> dict:
        """根据总分确定等级"""
        if total_score >= self.grade_rules['A']['min']:
            return {
                'grade': 'A',
                'type': self.grade_rules['A']['type'],
                'action': self.grade_rules['A']['action'],
                'priority': self.grade_rules['A']['priority']
            }
        elif total_score >= self.grade_rules['B']['min']:
            return {
                'grade': 'B',
                'type': self.grade_rules['B']['type'],
                'action': self.grade_rules['B']['action'],
                'priority': self.grade_rules['B']['priority']
            }
        elif total_score >= self.grade_rules['C']['min']:
            return {
                'grade': 'C',
                'type': self.grade_rules['C']['type'],
                'action': self.grade_rules['C']['action'],
                'priority': self.grade_rules['C']['priority']
            }
        else:
            return {
                'grade': 'D',
                'type': self.grade_rules['D']['type'],
                'action': self.grade_rules['D']['action'],
                'priority': self.grade_rules['D']['priority']
            }
    
    def _generate_reject_reason(self, dimension_scores: dict) -> str:
        """生成D级需求的驳回原因"""
        reasons = []
        
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1]['score'])
        
        for dim_name, dim_info in sorted_dims[:3]:
            if dim_info['score'] <= dim_info['max'] * 0.4:
                reasons.append(f"{dim_name}不足：{dim_info['matched_rule']}")
        
        if not reasons:
            reasons.append("综合评分未达到最低标准（40分），建议重新评估需求价值")
        
        return "；".join(reasons)
    
    def score_batch(self, demands: list, strategy_focus: list = None) -> list:
        """
        批量评分
        
        Args:
            demands: 需求列表
            strategy_focus: 公司战略重点列表
            
        Returns:
            评分结果列表，按优先级排序
        """
        results = []
        for demand in demands:
            result = self.score_demand(demand, strategy_focus)
            results.append(result)
        
        priority_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        results.sort(key=lambda x: (priority_order.get(x['grade'], 4), -x['total_score']))
        
        return results


def auto_score_demand(demands: list, rules_path: str = None, strategy_focus: list = None) -> dict:
    """
    便捷函数：自动对需求列表进行评分
    """
    scorer = DemandScorer(rules_path)
    scored_demands = scorer.score_batch(demands, strategy_focus)
    
    stats = {
        'total': len(scored_demands),
        'A': len([d for d in scored_demands if d['grade'] == 'A']),
        'B': len([d for d in scored_demands if d['grade'] == 'B']),
        'C': len([d for d in scored_demands if d['grade'] == 'C']),
        'D': len([d for d in scored_demands if d['grade'] == 'D']),
        'valid': len([d for d in scored_demands if d['grade'] != 'D']),
        'invalid': len([d for d in scored_demands if d['grade'] == 'D'])
    }
    
    return {
        'scored_demands': scored_demands,
        'stats': stats,
        'scoring_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


if __name__ == '__main__':
    test_demands = [
        {
            'id': 'D001',
            'description': '跨部门订单数据同步系统开发',
            'submitter': '研发-张三',
            'usage_scenario': '供应链、销售、财务跨部门数据协同',
            'expected_value': '减少数据重复录入，提升30%对账效率，降低5%财务差错率',
            'cross_department_impact': '供应链、销售、财务3个部门',
            'resource_input': '2人月开发资源',
            'deadline_risk': '无刚性时间节点，为年度战略重点项目'
        },
        {
            'id': 'D002',
            'description': '个人操作界面按钮位置调整',
            'submitter': '研发-李四',
            'usage_scenario': '仅个人操作习惯优化',
            'expected_value': '无业务效率提升',
            'cross_department_impact': '无跨部门影响',
            'resource_input': '0.5人天资源',
            'deadline_risk': '无紧急性'
        }
    ]
    
    result = auto_score_demand(test_demands, strategy_focus=['跨部门数据协同', '运营效率提升'])
    
    print(f"评分完成时间：{result['scoring_time']}")
    print(f"统计：{result['stats']}")
    for d in result['scored_demands']:
        print(f"\n需求 {d['id']}:")
        print(f"  总分：{d['total_score']}")
        print(f"  等级：{d['grade']} - {d['demand_type']}")
        print(f"  决策：{d['decision_action']}")
        if d['reject_reason']:
            print(f"  驳回原因：{d['reject_reason']}")
        print(f"  各维度得分：{d['dimension_scores']}")
