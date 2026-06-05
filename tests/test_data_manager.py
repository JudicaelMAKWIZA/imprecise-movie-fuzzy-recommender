"""Tests du chargement et du pretraitement MovieLens."""

from pathlib import Path

import pandas as pd
import pytest

from data_manager.loader import DataLoadingError, DataValidationError, MovieLensLoader
from data_manager.preprocessor import MovieLensPreprocessor


def test_loader_loads_all_movielens_files(tmp_path: Path) -> None:
    """Le loader charge les quatre fichiers officiels avec validation."""

    _write_minimal_movielens_dataset(tmp_path)
    loader = MovieLensLoader(raw_dir=tmp_path)

    data = loader.load_all()

    assert set(data) == {"movies", "ratings", "tags", "links"}
    assert len(data["movies"]) == 2
    assert len(data["ratings"]) == 3


def test_loader_raises_for_missing_file(tmp_path: Path) -> None:
    """Un fichier absent produit une erreur de chargement explicite."""

    loader = MovieLensLoader(raw_dir=tmp_path)

    with pytest.raises(DataLoadingError):
        loader.load_movies()


def test_loader_validates_required_columns(tmp_path: Path) -> None:
    """Les colonnes obligatoires sont controlees."""

    (tmp_path / "movies.csv").write_text("movieId,title\n1,Toy Story (1995)\n", encoding="utf-8")
    loader = MovieLensLoader(raw_dir=tmp_path)

    with pytest.raises(DataValidationError):
        loader.load_movies()


def test_preprocessor_builds_movie_features(tmp_path: Path) -> None:
    """Le preprocesseur derive notes, popularite, genres et annee."""

    _write_minimal_movielens_dataset(tmp_path)
    raw_data = MovieLensLoader(raw_dir=tmp_path).load_all()
    preprocessor = MovieLensPreprocessor(processed_dir=tmp_path / "processed")

    features = preprocessor.build_movie_features(raw_data)
    toy_story = features.loc[features["movieId"] == 1].iloc[0]

    assert toy_story["avg_rating"] == pytest.approx(4.25)
    assert toy_story["num_ratings"] == 2
    assert toy_story["genre_list"] == ["Adventure", "Animation"]
    assert toy_story["release_year"] == 1995
    assert toy_story["genre_vector"]["Adventure"] == 1
    assert toy_story["genre_comedy"] == 0


def test_preprocessor_save_and_load_processed_features(tmp_path: Path) -> None:
    """Les donnees derivees peuvent etre sauvegardees et rechargees en CSV."""

    _write_minimal_movielens_dataset(tmp_path)
    raw_data = MovieLensLoader(raw_dir=tmp_path).load_all()
    preprocessor = MovieLensPreprocessor(processed_dir=tmp_path / "processed")
    features = preprocessor.build_movie_features(raw_data)

    output_path = preprocessor.save_processed(features)
    loaded = preprocessor.load_processed(output_path.name)

    assert output_path.exists()
    assert isinstance(loaded.loc[0, "genre_list"], list)
    assert isinstance(loaded.loc[0, "genre_vector"], dict)


def test_release_year_extraction_handles_missing_year() -> None:
    """Un titre sans annee retourne None."""

    preprocessor = MovieLensPreprocessor()

    assert preprocessor.extract_release_year("Unknown title") is None
    assert preprocessor.extract_release_year("Movie (Director Cut) (2001)") == 2001


def _write_minimal_movielens_dataset(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {"movieId": 1, "title": "Toy Story (1995)", "genres": "Adventure|Animation"},
            {"movieId": 2, "title": "Jumanji (1995)", "genres": "Adventure|Comedy"},
        ]
    ).to_csv(directory / "movies.csv", index=False)
    pd.DataFrame(
        [
            {"userId": 1, "movieId": 1, "rating": 4.0, "timestamp": 111},
            {"userId": 2, "movieId": 1, "rating": 4.5, "timestamp": 112},
            {"userId": 1, "movieId": 2, "rating": 3.0, "timestamp": 113},
        ]
    ).to_csv(directory / "ratings.csv", index=False)
    pd.DataFrame(
        [{"userId": 1, "movieId": 1, "tag": "classic", "timestamp": 114}]
    ).to_csv(directory / "tags.csv", index=False)
    pd.DataFrame(
        [
            {"movieId": 1, "imdbId": "0114709", "tmdbId": "862"},
            {"movieId": 2, "imdbId": "0113497", "tmdbId": "8844"},
        ]
    ).to_csv(directory / "links.csv", index=False)
