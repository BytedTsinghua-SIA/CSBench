import pytest
import torch
import networkx as nx
from deepsnap.graph import Graph
from deepsnap.dataset import GraphDataset
from part2_deepsnap_basics import (
    get_num_node_classes,
    get_num_node_features,
    get_graph_class,
    get_graph_num_edges
)


@pytest.fixture
def sample_deepsnap_graph():
    # Create a sample NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(range(5))
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
    
    # Add node features and labels
    node_features = {i: torch.randn(10) for i in range(5)}
    node_labels = {i: torch.tensor(i % 3) for i in range(5)}
    
    nx.set_node_attributes(G, node_features, 'node_feature')
    nx.set_node_attributes(G, node_labels, 'node_label')
    
    # Convert to DeepSNAP graph
    graph = Graph(G)
    return graph


@pytest.fixture
def sample_deepsnap_dataset():
    # Create a list of sample DeepSNAP graphs
    graphs = []
    for i in range(3):
        G = nx.Graph()
        G.add_nodes_from(range(3 + i))
        G.add_edges_from([(0, 1), (1, 2)])
        
        # Add node features and graph label
        node_features = {j: torch.randn(8) for j in range(3 + i)}
        nx.set_node_attributes(G, node_features, 'node_feature')
        
        # Add graph-level label
        G.graph['graph_label'] = torch.tensor(i)
        
        graph = Graph(G)
        graphs.append(graph)
    
    dataset = GraphDataset(graphs, task='graph')
    return dataset


def test_get_num_node_classes(sample_deepsnap_graph):
    # Since we have 3 classes (0, 1, 2) in our sample
    num_classes = get_num_node_classes(sample_deepsnap_graph)
    assert isinstance(num_classes, int)
    assert num_classes >= 3  # Should be at least 3


def test_get_num_node_features(sample_deepsnap_graph):
    # We have 10 features per node in our sample
    num_features = get_num_node_features(sample_deepsnap_graph)
    assert isinstance(num_features, int)
    assert num_features == 10


def test_get_graph_class(sample_deepsnap_dataset):
    # Test with different indices
    for idx in range(len(sample_deepsnap_dataset)):
        label = get_graph_class(sample_deepsnap_dataset, idx)
        assert isinstance(label, int)
        assert label == idx  # Our dataset has labels 0, 1, 2


def test_get_graph_num_edges(sample_deepsnap_dataset):
    # Our graphs have 2 edges each (undirected)
    for idx in range(len(sample_deepsnap_dataset)):
        num_edges = get_graph_num_edges(sample_deepsnap_dataset, idx)
        assert isinstance(num_edges, int)
        assert num_edges == 2  # Each graph has 2 edges