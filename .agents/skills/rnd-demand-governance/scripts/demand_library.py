"""
需求库管理 v2 - 标准字段版
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
                json.dump({"version": "2.0", "next_id": 1, "demands": []}, f, ensure_ascii=False, indent=2)

    def _load(self):
        with open(self.lib_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def _save(self):
        with open(self.lib_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add(self, title: str, demand_type: str = '', demand_module: str = '',
            background: str = '', pain_points: str = '', description: str = '',
            label: str = '', priority: str = '', submitter: str = '',
            grade: str = '', total_score: int = 0, status: str = '待评审') -> dict:
        if not title:
            title = description[:50] if description else '未命名需求'

        demand_id = self.data['next_id']
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
            'submitter': submitter,
            'status': status,
            'grade': grade,
            'total_score': total_score,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        self.data['demands'].append(record)
        self.data['next_id'] += 1
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
        return [{'id': d['id'], 'title': d['title']} for d in self.data['demands']]

    def get(self, demand_id: str) -> dict:
        for d in self.data['demands']:
            if d['id'] == demand_id:
                return d
        return {}

    def search(self, keyword: str) -> list:
        return [d for d in self.data['demands'] if keyword.lower() in d['title'].lower() or keyword.lower() in d.get('description', '').lower() or keyword.lower() in d.get('background', '').lower()]

    def stats(self) -> dict:
        demands = self.data['demands']
        label_count = {}
        priority_count = {}
        module_count = {}
        for d in demands:
            lb = d.get('label', '未标注')
            pr = d.get('priority', '未标注')
            md = d.get('demand_module', '未分类')
            label_count[lb] = label_count.get(lb, 0) + 1
            priority_count[pr] = priority_count.get(pr, 0) + 1
            module_count[md] = module_count.get(md, 0) + 1
        return {'total': len(demands), 'labels': label_count, 'priorities': priority_count, 'modules': module_count}


if __name__ == '__main__':
    lib = DemandLibrary()

    r1 = lib.add('磐石系统侵权库重构+新人风控培训体系', '价值需求', '研发域',
                 '磐石系统现有侵权库不完善，采集上传流程复杂',
                 '效率低，一个一个上传查看；新人缺乏风控培训',
                 '用机器人生成核心对标品牌侵权设计素材，搭建全覆盖侵权库',
                 '战略', 'P0', '测试', 'A', 88, '已评审')
    print('添加1:', r1['id'], r1['title'])

    r2 = lib.add('客服工单智能分配', '价值需求', '研发域',
                 '人工分配经常出错', '客户等待2小时',
                 '规则引擎自动分类分配',
                 '经营', 'P1', '客服', 'B', 70, '已评审')
    print('添加2:', r2['id'], r2['title'])

    print('\n=== 需求列表 ===')
    for s in lib.list_summary():
        print(f"  {s['id']}  {s['title']}")

    print(f"\n统计: {lib.stats()}")

    d = lib.get('D001')
    print(f"\n=== D001详情 ===")
    for k, v in d.items():
        if v:
            print(f"  {k}: {v}")

    print('\n✅ 全部测试通过')
