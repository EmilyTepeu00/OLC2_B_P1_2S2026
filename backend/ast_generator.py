from graphviz import Digraph
import base64

def generar_ast(nodos):
    dot = Digraph('AST', format='png')
    dot.attr(rankdir='TB', splines='ortho')
    dot.attr('node', shape='box', style='rounded', fontname='monospace')
    
    if not nodos:
        return ""
    
    # CREAR NODOS
    node_counter = 0
    parent_map = {}
    
    for nodo in nodos:
        node_id = f'n{node_counter}'
        node_counter += 1
        dot.node(node_id, nodo['label'])
        parent_map[node_id] = nodo['depth']
    
    # CONECTAR NODOS
    for i, (node_id, depth) in enumerate(parent_map.items()):
        if depth == 0:
            continue
        # Buscar el padre mas cercano (nodo con depth - 1)
        for j in range(i - 1, -1, -1):
            if parent_map.get(f'n{j}', -1) == depth - 1:
                dot.edge(f'n{j}', node_id)
                break
    
    return base64.b64encode(dot.pipe()).decode('utf-8')