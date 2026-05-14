"""
需求库管理 v4
+ 去重检查（关键词重叠度）
+ 变更历史追踪
+ 状态流转校验
"""

import json
import os
from datetime import datetime


VALID_TRANSITIONS = {
    '待评审': ['已评审'],
    '已评审': ['已立项', '已驳回', '已暂缓'],
    '已暂缓': ['已立项', '已驳回'],
    '已立项': ['开发中', '已取消'],
    '开发中': ['已完成', '已取消'],
    '已驳回': [],
    '已取消': [],
    '已完成': [],
}


class DemandLibrary:

    def __init__(self, lib_path: str = None):
        if lib_path is None:
            lib_path = os.path.join(os.path.dirname(__file__), '..', 'rules', 'demand_library.json')
        self.lib_path = lib_path
        self._ensure_file()
        self._load()

    def _ensure_file(self):
        if not os.path.exists(self.lib_path):
            with open(self.lib_path, 'w', encoding='utf-8') as f:
                json.dump({"version": "4.0", "next_id": 1, "demands": []}, f, ensure_ascii=False, indent=2)

    def _load(self):
        with open(self.lib_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _add_history(self, demand: dict, action: str, detail: str = ''):
        if 'change_history' not in demand:
            demand['change_history'] = []
        demand['change_history'].append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'action': action,
            'detail': detail
        })

    @staticmethod
    def _keyword_overlap(text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            cn1 = set(text1.lower())
            cn2 = set(text2.lower())
            if not cn1 or not cn2:
                return 0.0
            return len(cn1 & cn2) / max(len(cn1), len(cn2))
        return len(words1 & words2) / max(len(words1), len(words2))

    def check_duplicate(self, title: str, description: str = '') -> list:
        results = []
        for d in self.data['demands']:
            title_sim = self._keyword_overlap(title, d.get('title', ''))
            desc_sim = self._keyword_overlap(description, d.get('description', ''))
            max_sim = max(title_sim, desc_sim)
            if max_sim >= 0.6:
                results.append({
                    'id': d['id'],
                    'title': d['title'],
                    'similarity': round(max_sim, 2),
                    'status': d.get('status', '')
                })
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results

    def add(self, title: str, demand_type: str = '', demand_module: str = '',
            background: str = '', pain_points: str = '', description: str = '',
            label: str = '', priority: str = '', ai_suggestions: str = '',
            submitter: str = '', grade: str = '', total_score: int = 0,
            status: str = '待评审') -> dict:
        if not title:
            title = description[:50] if description else '未命名需求'

        demand_id = self.data['next_id']
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        record = {
            'id': f'D{demand_id:03d}',
            'demand_type': demand_type,
            'demand_module': demand_module,
            'title': title,
            'background': background,
            'pain_points': pain_points,
            'description': description,
            'label': label,
            'priority': priority,
            'ai_suggestions': ai_suggestions,
            'submitter': submitter,
            'status': status,
            'grade': grade,
            'total_score': total_score,
            'change_history': [
                {'timestamp': now, 'action': '创建', 'detail': f'初始状态: {status}'}
            ],
            'created_at': now,
            'updated_at': now
        }
        self.data['demands'].append(record)
        self.data['next_id'] += 1
        self._save()
        return record

    def update(self, demand_id: str, **kwargs) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                changes = []
                for k, v in kwargs.items():
                    old_val = d.get(k)
                    if old_val != v:
                        changes.append(f"{k}: {old_val} → {v}")
                        d[k] = v
                if changes:
                    self._add_history(d, '更新', '; '.join(changes))
                d['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                self._save()
                return d
        return {}

    def transition_status(self, demand_id: str, new_status: str) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                current = d.get('status', '')
                allowed = VALID_TRANSITIONS.get(current, [])
                if new_status not in allowed:
                    return {
                        'error': f'状态流转不合法: {current} → {new_status}',
                        'allowed': allowed
                    }
                old_status = current
                d['status'] = new_status
                self._add_history(d, '状态变更', f'{old_status} → {new_status}')
                d['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                self._save()
                return d
        return {'error': f'需求 {demand_id} 不存在'}

    def list_all(self) -> list:
        return [d for d in self.data['demands']]

    def list_summary(self) -> list:
        return [{'id': d['id'], 'title': d['title'], 'status': d.get('status', '')} for d in self.data['demands']]

    def get(self, demand_id: str) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                return d
        return {}

    def search(self, keyword: str) -> list:
        kw = keyword.lower()
        return [d for d in self.data['demands']
                if kw in d['title'].lower()
                or kw in d.get('description', '').lower()
                or kw in d.get('background', '').lower()
                or kw in d.get('pain_points', '').lower()]

    def stats(self) -> dict:
        demands = self.data['demands']
        label_count = {}
        priority_count = {}
        module_count = {}
        status_count = {}
        for d in demands:
            lb = d.get('label', '未标注')
            pr = d.get('priority', '未标注')
            md = d.get('demand_module', '未分类')
            st = d.get('status', '未知')
            label_count[lb] = label_count.get(lb, 0) + 1
            priority_count[pr] = priority_count.get(pr, 0) + 1
            module_count[md] = module_count.get(md, 0) + 1
            status_count[st] = status_count.get(st, 0) + 1
        return {
            'total': len(demands),
            'labels': label_count,
            'priorities': priority_count,
            'modules': module_count,
            'statuses': status_count
        }


if __name__ == '__main__':
    lib = DemandLibrary()

    dupes = lib.check_duplicate('磐石系统侵权库重构', '侵权库自动化采集')
    print(f"去重检查: {dupes}")

    r = lib.transition_status('D001', '已立项')
    print(f"状态变更: {r}")

    d = lib.get('D001')
    print(f"变更历史: {d.get('change_history', [])}")
