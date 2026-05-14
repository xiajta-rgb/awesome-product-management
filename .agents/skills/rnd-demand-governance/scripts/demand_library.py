"""
需求库管理 v1
记录、查询、管理所有提交过的需求
"""

import json
import os
from datetime import datetime


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
                json.dump({"version": "1.0", "total_count": 0, "next_id": 1, "demands": []}, f, ensure_ascii=False, indent=2)

    def _load(self):
        with open(self.lib_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add(self, demand_name: str, raw_description: str = '', submitter: str = '', grade: str = '', total_score: int = 0, status: str = '待评审') -> dict:
        if not demand_name:
            demand_name = raw_description[:50] if raw_description else '未命名需求'

        demand_id = self.data['next_id']
        record = {
            'id': f'D{demand_id:03d}',
            'demand_name': demand_name,
            'raw_description': raw_description,
            'submitter': submitter,
            'status': status,
            'grade': grade,
            'total_score': total_score,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.data['demands'].append(record)
        self.data['next_id'] += 1
        self.data['total_count'] = len(self.data['demands'])
        self._save()
        return record

    def update(self, demand_id: str, **kwargs) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                d.update(kwargs)
                d['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                self._save()
                return d
        return {}

    def list_all(self) -> list:
        return [d for d in self.data['demands']]

    def list_summary(self) -> list:
        return [{'id': d['id'], 'demand_name': d['demand_name']} for d in self.data['demands']]

    def get(self, demand_id: str) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                return d
        return {}

    def search(self, keyword: str) -> list:
        return [d for d in self.data['demands'] if keyword.lower() in d['demand_name'].lower() or keyword.lower() in d.get('raw_description', '').lower()]

    def stats(self) -> dict:
        demands = self.data['demands']
        grade_count = {}
        status_count = {}
        for d in demands:
            g = d.get('grade', '未评审')
            s = d.get('status', '未知')
            grade_count[g] = grade_count.get(g, 0) + 1
            status_count[s] = status_count.get(s, 0) + 1
        return {'total': len(demands), 'grades': grade_count, 'statuses': status_count}


if __name__ == '__main__':
    lib = DemandLibrary()

    # 添加测试需求
    r1 = lib.add('亚马逊侵权专利库自动化采集系统', '自动化采集脚本提升效率和避免侵权', '研发-张三', 'A', 85, '已评审')
    r2 = lib.add('数据安全合规平台', '6月底前完成数据出境安全评估', '法务-李四', 'A', 86, '已评审')
    r3 = lib.add('客服工单智能分配', '工单自动分类分配缩短等待时间', '客服-王五', 'B', 70, '已评审')

    print('=== 需求列表 ===')
    for s in lib.list_summary():
        print(f"  {s['id']}  {s['demand_name']}")

    print(f"\n统计: {lib.stats()}")
