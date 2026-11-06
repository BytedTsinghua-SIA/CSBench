import numpy as np
import pytest

try:
    from movie_recommender import (
        svd_lfm,
        get_train_mse,
        update_user_vecs,
        update_movie_vecs,
    )
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_ERROR = e
    svd_lfm = get_train_mse = update_user_vecs = update_movie_vecs = None


def _ensure_import_ok():
    if IMPORT_ERROR is not None:
        pytest.fail(f"Import movie_recommender failed: {IMPORT_ERROR}")


def test_svd_lfm_reconstructs_observed_entries():
    _ensure_import_ok()

    R = np.array([[3.0, np.nan], [np.nan, -2.0]])
    user_vecs, movie_vecs = svd_lfm(R.copy())
    assert np.isclose(user_vecs[0].dot(movie_vecs[0]), 3.0, atol=1e-6)
    assert np.isclose(user_vecs[1].dot(movie_vecs[1]), -2.0, atol=1e-6)


def test_get_train_mse_matches_manual_average():
    _ensure_import_ok()

    user_vecs = np.array([[1.0, 0.0], [0.0, 1.0]])
    movie_vecs = np.array([[1.0, 0.0], [0.0, 1.0]])
    R = np.array([[1.0, np.nan], [np.nan, 3.0]])
    mse = get_train_mse(R, user_vecs, movie_vecs)
    assert np.isclose(mse, ((1.0 - 1.0)**2 + (1.0 - 3.0)**2) / 2)


def test_als_updates_solve_regularized_system():
    _ensure_import_ok()

    R = np.array([[4.0, np.nan], [np.nan, 6.0]])
    user_vecs = np.zeros((2, 2))
    movie_vecs = np.array([[2.0, 0.0], [0.0, 2.0]])
    user_rated = np.array([np.array([0]), np.array([1])], dtype=object)
    movie_rated = np.array([np.array([0]), np.array([1])], dtype=object)

    updated_users = update_user_vecs(user_vecs.copy(), movie_vecs, R, user_rated)
    assert np.allclose(updated_users[0], np.array([8.0/5.0, 0.0]))
    assert np.allclose(updated_users[1], np.array([0.0, 12.0/5.0]))

    updated_movies = update_movie_vecs(updated_users, movie_vecs.copy(), R, movie_rated)
    assert np.allclose(updated_movies[0], np.array([160.0/89.0, 0.0]))
    assert np.allclose(updated_movies[1], np.array([0.0, 360.0/169.0]))