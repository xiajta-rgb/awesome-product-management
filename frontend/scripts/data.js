const AppData = {
    rawData: null,
    feedItems: [],
    hitProducts: [],
    topElements: [],
    visualSuggestions: [],
    trends: [],
    alerts: [],
    stats: {}
};

async function loadSkillData() {
    try {
        const response = await fetch('/api/skill-result');
        if (!response.ok) throw new Error('Failed to load skill result');
        AppData.rawData = await response.json();
        transformSkillData(AppData.rawData);
        return true;
    } catch (error) {
        console.warn('Failed to load skill result, using demo mode:', error.message);
        AppData.rawData = null;
        generateDemoData();
        return false;
    }
}

function transformSkillData(data) {
    const now = new Date(data.run_time || Date.now()).toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });

    AppData.feedItems = [];

    const hitProducts = data.hit_products?.products || [];
    hitProducts.forEach((p, i) => {
        AppData.feedItems.push({
            type: 'hit',
            icon: 'hit',
            title: `爆品推荐: ${p.title}`,
            sourceTag: p.data_source || 'amazon',
            desc: `综合得分${p.score || '--'}，${p.review_status || ''}，${p.margin_alert || ''}。核心特征：${Array.isArray(p.features) ? p.features.join('、') : ''}`,
            tags: Array.isArray(p.features) ? p.features.map(f => ({ text: f, type: 'material' })) : [],
            meta: `得分: ${p.score || '--'} | 毛利: ${p.expected_margin ? (p.expected_margin * 100).toFixed(0) + '%' : '--'} | 独特性: ${p.uniqueness_coefficient?.toFixed(2) || '--'}`,
            time: now,
            _raw: p
        });
    });

    const potentialProducts = data.potential_products?.products || [];
    potentialProducts.forEach((p, i) => {
        AppData.feedItems.push({
            type: 'hit',
            icon: 'hit',
            title: `潜力品推荐: ${p.title}`,
            sourceTag: p.data_source || 'amazon',
            desc: `${p.growth_potential || ''}。核心特征：${Array.isArray(p.features) ? p.features.join('、') : ''}`,
            tags: Array.isArray(p.features) ? p.features.map(f => ({ text: f, type: 'material' })) : [],
            meta: `毛利: ${p.expected_margin ? (p.expected_margin * 100).toFixed(0) + '%' : '--'} | 供应链: ${p.supply_chain_feasibility || '待评估'}`,
            time: now,
            _raw: p
        });
    });

    const visualSuggestions = data.visual_diff_suggestions?.suggestions || [];
    visualSuggestions.forEach((s, i) => {
        AppData.feedItems.push({
            type: 'trend',
            icon: 'trend',
            title: `视觉差异化: ${s.element}`,
            sourceTag: s.data_source || 'system',
            desc: s.description || '',
            tags: [{ text: s.element, type: 'design' }, { text: s.suggestion_type, type: 'material' }],
            meta: `类型: ${s.suggestion_type}`,
            time: now,
            _raw: s
        });
    });

    const pitfalls = data.pitfall_warnings?.pitfalls || [];
    pitfalls.forEach((p, i) => {
        AppData.feedItems.push({
            type: 'alert',
            icon: 'alert',
            title: `避坑预警: ${p.title}`,
            sourceTag: p.data_source || 'amazon_reviews',
            desc: p.description || '',
            tags: p.pain_points?.map(pp => ({ text: pp, type: 'design' })) || [],
            meta: `痛点: ${p.pain_points?.join(' | ') || ''}`,
            time: now,
            _raw: p
        });
    });

    const uniquenessRecs = data.uniqueness_recommendations?.recommendations || [];
    uniquenessRecs.forEach((r, i) => {
        AppData.feedItems.push({
            type: 'trend',
            icon: 'trend',
            title: `独特性推荐: ${r.title || '产品'}`,
            sourceTag: 'uniqueness',
            desc: `独特性系数: ${r.uniqueness_coefficient?.toFixed(2) || '--'}，${r.combination_suggestion || ''}`,
            tags: [{ text: `独特性: ${(r.uniqueness_coefficient || 0).toFixed(2)}`, type: 'score' }],
            meta: `系数: ${r.uniqueness_coefficient?.toFixed(2) || '--'}`,
            time: now,
            _raw: r
        });
    });

    AppData.hitProducts = [...hitProducts, ...potentialProducts].map((p, i) => ({
        id: i + 1,
        title: p.title || '',
        url: p.url || '#',
        price: p.price ? `$${p.price}` : '--',
        features: Array.isArray(p.features) ? p.features : [],
        category: p.data_source || '',
        score: p.score || 0,
        margin: p.expected_margin ? (p.expected_margin * 100) : 0,
        uniqueness: p.uniqueness_coefficient || 0,
        reviewStatus: p.review_status || '',
        warning: p.margin_alert || null,
        sellingPoints: p.selling_points || [],
        trendMatch: p.trend_match_points || []
    }));

    const elements = data.top10_elements?.elements || [];
    AppData.topElements = elements.map((e, i) => ({
        rank: i + 1,
        name: e.element || '',
        standard: e.element || '',
        desc: `${e.frequency}次出现，${e.is_core ? '核心元素' : '辅助元素'}，毛利系数${(e.margin * 100).toFixed(0)}%`,
        freq: e.frequency || 0,
        scene: e.is_core ? '核心爆品元素' : '辅助元素',
        category: e.element || '',
        source: 'system_analysis'
    }));

    AppData.visualSuggestions = visualSuggestions.map(s => ({
        category: s.element || '',
        title: s.suggestion_type || '',
        desc: s.description || ''
    }));

    AppData.trends = visualSuggestions.map(s => ({
        title: `差异化建议: ${s.element}`,
        source: s.data_source || 'system',
        heat: s.suggestion_type === 'visual_gap' ? 'high' : 'medium',
        desc: s.description || '',
        tags: [{ text: s.element, type: 'design' }]
    }));

    AppData.alerts = pitfalls.map(p => ({
        severity: 'warning',
        title: p.title || '',
        desc: p.description || '',
        source: p.data_source || 'system',
        painPoints: p.pain_points || []
    }));

    const stats = data.data_statistics || {};
    AppData.stats = {
        hitCount: hitProducts.length,
        elementCount: elements.length,
        trendMatch: hitProducts.length > 0 ? `${(hitProducts.filter(p => p.score >= 80).length / hitProducts.length * 100).toFixed(0)}%` : '--',
        margin: hitProducts.length > 0 ? `${(hitProducts.reduce((sum, p) => sum + (p.expected_margin || 0), 0) / hitProducts.length * 100).toFixed(0)}%` : '--'
    };
}

