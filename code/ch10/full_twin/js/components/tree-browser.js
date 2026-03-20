class TreeBrowser {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = { expandOnSelect: true, showIcons: true, ...options };
        this.assetData = null;
        this.selectedAssetId = null;
        this.expandedNodes = new Set();
        this.eventListeners = {};
        this.init();
    }

    init() {
        if (!this.container) return;
        this.container.addEventListener('click', (event) => {
            const nodeElement = event.target.closest('.tree-node');
            if (!nodeElement) return;
            const assetId = nodeElement.dataset.assetId;
            if (event.target.closest('.tree-toggle')) {
                this.toggleNode(assetId);
            } else if (event.target.closest('.tree-label')) {
                this.selectAsset(assetId);
            }
        });
        this.showLoading();
    }

    async loadAssetHierarchy() {
        try {
            this.showLoading();
            const client = window.graphqlClient;
            const data = await client.getAssetHierarchy();
            if (data && data.assetHierarchy) {
                this.assetData = this.transformApiData(data.assetHierarchy);
                this.renderTree();
                this.emit('tree-loaded', { data: this.assetData });
            } else {
                throw new Error('No asset hierarchy data received');
            }
        } catch (error) {
            console.error('Failed to load asset hierarchy:', error);
            this.showError('Failed to load asset hierarchy. Please try again.');
            this.emit('tree-error', { error });
        }
    }

    transformApiData(apiData, parentId = null) {
        const transformNode = (node, parentId = null) => {
            const transformed = {
                id: node.name,
                name: node.name,
                type: this.inferNodeType(node.name),
                parentId,
                children: [],
                metadata: { originalName: node.name, label: node.label }
            };
            if (node.children && Array.isArray(node.children)) {
                transformed.children = node.children.map(child => transformNode(child, transformed.id));
            }
            return transformed;
        };
        return transformNode(apiData, parentId);
    }

    inferNodeType(name) {
        const n = name.toLowerCase();
        if (n.includes('building') || n.includes('house')) return 'building';
        if (n.includes('garage') || n.includes('pool') || n.includes('land') || n.includes('terrace')) return 'facility';
        if (n.includes('tank')) return 'equipment';
        if (n.includes('space') || n.includes('room')) return 'room';
        return 'default';
    }

    renderTree() {
        if (!this.assetData) return;
        this.container.innerHTML = '';
        const wrapper = document.createElement('div');
        wrapper.className = 'tree-wrapper';
        const roots = Array.isArray(this.assetData) ? this.assetData : [this.assetData];
        roots.forEach(asset => wrapper.appendChild(this.createTreeNode(asset, 0)));
        this.container.appendChild(wrapper);
        this.restoreExpandedState();
    }

    createTreeNode(asset, level = 0) {
        const nodeWrapper = document.createElement('div');
        nodeWrapper.className = 'tree-node-wrapper';

        const node = document.createElement('div');
        node.className = 'tree-node';
        node.dataset.assetId = asset.id;
        node.dataset.level = level;
        node.setAttribute('tabindex', '0');

        const hasChildren = asset.children && asset.children.length > 0;
        if (hasChildren) node.setAttribute('aria-expanded', 'false');

        const content = document.createElement('div');
        content.className = 'tree-node-content';
        content.style.paddingLeft = `${level * 20 + 8}px`;

        if (hasChildren) {
            const toggle = document.createElement('button');
            toggle.className = 'tree-toggle';
            toggle.innerHTML = '<svg viewBox="0 0 10 10" fill="none"><path d="M3 1l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
            content.appendChild(toggle);
        } else {
            const spacer = document.createElement('span');
            spacer.className = 'tree-spacer';
            content.appendChild(spacer);
        }

        if (this.options.showIcons) {
            const icon = document.createElement('span');
            icon.className = 'tree-icon';
            icon.innerHTML = this.getAssetIcon(asset.type);
            content.appendChild(icon);
        }

        const label = document.createElement('span');
        label.className = 'tree-label';
        label.textContent = asset.name;
        content.appendChild(label);

        if (asset.metadata?.label) {
            const badge = document.createElement('span');
            badge.className = 'asset-type-badge';
            badge.textContent = asset.metadata.label;
            content.appendChild(badge);
        }

        node.appendChild(content);
        nodeWrapper.appendChild(node);

        if (hasChildren) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'tree-children';
            childrenContainer.style.display = 'none';
            asset.children.forEach(child => childrenContainer.appendChild(this.createTreeNode(child, level + 1)));
            nodeWrapper.appendChild(childrenContainer);
        }

        return nodeWrapper;
    }

    getAssetIcon(type) {
        const icons = {
            building: '<svg viewBox="0 0 16 16" fill="none"><path d="M2 14V4l6-2.5L14 4v10" stroke="#3b82f6" stroke-width="1.3"/><path d="M5 7h2M5 9.5h2M9 7h2M9 9.5h2" stroke="#3b82f6" stroke-width="1.2" stroke-linecap="round"/><path d="M6 14v-3h4v3" stroke="#3b82f6" stroke-width="1.3"/></svg>',
            facility: '<svg viewBox="0 0 16 16" fill="none"><rect x="1.5" y="5" width="13" height="9" rx="1.5" stroke="#8b5cf6" stroke-width="1.3"/><path d="M4 8h3M4 10.5h3M9 8h3" stroke="#8b5cf6" stroke-width="1.2" stroke-linecap="round"/><path d="M5 5V3h6v2" stroke="#8b5cf6" stroke-width="1.3"/></svg>',
            room: '<svg viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="1.5" stroke="#22c55e" stroke-width="1.3"/><path d="M6 8h4" stroke="#22c55e" stroke-width="1.2" stroke-linecap="round"/><circle cx="11" cy="8" r="1" fill="#22c55e"/></svg>',
            equipment: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#f59e0b" stroke-width="1.3"/><circle cx="8" cy="8" r="2" stroke="#f59e0b" stroke-width="1.2"/><path d="M8 2.5V1M8 15v-1.5M13.5 8H15M1 8h1.5" stroke="#f59e0b" stroke-width="1.2" stroke-linecap="round"/></svg>',
            default: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="3" stroke="#64748b" stroke-width="1.3"/><path d="M8 2v2M8 12v2M2 8h2M12 8h2" stroke="#64748b" stroke-width="1.2" stroke-linecap="round"/></svg>'
        };
        return icons[type] || icons.default;
    }

    toggleNode(assetId) {
        const node = this.container.querySelector(`[data-asset-id="${assetId}"]`);
        if (!node) return;
        const children = node.parentElement.querySelector('.tree-children');
        const toggle = node.querySelector('.tree-toggle');
        if (!children || !toggle) return;

        const isExpanded = this.expandedNodes.has(assetId);
        children.style.display = isExpanded ? 'none' : 'block';
        toggle.classList.toggle('expanded', !isExpanded);
        node.setAttribute('aria-expanded', String(!isExpanded));

        if (isExpanded) this.expandedNodes.delete(assetId);
        else this.expandedNodes.add(assetId);
    }

    async selectAsset(assetId) {
        const prev = this.container.querySelector('.tree-node.selected');
        if (prev) prev.classList.remove('selected');

        const node = this.container.querySelector(`[data-asset-id="${assetId}"]`);
        if (!node) return;

        node.classList.add('selected');
        if (this.options.expandOnSelect) this.expandToNode(assetId);
        this.selectedAssetId = assetId;

        const assetData = this.findAssetById(assetId);
        await this.loadNodeChildrenIfNeeded(assetId, assetData);
        this.emit('asset-selected', { assetId, assetData, nodeElement: node });
    }

    async loadNodeChildrenIfNeeded(assetId, assetData) {
        if (!assetData || assetData.children.length > 0) return;
        try {
            const client = window.graphqlClient;
            const nodeData = await client.getNodeChildren(assetData.metadata?.originalName || assetData.name);
            if (nodeData?.children?.length > 0) {
                assetData.children = nodeData.children.map(child => this.transformApiData(child, assetId));
                this.renderTree();
                const node = this.container.querySelector(`[data-asset-id="${assetId}"]`);
                if (node) node.classList.add('selected');
            }
        } catch (error) {
            console.error(`Failed to load children for ${assetId}:`, error);
        }
    }

    expandToNode(assetId) {
        const asset = this.findAssetById(assetId);
        if (!asset) return;
        const path = [];
        let current = asset;
        while (current?.parentId) {
            path.unshift(current.parentId);
            current = this.findAssetById(current.parentId);
        }
        path.forEach(id => { if (!this.expandedNodes.has(id)) this.toggleNode(id); });
    }

    findAssetById(assetId) {
        if (!this.assetData) return null;
        const search = (asset) => {
            if (asset.id === assetId) return asset;
            for (const child of (asset.children || [])) {
                const found = search(child);
                if (found) return found;
            }
            return null;
        };
        const roots = Array.isArray(this.assetData) ? this.assetData : [this.assetData];
        for (const root of roots) {
            const found = search(root);
            if (found) return found;
        }
        return null;
    }

    restoreExpandedState() {
        this.expandedNodes.forEach(assetId => {
            const node = this.container.querySelector(`[data-asset-id="${assetId}"]`);
            if (!node) return;
            const children = node.parentElement.querySelector('.tree-children');
            const toggle = node.querySelector('.tree-toggle');
            if (children && toggle) {
                children.style.display = 'block';
                toggle.classList.add('expanded');
                node.setAttribute('aria-expanded', 'true');
            }
        });
    }

    getSelectedAsset() {
        return this.selectedAssetId ? this.findAssetById(this.selectedAssetId) : null;
    }

    showLoading() {
        this.container.innerHTML = `
            <div class="tree-loading">
                <div class="loading-spinner"></div>
                <div>Loading asset hierarchy...</div>
            </div>
        `;
    }

    showError(message) {
        this.container.innerHTML = `
            <div class="tree-error">
                <div class="error-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="#dc2626" stroke-width="1.5"/>
                        <path d="M12 8v4M12 16h.01" stroke="#dc2626" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <div class="error-message">${message}</div>
                <button class="retry-button" onclick="digitalTwinViewer?.treeBrowser?.loadAssetHierarchy()">Retry</button>
            </div>
        `;
    }

    on(event, callback) {
        if (!this.eventListeners[event]) this.eventListeners[event] = [];
        this.eventListeners[event].push(callback);
    }

    emit(event, data) {
        (this.eventListeners[event] || []).forEach(cb => { try { cb(data); } catch (e) { console.error(e); } });
    }
}

window.TreeBrowser = TreeBrowser;
