import torch
import networkx as nx
import matplotlib.pyplot as plt

from deepsnap.graph import Graph
from deepsnap.batch import Batch
from deepsnap.dataset import GraphDataset
from torch_geometric.datasets import Planetoid, TUDataset

from torch.utils.data import DataLoader

def get_num_node_classes(graph):
    # TODO: Implement this function that takes a deepsnap graph object
    # and return the number of node classes of that graph.

    num_node_classes = 0

    ############# Your code here #############
    ## (~1 line of code)
    ## Note
    ## 1. Colab autocomplete functionality might be useful
    ## 2. DeepSNAP documentation might be useful https://snap.stanford.edu/deepsnap/modules/graph.html


    ##########################################

    return num_node_classes

def get_num_node_features(graph):
    # TODO: Implement this function that takes a deepsnap graph object
    # and return the number of node features of that graph.

    num_node_features = 0

    ############# Your code here #############
    ## (~1 line of code)
    ## Note
    ## 1. Colab autocomplete functionality might be useful
    ## 2. DeepSNAP documentation might be useful https://snap.stanford.edu/deepsnap/modules/graph.html


    ##########################################

    return num_node_features

def get_graph_class(dataset, idx):
    # TODO: Implement this function that takes a deepsnap dataset object,
    # the index of the graph in the dataset, and returns the class/label
    # of the graph (in integer).

    label = -1

    ############# Your code here ############
    ## (~1 line of code)
    ## Note
    ## 1. The label refers to the graph-level attribute


    #########################################

    return label

def get_graph_num_edges(dataset, idx):
    # TODO: Implement this function that takes a deepsnap dataset object,
    # the index of the graph in dataset, and returns the number of
    # edges in the graph (in integer).

    num_edges = 0

    ############# Your code here ############
    ## (~1 lines of code)
    ## Note
    ## 1. You can use the class property directly


    #########################################

    return num_edges