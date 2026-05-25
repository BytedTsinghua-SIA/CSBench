import pytest
import torch
import networkx as nx
from deepsnap.graph import Graph
from part3_deepsnap_advanced import edge_indices_disjoint, cluster_transform_fn


@pytest.fixture
def sample_edge_indices():
    # Create two disjoint edge indices
    edge_index_1 = torch.tensor([
        [0, 1, 2],
        [1, 2, 3]
    ])
    
    # Create two overlapping edge indices
    edge_index_2 = torch.tensor([
        [3, 4, 5],
        [4, 5, 6]
    ])
    
    edge_index_3 = torch.tensor([
        [2, 4, 6],
        [3, 5, 7]
    ])
    
    return edge_index_1, edge_index_2, edge_index_3


def test_edge_indices_disjoint(sample_edge_indices):
    edge_index_1, edge_index_2, edge_index_3 = sample_edge_indices
    
    # Test disjoint edge indices
    is_disjoint = edge_indices_disjoint(edge_index_1, edge_index_2)
    assert isinstance(is_disjoint, bool)
    assert is_disjoint, "Edge indices should be disjoint"
    
    # Test overlapping edge indices (edge (2,3) is in both index_1 and index_3)
    is_disjoint = edge_indices_disjoint(edge_index_1, edge_index_3)
    assert isinstance(is_disjoint, bool)
    assert not is_disjoint, "Edge indices should not be disjoint"


@pytest.fixture
def sample_graph_for_clustering():
    # Create a sample graph with some triangles for clustering coefficient
    G = nx.Graph()
    G.add_nodes_from(range(6))
    
    # Add a triangle (nodes 0, 1, 2)
    G.add_edges_from([(0, 1), (1, 2), (2, 0)])
    
    # Add a chain (nodes 3, 4, 5)
    G.add_edges_from([(3, 4), (4, 5)])
    
    # Add node features
    node_features = {i: torch.randn(5) for i in range(6)}
    nx.set_node_attributes(G, node_features, 'node_feature')
    
    graph = Graph(G)
    return graph


def test_cluster_transform_fn(sample_graph_for_clustering):
    graph = sample_graph_for_clustering
    original_feature_dim = graph.node_feature.shape[1]
    
    # Apply the transformation
    try:
        cluster_transform_fn(graph)
        
        # Check if a new feature dimension was added
        assert graph.node_feature.shape[1] == original_feature_dim + 1, "Cluster transform should add a new feature dimension"
        
        # The first 3 nodes form a triangle, so their clustering coefficient should be 1
        # The nodes in the chain should have clustering coefficient 0
        for i in range(3):
            assert 0.9 < graph.node_feature[i, -1] < 1.1, "Node {} should have clustering coefficient close to 1".format(i)
        
        for i in range(3, 6):
            assert -0.1 < graph.node_feature[i, -1] < 0.1, "Node {} should have clustering coefficient close to 0".format(i)
                   
    except Exception as e:
        pytest.fail(f"cluster_transform_fn raised an exception: {e}")