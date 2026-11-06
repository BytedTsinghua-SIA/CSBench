# CS224W - Colab 3: GNN Layers, DeepSNAP, and Link Prediction

## Background

In Colab 2, we used pre-built GNN layers from PyTorch Geometric. In this Colab, we will dive deeper by implementing popular GNN layers, **GraphSAGE** and **Graph Attention Network (GAT)**, from scratch. We will then explore **DeepSNAP**, a powerful library for advanced graph manipulations, data splitting, and feature engineering. Finally, we will apply our knowledge to build a GNN for a new task: **link prediction**.

### Learning Goals

- Implement custom GNN layers (GraphSAGE and GAT) using the PyTorch Geometric message-passing API.
- Understand the inner workings of attention mechanisms in GATs.
- Utilize DeepSNAP for sophisticated graph operations, including transductive and inductive data splitting for node, edge, and graph-level tasks.
- Perform graph transformations and compute node features like PageRank and clustering coefficients.
- Build and train a GNN model for link prediction, a common edge-level task.

### Assignment Structure

The assignment is divided into four main parts:

1.  **GNN Layers from Scratch**: You will implement the `forward`, `message`, and `aggregate` methods for both GraphSAGE and GAT layers. This will give you a fundamental understanding of how GNNs propagate information.

    For the **GraphSAGE** layer, you will implement the following update rule, which includes a skip connection and mean aggregation. $\ell$-2 normalization is applied after each iteration.

    > \begin{equation}
    > h_v^{(l)} = W_l\cdot h_v^{(l-1)} + W_r \cdot AGG(\{h_u^{(l-1)}, \forall u \in N(v) \})
    > \end{equation}

    > \begin{equation}
    > AGG(\{h_u^{(l-1)}, \forall u \in N(v) \}) = \frac{1}{|N(v)|} \sum_{u\in N(v)} h_u^{(l-1)}
    > \end{equation}

    For the **GAT** layer, you will implement a multi-head attention mechanism. The attention coefficients are computed as follows:

    > \begin{equation}
    > \alpha_{ij} = \frac{\exp\Big(\text{LeakyReLU}\Big(\overrightarrow{a_l}^T \mathbf{W_l} \overrightarrow{h_i} + \overrightarrow{a_r}^T\mathbf{W_r}\overrightarrow{h_j}\Big)\Big)}{\sum_{k\in \mathcal{N}_i} \exp\Big(\text{LeakyReLU}\Big(\overrightarrow{a_l}^T \mathbf{W_l} \overrightarrow{h_i} + \overrightarrow{a_r}^T\mathbf{W_r}\overrightarrow{h_k}\Big)\Big)}
    > \end{equation}

    The final output features for each node are then computed as a concatenation of the outputs from multiple attention heads:

    > \begin{equation}
    >     \overrightarrow{h_i}' = ||_{k=1}^K \Big(\sum_{j \in \mathcal{N}_i} \alpha_{ij}^{(k)} \mathbf{W_r}^{(k)} \overrightarrow{h_j}\Big)
    > \end{equation}

2.  **DeepSNAP Basics**: You will get acquainted with the `deepsnap.graph.Graph` and `deepsnap.dataset.GraphDataset` objects. You'll write functions to inspect graph properties within the DeepSNAP framework.

3.  **Advanced DeepSNAP**: You will explore more advanced features of DeepSNAP, including different data splitting strategies for link prediction (`"all"` vs. `"disjoint"`) and writing custom graph transformation functions to engineer new node features.

4.  **GNN for Link Prediction**: You will build a complete GNN pipeline to predict missing links in the CORA citation network. This involves implementing the model, loss function, and training/testing loops for this edge-level task.

### Files to Edit

Your solution will be implemented across the following four files:

*   `part1_gnn_layers.py`: Implement the GraphSAGE and GAT models.
*   `part2_deepsnap_basics.py`: Implement functions to get graph statistics using DeepSNAP.
*   `part3_deepsnap_advanced.py`: Implement functions for edge splitting analysis and graph feature transformation.
*   `part4_link_prediction.py`: Implement the GNN model and training pipeline for link prediction.