class SplitPanes {
    constructor() {
        this.verticalSplit = null;
        this.horizontalSplit = null;
    }

    init() {
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
    }

    handleWindowResize() {
        // Split.js handles resize automatically
    }
}

window.SplitPanes = SplitPanes;
