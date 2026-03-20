const GraphQLQueries = {
    GET_ASSET_HIERARCHY: `
        query GetHomeHierarchy($rootNode: String!) {
            tree(rootNode: $rootNode) {
                name
                label
                children {
                    name
                    label
                    children {
                        name
                        label
                        children {
                            name
                            label
                        }
                    }
                }
            }
        }
    `,

    GET_NODE_CHILDREN: `
        query GetNodeChildren($rootNode: String!) {
            tree(rootNode: $rootNode) {
                name
                label
                children {
                    name
                    label
                }
            }
        }
    `,

    GET_MEASURES: `
        query GetMeasures($space: String!, $startDate: String!, $endDate: String!) {
            spaces(space: $space, startDate: $startDate, endDate: $endDate) {
                name
                sensors {
                    id
                    space
                    x
                    y
                }
                measurements {
                    name
                    values {
                        timestamp
                        value
                    }
                }
            }
        }
    `
};

window.GraphQLQueries = GraphQLQueries;
