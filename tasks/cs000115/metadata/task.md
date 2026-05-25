# Task Overview
This homework requires finishing the recommender system and k-nearest neighbors utilities. Complete every `TODO` so that the latent factor model based on SVD works, including training MSE calculation and alternating least squares updates. Finish the PCA visualization, nearest-neighbor lookup, scaling pipeline, and hyperparameter grid search for the world values dataset.

# Implementation Requirements
- Edit only the existing modules and keep the provided structure.
- `movie_recommender.py` must handle missing entries by zero fill, compute the compact SVD, build user and movie embeddings, report training MSE over observed ratings, set the dimensionality used in the alternating optimization, and implement the user/movie updates that solve the regularized least-squares systems using the provided rated-index lists.
- `world_values_utils.py` needs to fit PCA to the survey feature matrix and return the first two components for plotting.
- `world_values_starter.py` should list the seven nearest countries to the USA entry and perform a grid search using `GridSearchCV` with negative mean-squared-error scoring to report RMSE values.
- `world_values_pipelines.py` must scale inputs before KNN regression.
- `world_values_parameters.py` should configure the grid search to use distance-based neighbor weighting.
