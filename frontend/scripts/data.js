const MOCK_DATA = {
    feedItems: [
        {
            type: 'hit',
            icon: 'hit',
            title: '新品爆品推荐: 男士商务休闲棉麻衬衫',
            sourceTag: 'amazon_bestseller',
            desc: '月销1280单，趋势匹配度92%，综合得分86分。核心卖点：Earth Tone色系 + Cotton Linen Blend材质 + Slim Fit版型，适配25+商务通勤场景。',
            tags: [
                { text: 'Earth Tone', type: 'color' },
                { text: 'Cotton Linen Blend', type: 'material' },
                { text: 'Slim Fit', type: 'fit' },
                { text: 'Score: 86', type: 'score' }
            ],
            meta: '销量: 1280 | 匹配度: 92% | 毛利: 42%',
            time: '2026-05-14 08:00'
        },
        {
            type: 'trend',
            icon: 'trend',
            title: '站外趋势: 纹理感面料搜索量上涨20%',
            sourceTag: 'google_trends',
            desc: '当前站内商务衬衫多为平纹面料，但TikTok和Pinterest趋势显示纹理感面料（如泡泡纱、华夫格）搜索热度显著上升，建议改版方向。',
            tags: [
                { text: 'Texture Fabric', type: 'material' },
                { text: 'Business Casual', type: 'design' }
            ],
            meta: '趋势: 短期 | 热度: 高',
            time: '2026-05-14 07:30'
        },
        {
            type: 'alert',
            icon: 'alert',
            title: '避坑预警: 某聚酯纤维材质易掉色',
            sourceTag: 'amazon_reviews',
            desc: '基于352条可靠评论数据，发现某类聚酯纤维工装裤"Color Fading"差评率高达18%，建议规避该材质供应商。',
            tags: [
                { text: 'Color Fading', type: 'design' },
                { text: 'Workwear Outdoor', type: 'fit' }
            ],
            meta: '差评率: 18% | 评论数: 352',
            time: '2026-05-14 06:00'
        },
        {
            type: 'supply',
            icon: 'supply',
            title: '供应链预警: 帆布面料成本上涨8%',
            sourceTag: '3-grid',
            desc: '近两周帆布面料3-grid报价上涨约8%，MOQ从500件提至800件。工装登山类商品需关注毛利变化，低于30%将触发低毛利预警。',
            tags: [
                { text: 'Canvas', type: 'material' },
                { text: '成本预警', type: 'design' }
            ],
            meta: '涨幅: +8% | MOQ: 800件',
            time: '2026-05-14 05:00'
        },
        {
            type: 'hit',
            icon: 'hit',
            title: '潜力爆品: 女士休闲运动速干Leggings',
            sourceTag: 'amazon_trending',
            desc: '月销680单，趋势匹配度88%，综合得分76分。Fresh Contrast配色 + Quick Dry面料 + Oversized腰部设计，成长空间大。',
            tags: [
                { text: 'Quick Dry', type: 'material' },
                { text: 'Fresh Contrast', type: 'color' },
                { text: 'Oversized', type: 'fit' },
                { text: 'Score: 76', type: 'score' }
            ],
            meta: '销量: 680 | 匹配度: 88% | 毛利: 38%',
            time: '2026-05-13 22:00'
        },
        {
            type: 'trend',
            icon: 'trend',
            title: '季节性趋势: 夏季透气速干面料热度上升',
            sourceTag: 'wgsn',
            desc: 'WGSN夏季趋势报告显示，透气速干面料在休闲运动品类中搜索量环比增长35%，预计6-8月为爆发期。',
            tags: [
                { text: 'Breathable Mesh', type: 'material' },
                { text: 'Casual Sport', type: 'design' }
            ],
            meta: '周期: 中期 | 热度: 高 | 增幅: +35%',
            time: '2026-05-13 18:00'
        },
        {
            type: 'alert',
            icon: 'alert',
            title: '合规预警: 无尺码标注商品被严查',
            sourceTag: 'amazon_policy',
            desc: '亚马逊近期加强服装类目合规审查，无尺码标注商品面临下架风险。请确保所有上架商品均包含完整尺码信息。',
            tags: [
                { text: '合规风险', type: 'design' },
                { text: '全品类', type: 'fit' }
            ],
            meta: '风险等级: 高 | 影响范围: 全品类',
            time: '2026-05-13 14:00'
        },
        {
            type: 'hit',
            icon: 'hit',
            title: '新品爆品: 男士工装登山多口袋防水裤',
            sourceTag: 'amazon_bestseller',
            desc: '月销1520单，趋势匹配度95%，综合得分91分。Army Green色系 + Waterproof Coating面料 + Multi Pocket设计 + Reinforced Stitching工艺。',
            tags: [
                { text: 'Waterproof Coating', type: 'material' },
                { text: 'Multi Pocket', type: 'design' },
                { text: 'Army Green', type: 'color' },
                { text: 'Score: 91', type: 'score' }
            ],
            meta: '销量: 1520 | 匹配度: 95% | 毛利: 45%',
            time: '2026-05-13 10:00'
        }
    ],

    hitProducts: [
        {
            id: 1,
            title: '男士商务休闲棉麻衬衫 — 修身简约款',
            url: 'https://www.amazon.com/dp/example1',
            price: '$34.99',
            features: ['Slim Fit', 'Cotton Linen Blend', 'Minimal Embroidery'],
            category: '男装商务休闲',
            score: 86,
            margin: 42,
            uniqueness: 0.82,
            reviewStatus: '好评率 94%',
            warning: null,
            sellingPoints: ['Earth Tone低饱和色系，适配商务通勤', '棉麻混纺透气舒适，适合春夏季节'],
            trendMatch: ['Earth Tone', 'Cotton Linen Blend', 'Slim Fit']
        },
        {
            id: 2,
            title: '女士休闲运动速干Leggings — 撞色高腰款',
            url: 'https://www.amazon.com/dp/example2',
            price: '$28.99',
            features: ['Oversized', 'Quick Dry', 'Fresh Contrast'],
            category: '女装休闲运动',
            score: 76,
            margin: 38,
            uniqueness: 0.75,
            reviewStatus: '好评率 91%',
            warning: null,
            sellingPoints: ['速干面料运动后快速排汗', '高腰设计修饰腰线'],
            trendMatch: ['Quick Dry', 'Fresh Contrast']
        },
        {
            id: 3,
            title: '男士工装登山多口袋防水裤 — 加固缝线版',
            url: 'https://www.amazon.com/dp/example3',
            price: '$52.99',
            features: ['Loose Fit', 'Waterproof Coating', 'Multi Pocket', 'Reinforced Stitching'],
            category: '男装工装登山',
            score: 91,
            margin: 45,
            uniqueness: 0.88,
            reviewStatus: '好评率 96%',
            warning: null,
            sellingPoints: ['防水涂层面料应对户外恶劣环境', '多口袋设计增强实用收纳', '加固缝线提升耐用性'],
            trendMatch: ['Waterproof Coating', 'Multi Pocket', 'Army Green', 'Reinforced Stitching']
        },
        {
            id: 4,
            title: '女士商务休闲西装套 — 蓝灰色修身款',
            url: 'https://www.amazon.com/dp/example4',
            price: '$68.99',
            features: ['Slim Fit', 'Silk Blend', 'Blue Gray'],
            category: '女装商务休闲',
            score: 82,
            margin: 28,
            uniqueness: 0.79,
            reviewStatus: '无有效评论',
            warning: '低毛利预警',
            sellingPoints: ['蓝灰色商务通勤百搭', '真丝混纺质感高级'],
            trendMatch: ['Blue Gray', 'Slim Fit']
        },
        {
            id: 5,
            title: '男士休闲运动透气卫衣 — 机能拉链设计',
            url: 'https://www.amazon.com/dp/example5',
            price: '$42.99',
            features: ['Loose Fit', 'Breathable Mesh', 'Functional Zipper'],
            category: '男装休闲运动',
            score: 78,
            margin: 35,
            uniqueness: 0.71,
            reviewStatus: '好评率 89%',
            warning: null,
            sellingPoints: ['透气网布面料夏季友好', '机能拉链设计时尚实用'],
            trendMatch: ['Breathable Mesh', 'Functional Zipper', 'Loose Fit']
        },
        {
            id: 6,
            title: '女士工装登山户外外套 — 多口袋防水款',
            url: 'https://www.amazon.com/dp/example6',
            price: '$78.99',
            features: ['Adjustable Design', 'Waterproof Coating', 'Multi Pocket'],
            category: '女装工装登山',
            score: 84,
            margin: 40,
            uniqueness: 0.85,
            reviewStatus: '好评率 93%',
            warning: null,
            sellingPoints: ['多调节设计适配不同体型', '防水涂层应对多变天气'],
            trendMatch: ['Waterproof Coating', 'Multi Pocket', 'Adjustable Design']
        }
    ],

    topElements: [
        { rank: 1, name: 'Earth Tone', standard: 'Earth Tone', desc: '低饱和大地色系（卡其、燕麦、驼色），商务休闲品类核心趋势', freq: 48, scene: '商务通勤、日常休闲', category: '商务休闲', source: 'WGSN + Pinterest' },
        { rank: 2, name: '多口袋设计', standard: 'Multi Pocket', desc: '工装登山品类标志性设计元素，功能性优先', freq: 42, scene: '户外登山、工装场景', category: '工装登山', source: 'amazon_bestseller' },
        { rank: 3, name: '防水涂层', standard: 'Waterproof Coating', desc: '应对多变天气的核心面料处理技术', freq: 38, scene: '户外场景、雨季', category: '工装登山', source: 'WGSN' },
        { rank: 4, name: '速干面料', standard: 'Quick Dry', desc: '运动后排汗快干，休闲运动品类核心材质', freq: 35, scene: '运动健身、日常休闲', category: '休闲运动', source: 'google_trends' },
        { rank: 5, name: '修身版型', standard: 'Slim Fit', desc: '商务休闲品类主流版型，简洁利落', freq: 33, scene: '商务通勤、职场', category: '商务休闲', source: 'amazon_trending' },
        { rank: 6, name: '机能拉链', standard: 'Functional Zipper', desc: '兼具装饰与功能的拉链设计，运动品类流行元素', freq: 29, scene: '运动休闲、户外', category: '休闲运动', source: 'TikTok' },
        { rank: 7, name: '透气网布', standard: 'Breathable Mesh', desc: '夏季运动面料首选，透气性优先', freq: 27, scene: '夏季运动、健身', category: '休闲运动', source: 'WGSN' },
        { rank: 8, name: '加固缝线', standard: 'Reinforced Stitching', desc: '提升耐用性的工艺细节，工装品类标配', freq: 25, scene: '工装场景、户外', category: '工装登山', source: 'amazon_bestseller' },
        { rank: 9, name: '棉麻混纺', standard: 'Cotton Linen Blend', desc: '春夏季节商务休闲材质首选', freq: 23, scene: '春夏商务、日常', category: '商务休闲', source: 'Pinterest' },
        { rank: 10, name: '宽松版型', standard: 'Loose Fit', desc: '休闲运动品类主流版型，舒适自由', freq: 21, scene: '日常休闲、运动', category: '休闲运动', source: 'TikTok' }
    ],

    visualSuggestions: [
        {
            category: '商务休闲衬衫',
            title: '面料纹理升级建议',
            desc: '当前站内爆品多为平纹面料，但TikTok趋势显示纹理感面料（泡泡纱、华夫格）搜索量上涨20%。建议改版为泡泡纱材质衬衫，保留Earth Tone色系但增加面料层次。'
        },
        {
            category: '工装登山裤',
            title: '色彩差异化建议',
            desc: '站内工装裤以军绿色为主（占比78%），但站外趋势显示Navy Blue和Blue Gray在工装场景搜索量上升15%。建议增加Navy Blue配色工装裤，形成差异化。'
        },
        {
            category: '休闲运动卫衣',
            title: '版型微调建议',
            desc: '当前宽松版型占主导，但Instagram上"Structured Oversize"（结构化宽松）趋势上升。建议在保持宽松的基础上增加肩部结构设计，提升高级感。'
        }
    ],

    trends: [
        {
            title: '纹理感面料热度上升',
            source: 'google_trends',
            heat: 'high',
            desc: '泡泡纱、华夫格等纹理面料搜索量环比增长20%，商务休闲品类潜在改版方向。',
            tags: [{ text: 'Texture Fabric', type: 'material' }, { text: 'Business Casual', type: 'design' }]
        },
        {
            title: '低饱和色系持续流行',
            source: 'wgsn',
            heat: 'high',
            desc: 'Earth Tone色系在商务休闲品类中持续主导，WGSN预测未来6个月仍为趋势核心。',
            tags: [{ text: 'Earth Tone', type: 'color' }, { text: '中期趋势', type: 'design' }]
        },
        {
            title: '防水面料季节性增长',
            source: 'pinterest',
            heat: 'medium',
            desc: '雨季来临，防水涂层面料在工装登山品类搜索量增长30%。',
            tags: [{ text: 'Waterproof Coating', type: 'material' }, { text: '季节性', type: 'design' }]
        },
        {
            title: '反光条设计潮流回归',
            source: 'tiktok',
            heat: 'medium',
            desc: 'TikTok上反光条穿搭视频播放量突破500万，休闲运动品类可关注。',
            tags: [{ text: 'Reflective Strip', type: 'design' }, { text: 'Casual Sport', type: 'design' }]
        },
        {
            title: '可持续面料长期趋势',
            source: 'statista',
            heat: 'medium',
            desc: 'Statista报告显示可持续面料在服装品类年增长率达22%，长期趋势值得关注。',
            tags: [{ text: 'Sustainable', type: 'material' }, { text: '长期趋势', type: 'design' }]
        },
        {
            title: '蓝灰色商务趋势',
            source: 'instagram',
            heat: 'high',
            desc: 'Instagram上Blue Gray商务穿搭话题热度上升18%，女装商务休闲品类新方向。',
            tags: [{ text: 'Blue Gray', type: 'color' }, { text: 'Womenswear', type: 'design' }]
        }
    ],

    alerts: [
        {
            severity: 'critical',
            title: '聚酯纤维材质掉色问题',
            desc: '基于352条可靠评论，某类聚酯纤维工装裤"Color Fading"差评率达18%。建议规避该材质供应商或改进染色工艺。',
            source: 'amazon_reviews',
            painPoints: ['Color Fading (18%)', 'Rough Material (12%)']
        },
        {
            severity: 'critical',
            title: '尺码偏小投诉集中',
            desc: '商务休闲衬衫品类中"Size Too Small"差评率环比增长5%，建议在尺码表中增加详细测量数据。',
            source: 'amazon_reviews',
            painPoints: ['Size Too Small (+5%)', 'Length Issue (8%)']
        },
        {
            severity: 'warning',
            title: '起球问题频发',
            desc: '休闲运动卫衣品类"Pilling"差评率达14%，主要集中在低价位（<$25）产品。建议优化面料品质。',
            source: 'amazon_reviews',
            painPoints: ['Pilling (14%)', 'Color Fading (6%)']
        }
    ],

    stats: {
        hitCount: 12,
        elementCount: 10,
        trendMatch: '87%',
        margin: '38%'
    }
};
