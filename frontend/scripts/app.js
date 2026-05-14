const App = {
    currentSection: 'feed',
    currentFeedTab: 'all',

    init() {
        this.updateLastTime();
        this.renderStats();
        this.renderFeed();
        this.renderProducts();
        this.renderElements();
        this.renderTrends();
        this.renderAlerts();
        this.bindEvents();
    },

    updateLastTime() {
        const now = new Date();
        const timeStr = now.toLocaleString('zh-CN', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        document.getElementById('lastUpdateTime').textContent = timeStr;
    },

    renderStats() {
        const stats = MOCK_DATA.stats;
        document.getElementById('statHitCount').textContent = stats.hitCount;
        document.getElementById('statElementCount').textContent = stats.elementCount;
        document.getElementById('statTrendMatch').textContent = stats.trendMatch;
        document.getElementById('statMargin').textContent = stats.margin;
    },

    renderFeed() {
        const container = document.getElementById('feedStream');
        const items = MOCK_DATA.feedItems;
        container.innerHTML = items.map(item => Renderers.feedItem(item)).join('');
    },

    renderProducts() {
        const container = document.getElementById('productCards');
        const products = MOCK_DATA.hitProducts;
        container.innerHTML = products.map(p => Renderers.productCard(p)).join('');
    },

    renderElements() {
        const listContainer = document.getElementById('elementsList');
        const suggestionsContainer = document.getElementById('suggestionsGrid');
        listContainer.innerHTML = MOCK_DATA.topElements.map(e => Renderers.elementCard(e)).join('');
        suggestionsContainer.innerHTML = MOCK_DATA.visualSuggestions.map(s => Renderers.suggestionCard(s)).join('');
    },

    renderTrends() {
        const container = document.getElementById('trendsGrid');
        container.innerHTML = MOCK_DATA.trends.map(t => Renderers.trendCard(t)).join('');
    },

    renderAlerts() {
        const container = document.getElementById('alertsList');
        container.innerHTML = MOCK_DATA.alerts.map(a => Renderers.alertCard(a)).join('');
    },

    bindEvents() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        document.querySelectorAll('.feed-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.currentFeedTab = tab.dataset.tab;
                document.querySelectorAll('.feed-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.filterFeed();
            });
        });

        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });

        document.getElementById('modalClose').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('modalOverlay').addEventListener('click', (e) => {
            if (e.target === document.getElementById('modalOverlay')) {
                this.closeModal();
            }
        });

        const slider = document.getElementById('uniquenessSlider');
        const sliderValue = document.getElementById('uniquenessValue');
        slider.addEventListener('input', () => {
            sliderValue.textContent = parseFloat(slider.value).toFixed(2);
        });

        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('manualPushBtn').addEventListener('click', () => {
            this.triggerManualPush();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    },

    switchSection(section) {
        this.currentSection = section;

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelector(`.nav-item[data-section="${section}"]`).classList.add('active');

        const sections = ['contentFeed', 'productsGrid', 'elementsSection', 'trendsSection', 'alertsSection', 'settingsSection'];
        const sectionMap = {
            feed: 'contentFeed',
            products: 'productsGrid',
            elements: 'elementsSection',
            trends: 'trendsSection',
            alerts: 'alertsSection',
            settings: 'settingsSection'
        };

        sections.forEach(s => {
            const el = document.getElementById(s);
            if (el) el.style.display = 'none';
        });

        const targetId = sectionMap[section];
        const targetEl = document.getElementById(targetId);
        if (targetEl) targetEl.style.display = 'block';

        const titles = {
            feed: '每日信息流',
            products: '爆品推荐',
            elements: '爆品元素',
            trends: '趋势追踪',
            alerts: '避坑预警',
            settings: '推送设置'
        };

        const breadcrumbs = {
            feed: '信息流',
            products: '爆品推荐',
            elements: '爆品元素',
            trends: '趋势追踪',
            alerts: '避坑预警',
            settings: '推送设置'
        };

        document.getElementById('pageTitle').textContent = titles[section] || '';
        document.getElementById('breadcrumbCurrent').textContent = breadcrumbs[section] || '';
    },

    filterFeed() {
        const feedItems = document.querySelectorAll('.feed-item');
        feedItems.forEach(item => {
            if (this.currentFeedTab === 'all') {
                item.style.display = 'flex';
            } else if (this.currentFeedTab === 'trends') {
                item.style.display = item.dataset.type === 'trend' ? 'flex' : 'none';
            } else if (this.currentFeedTab === 'alerts') {
                item.style.display = item.dataset.type === 'alert' ? 'flex' : 'none';
            } else if (this.currentFeedTab === 'supply') {
                item.style.display = item.dataset.type === 'supply' ? 'flex' : 'none';
            }
        });
    },

    refreshData() {
        const btn = document.getElementById('refreshBtn');
        btn.style.opacity = '0.6';
        btn.style.pointerEvents = 'none';

        setTimeout(() => {
            this.updateLastTime();
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        }, 1200);
    },

    openProductModal(productId) {
        const product = MOCK_DATA.hitProducts.find(p => p.id === productId);
        if (!product) return;

        const modal = document.getElementById('modalOverlay');
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');

        title.textContent = '商品详情';
        body.innerHTML = `
            <div class="modal-product-title">${product.title}</div>
            <div class="modal-product-url">${product.url}</div>
            <div class="modal-field">
                <div class="modal-field-label">定价</div>
                <div class="modal-field-value mono">${product.price}</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">品类</div>
                <div class="modal-field-value">${product.category}</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">综合得分</div>
                <div class="modal-field-value mono">${product.score} / 100</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">核心特征</div>
                <div class="modal-field-value">
                    <div class="feed-tags" style="margin-top:4px;">
                        ${product.features.map(f => `<span class="feed-tag fit">${f}</span>`).join('')}
                    </div>
                </div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">核心卖点</div>
                <div class="modal-field-value">
                    <ul style="list-style:none;padding:0;">
                        ${product.sellingPoints.map(sp => `<li style="padding:4px 0;padding-left:16px;position:relative;">
                            <span style="position:absolute;left:0;color:var(--accent-primary);">&#8226;</span>${sp}
                        </li>`).join('')}
                    </ul>
                </div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">趋势匹配元素</div>
                <div class="modal-field-value">
                    <div class="feed-tags" style="margin-top:4px;">
                        ${product.trendMatch.map(tm => `<span class="feed-tag material">${tm}</span>`).join('')}
                    </div>
                </div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">预期毛利</div>
                <div class="modal-field-value mono" style="color:${product.margin >= 30 ? 'var(--accent-success)' : 'var(--accent-danger)'};">
                    ${product.margin}% ${product.margin < 30 ? '(低毛利预警)' : ''}
                </div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">独特性系数</div>
                <div class="modal-field-value mono">${product.uniqueness.toFixed(2)}</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">评论状态</div>
                <div class="modal-field-value">${product.reviewStatus}</div>
            </div>
        `;

        modal.classList.add('active');
    },

    closeModal() {
        document.getElementById('modalOverlay').classList.remove('active');
    },

    saveSettings() {
        const categories = Array.from(document.querySelectorAll('#categoryCheckboxes input:checked')).map(cb => cb.value);
        const frequency = document.getElementById('pushFrequency').value;
        const channels = Array.from(document.querySelectorAll('#channelCheckboxes input:checked')).map(cb => cb.value);
        const uniquenessThreshold = parseFloat(document.getElementById('uniquenessSlider').value);

        const btn = document.getElementById('saveSettingsBtn');
        const originalText = btn.textContent;
        btn.textContent = '已保存';
        btn.style.background = 'var(--accent-success)';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    },

    triggerManualPush() {
        const btn = document.getElementById('manualPushBtn');
        const originalText = btn.textContent;
        btn.textContent = '推送中...';
        btn.style.pointerEvents = 'none';
        setTimeout(() => {
            btn.textContent = '推送成功';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.pointerEvents = 'auto';
            }, 1500);
        }, 1000);
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
