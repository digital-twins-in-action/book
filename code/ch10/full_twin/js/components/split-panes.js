class SplitPanes {
    constructor() {
        this.verticalSplit = null;
        this.horizontalSplit = null;
        this.mobileBreakpoint = 768;
    }

    isMobile() {
        return window.innerWidth <= this.mobileBreakpoint;
    }

    init() {
        if (this.isMobile()) {
            this._clearSplits();
            return;
        }

        this.verticalSplit = Split(['#tree-browser-pane', '#right-pane'], {
            direction: 'horizontal',
            sizes: [25, 75],
            minSize: [200, 400],
            gutterSize: 6,
            cursor: 'col-resize'
        });

        this.horizontalSplit = Split(['#scene-viewer-pane', '#data-panel-pane'], {
            direction: 'vertical',
            sizes: [60, 40],
            minSize: [300, 200],
            gutterSize: 6,
            cursor: 'row-resize'
        });

        window.addEventListener('resize', () => this.handleWindowResize());
    }

    _clearSplits() {
        if (this.verticalSplit) {
            this.verticalSplit.destroy();
            this.verticalSplit = null;
        }
        if (this.horizontalSplit) {
            this.horizontalSplit.destroy();
            this.horizontalSplit = null;
        }
        // Remove inline styles Split.js may have set
        ['tree-browser-pane', 'right-pane', 'scene-viewer-pane', 'data-panel-pane'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.removeProperty('width'), el.style.removeProperty('height');
        });
    }

    handleWindowResize() {
        if (this.isMobile() && (this.verticalSplit || this.horizontalSplit)) {
            this._clearSplits();
        } else if (!this.isMobile() && !this.verticalSplit) {
            this.init();
        }
    }
}

window.SplitPanes = SplitPanes;
