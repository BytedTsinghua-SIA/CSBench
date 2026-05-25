import torch
import networkx as nx
import matplotlib.pyplot as plt

from deepsnap.graph import Graph
from deepsnap.batch import Batch
from deepsnap.dataset import GraphDataset
from torch_geometric.datasets import Planetoid, TUDataset

from torch.utils.data import DataLoader

def edge_indices_disjoint(edge_index_1, edge_index_2):
    # TODO: Implement this function that takes two edge index tensors,
    # and returns whether these two edge index tensors are disjoint.
    disjoint = None

    ############# Your code here ############
    ## (~5 lines of code)
    ## Note
    ## 1. Here disjoint means that there is no single edge belongs to either edge index tensors
    ## 2. You do not need to consider the undirected case. For example, if edge_index_1 contains
    ## edge (a, b) and edge_index_2 contains edge (b, a). We will treat them as disjoint in this
    ## function.
    pass

    #########################################

    return disjoint

def cluster_transform_fn(graph):
    # TODO: Implement this function that takes an deepsnap graph object,
    # transform the graph by adding nodes clustering coefficient into the
    # graph.node_feature

    ############# Your code here ############
    ## (~5 lines of code)
    ## Note
    ## 1. Compute the clustering coefficient value for each node and
    ## concat them to the last dimension of graph.node_feature
    pass

    #########################################