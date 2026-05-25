import numpy as np
import pandas as pd
import matplotlib
import pytest

matplotlib.use('Agg')

try:
    import world_values_utils as utils
    from world_values_utils import plot_pca
    from world_values_pipelines import k_nearest_neighbors_regression_pipeline
    from world_values_parameters import regression_knn_parameters
    from world_values_starter import _rmse_grid_search
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_ERROR = e
    utils = None
    plot_pca = None
    k_nearest_neighbors_regression_pipeline = None
    regression_knn_parameters = None
    _rmse_grid_search = None


def _ensure_import_ok():
    if IMPORT_ERROR is not None:
        pytest.fail(f"Import world_values_* modules failed: {IMPORT_ERROR}")


def test_plot_pca_projects_two_dimensions(monkeypatch):
    _ensure_import_ok()

    captured = {}

    class DummyPCA:
        def __init__(self, n_components):
            captured['n_components'] = n_components

        def fit_transform(self, data):
            captured['rows'] = len(data)
            return np.zeros((len(data), 2))

    monkeypatch.setattr(utils, 'PCA', DummyPCA)

    scatter_args = {}

    def fake_scatter(x, y, c=None):
        scatter_args['x'] = x
        scatter_args['y'] = y
        scatter_args['c'] = c

    monkeypatch.setattr(utils.plt, 'scatter', fake_scatter)
    monkeypatch.setattr(utils.plt, 'show', lambda: None)

    values = pd.DataFrame({'a': [1.0, 2.0, 3.0], 'b': [4.0, 5.0, 6.0]})
    labels = pd.DataFrame({'2015': [0.3, 0.5, 0.7]})

    plot_pca(values, labels)

    assert captured['n_components'] == 2
    assert captured['rows'] == 3
    assert len(scatter_args['x']) == 3
    assert np.array_equal(scatter_args['c'], labels['2015'])


def test_pipeline_and_parameters_configuration():
    _ensure_import_ok()

    scale = k_nearest_neighbors_regression_pipeline.named_steps['scale']
    assert scale.__class__.__name__ == 'StandardScaler'
    assert regression_knn_parameters['knn__weights'] == ['distance']


def test_rmse_grid_search_executes(monkeypatch):
    _ensure_import_ok()

    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'show', lambda: None)

    X = pd.DataFrame(
        np.array([[0.0, 1.0], [1.0, 0.5], [0.5, 0.8], [1.5, 1.2]]),
        columns=['f1', 'f2'],
    )
    y = pd.DataFrame({'2015': [0.1, 0.2, 0.3, 0.4]})

    params = {
        'knn__n_neighbors': [1, 2],
        'knn__weights': ['distance'],
    }

    _rmse_grid_search(X, y, k_nearest_neighbors_regression_pipeline, params, 'knn')