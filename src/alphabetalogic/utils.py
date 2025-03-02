import random

import matplotlib.pyplot as plt
import networkx as nx


class Vertex:
    """
    Klasa reprezentujaca polaczenie dwoch wezlow.

    Attributes
    ----------
        beg: object
            Poczatek wezla.
        end: object
            Koniec wezla.
        desc: str
            Opis wyrazenia znajdujacego sie w wezle.
    """

    def __init__(self, beg, end, desc):
        self.beg = beg
        self.end = end
        self.desc: str = desc

class GraphVisualizer:
    def __init__(self, root, nodes):
        self.root = root
        self.nodes = nodes
        self.graph = nx.Graph()
        self.labels = {}

    def hierarchy_pos(self, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
        """
        From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
        Licensed under Creative Commons Attribution-Share Alike

        If the graph is a tree this will return the positions to plot this in a
        hierarchical layout.

        G: the graph (must be a tree)

        root: the root node of current branch
        - if the tree is directed and this is not given,
        the root will be found and used
        - if the tree is directed and this is given, then
        the positions will be just for the descendants of this node.
        - if the tree is undirected and not given,
        then a random choice will be used.

        width: horizontal space allocated for this branch - avoids overlap with other branches

        vert_gap: gap between levels of hierarchy

        vert_loc: vertical location of root

        xcenter: horizontal location of root
        """
        if not nx.is_tree(self.graph):
            raise TypeError("cannot use hierarchy_pos on a graph that is not a tree")

        if self.root is None:
            if isinstance(self.graph, nx.DiGraph):
                self.root = next(
                    iter(nx.topological_sort(self.graph))
                )  # allows back compatibility with nx version 1.11
            else:
                self.root = random.choice(list(self.graph.nodes))

        def _hierarchy_pos(
            G, root, width=1.0, vert_gap=0.2, vert_loc=0.0, xcenter=0.5, pos=None, parent=None
        ):
            """
            see hierarchy_pos docstring for most arguments

            pos: a dict saying where all nodes go if they have been assigned
            parent: parent of this branch. - only affects it if non-directed

            """

            if pos is None:
                pos = {root: (xcenter, vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)
            children = list(G.neighbors(root))
            if not isinstance(G, nx.DiGraph) and parent is not None:
                children.remove(parent)
            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(
                        G,
                        child,
                        width=dx,
                        vert_gap=vert_gap,
                        vert_loc=vert_loc - vert_gap,
                        xcenter=nextx,
                        pos=pos,
                        parent=root,
                    )
            return pos

        return _hierarchy_pos(self.graph, self.root, width, vert_gap, vert_loc, xcenter)

    def display(self):
        self.graph.add_edges_from([[node.beg, node.end] for node in self.nodes])
        self.edge_labels = dict(
            [((node.beg, node.end), node.desc) for node in self.nodes]
        )
        for node in self.graph.nodes():
            self.labels[node] = node.exp

        self.color_map = [node.color for node in self.graph]

        options = {"edgecolors": "black", "node_size": 1200}
        pos = self.hierarchy_pos()
        # pos = nx.spring_layout(self.graph)

        nx.draw(
            self.graph,
            pos=pos,
            with_labels=True,
            node_color=self.color_map,
            labels=self.labels,
            **options,
        )

        nx.draw_networkx_edge_labels(
            self.graph,
            pos=pos,
            edge_labels=self.edge_labels,
            label_pos=0.5,
            rotate=False,
            alpha=0.4,
            font_color="black",
            font_size=7,
            font_weight="bold",
        )

        # plt.savefig("graph.png", format="PNG")
        plt.show()

def negate_expression(logical_expression: str) -> str:

    return "~" + logical_expression


