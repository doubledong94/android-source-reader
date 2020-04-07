def remove_node(node2node, node_deleted):
    del node2node[node_deleted]
    for node in node2node.copy():
        if node_deleted in node2node[node]:
            del node2node[node][node_deleted]


def separation(node2nodes):
    used_node = []
    sub_graphs = []
    node_too_large = {}
    for node, sub_nodes in node2nodes.copy().items():
        if len(sub_nodes) > 10:
            # print(node + "  " + str(len(sub_nodes)))
            node_too_large[node] = node2nodes[node]
            remove_node(node2nodes, node)
    for node in node2nodes:
        if node not in used_node:
            search_stack = [node]
            used_node.append(node)
            # print('wide search for node : ' + node)
            sub_graphs.append(wide_first_search(node2nodes, search_stack, used_node))
    return sub_graphs, node_too_large


def wide_first_search(node2node, search_stack, used_nodes):
    sub_graph = []
    while len(search_stack) > 0:
        current_node = search_stack.pop(0)
        # hear is the thing you want to do on each node
        # print('adding node : ' + current_node)
        sub_graph.append(current_node)
        for sub_node in node2node[current_node]:
            if sub_node in used_nodes:
                continue
            used_nodes.append(sub_node)
            search_stack.append(sub_node)
    return sub_graph


if __name__ == '__main__':
    a = {'a': ['b', 'c'], 'b': ['a', 'e'], 'c': ['a'], 'd': ['f'], 'e': ['b'], 'f': ['d']}
    print(separation(a))