function generateDemoData() {
    const now = new Date().toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });

    AppData.feedItems = [
        {
            type: 'hit', icon: 'hit',
            title: '爆品推荐: 男士商务休闲棉麻衬衫',
            sourceTag: 'amazon',
            desc: '综合得分99.57，好评率92%。核心特征：修身、棉麻混纺、大地色',
            tags: [{ text: '修身', type: 'fit' }, { text: '棉麻混纺', type: 'material' }, { text: '大地色', type: 'color' }],
            meta: '得分: 99.57 | 毛利: 40% | 独特性: 1.00', time: now,
            _raw: { title: '男士商务休闲棉麻衬衫', score: 99.57 }
        },
        {
            type: 'trend', icon: 'trend',
            title: '视觉差异化: Earth Tone',
            sourceTag: 'system',
            desc: '站内爆品独有元素 "Earth Tone"，可作为视觉差异化亮点',
            tags: [{ text: 'Earth Tone', type: 'design' }, { text: 'visual_differentiation', type: 'material' }],
            meta: '类型: visual_differentiation', time: now, _raw: {}
        },
        {
            type: 'trend', icon: 'trend',
            title: '视觉差异化: Slim Fit',
            sourceTag: 'system',
            desc: '站内爆品独有元素 "Slim Fit"，可作为视觉差异化亮点',
            tags: [{ text: 'Slim Fit', type: 'design' }, { text: 'visual_differentiation', type: 'material' }],
            meta: '类型: visual_differentiation', time: now, _raw: {}
        },
        {
            type: 'trend', icon: 'trend',
            title: '视觉差异化: Cotton Linen Blend',
            sourceTag: 'system',
            desc: '站内爆品独有元素 "Cotton Linen Blend"，可作为视觉差异化亮点',
            tags: [{ text: 'Cotton Linen Blend', type: 'design' }, { text: 'visual_differentiation', type: 'material' }],
            meta: '类型: visual_differentiation', time: now, _raw: {}
        }
    ];

    AppData.hitProducts = [
        {
            id: 1, title: '男士商务休闲棉麻衬衫 — 修身款',
            url: 'https://amazon.com/dp/B08XYZ1234', price: '$29.99',
            features: ['修身', '棉麻混纺', '大地色'], category: '男装商务休闲',
            score: 99.57, margin: 40, uniqueness: 1.00, reviewStatus: '有有效评论',
            warning: null, sellingPoints: ['大地色低饱和色系，适配商务通勤', '棉麻混纺透气舒适，适合春夏季节'],
            trendMatch: ['Earth Tone', 'Cotton Linen Blend', 'Slim Fit']
        }
    ];

    AppData.topElements = [];
    AppData.visualSuggestions = [
        { category: 'Earth Tone', title: 'visual_differentiation', desc: '站内爆品独有元素 "Earth Tone"，可作为视觉差异化亮点' },
        { category: 'Slim Fit', title: 'visual_differentiation', desc: '站内爆品独有元素 "Slim Fit"，可作为视觉差异化亮点' },
        { category: 'Cotton Linen Blend', title: 'visual_differentiation', desc: '站内爆品独有元素 "Cotton Linen Blend"，可作为视觉差异化亮点' }
    ];
    AppData.trends = AppData.visualSuggestions.map(s => ({
        title: `差异化建议: ${s.category}`, source: 'system',
        heat: 'medium', desc: s.desc, tags: [{ text: s.category, type: 'design' }]
    }));
    AppData.alerts = [];
    AppData.stats = { hitCount: 1, elementCount: 0, trendMatch: '100%', margin: '40%' };
}
