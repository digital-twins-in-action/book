class GraphQLClient {
    constructor(endpoint, options = {}) {
        this.endpoint = endpoint || '/graphql';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        this.maxRetries = options.maxRetries || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.timeout = options.timeout || 10000;
    }

    async query(query, variables = {}) {
        let lastError;

        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(this.endpoint, {
                    method: 'POST',
                    headers: this.defaultHeaders,
                    body: JSON.stringify({ query, variables }),
                    signal: controller.signal,
                    mode: 'cors',
                    credentials: 'omit'
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const result = await response.json();

                if (result.errors && result.errors.length > 0) {
                    throw new Error(`GraphQL: ${result.errors.map(e => e.message).join(', ')}`);
                }

                return result.data;
            } catch (error) {
                lastError = error;
                if (error.name === 'AbortError') {
                    lastError = new Error('Request timeout');
                }
                if (attempt < this.maxRetries) {
                    await new Promise(r => setTimeout(r, this.retryDelay * Math.pow(2, attempt)));
                }
            }
        }

        throw lastError;
    }

    async getAssetHierarchy(rootNode = "742 Evergreen Terrace") {
        const q = GraphQLQueries.GET_ASSET_HIERARCHY;
        const result = await this.query(q, { rootNode });
        return { assetHierarchy: result.tree };
    }

    async getNodeChildren(nodeName) {
        const q = GraphQLQueries.GET_NODE_CHILDREN;
        const result = await this.query(q, { rootNode: nodeName });
        return result.tree;
    }

    async getMeasures(spaceName, startDate = "2025-10-06T00:00:00Z", endDate = "2025-10-06T01:00:59Z") {
        const q = GraphQLQueries.GET_MEASURES;
        const result = await this.query(q, { space: spaceName, startDate, endDate });
        return result.spaces;
    }
}

window.GraphQLClient = GraphQLClient;
