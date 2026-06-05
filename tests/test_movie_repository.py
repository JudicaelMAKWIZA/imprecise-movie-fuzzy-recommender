"""Tests du repository de films."""

import pandas as pd

from data_manager.movie_repository import MovieRepository
from data_manager.schemas import MovieFeatures


def test_movie_repository_indexes_and_filters_by_genres() -> None:
    """Le repository permet l'acces par id et le prefiltrage crisp par genre."""

    repository = MovieRepository(
        [
            MovieFeatures(1, "A", ["Sci-Fi"], 4.0, 100),
            MovieFeatures(2, "B", ["Comedy"], 3.0, 10),
        ]
    )

    assert repository.get_by_id(1).title == "A"
    assert [movie.movie_id for movie in repository.filter_by_genres(["sci-fi"])] == [1]
    assert [movie.movie_id for movie in repository.filter_by_genres([])] == [1, 2]


def test_movie_repository_search_by_title() -> None:
    """La recherche titre est deterministe et insensible a la casse."""

    repository = MovieRepository([MovieFeatures(1, "Interstellar (2014)")])

    assert repository.search_by_title("stellar")[0].movie_id == 1
    assert repository.search_by_title("") == []


def test_movie_repository_from_dataframe() -> None:
    """Le repository peut etre construit depuis les donnees pretraitees."""

    dataframe = pd.DataFrame(
        [
            {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genre_list": ["Adventure", "Animation"],
                "avg_rating": 4.25,
                "num_ratings": 2,
                "release_year": 1995,
                "genre_vector": {"Adventure": 1, "Animation": 1},
            }
        ]
    )

    repository = MovieRepository.from_dataframe(dataframe)
    movie = repository.get_by_id(1)

    assert movie.title == "Toy Story (1995)"
    assert movie.average_rating == 4.25
    assert movie.number_of_ratings == 2
    assert movie.genre_vector["Adventure"] == 1


def test_movie_repository_from_dataframe_decodes_serialized_feature_columns() -> None:
    """Les colonnes relues depuis CSV restent compatibles avec le pipeline."""

    dataframe = pd.DataFrame(
        [
            {
                "movieId": 1,
                "title": "Toy Story (1995)",
                "genre_list": '["Adventure", "Animation"]',
                "avg_rating": 4.25,
                "num_ratings": 2,
                "release_year": 1995,
                "genre_vector": '{"Adventure": 1, "Animation": 1}',
            }
        ]
    )

    repository = MovieRepository.from_dataframe(dataframe)
    movie = repository.get_by_id(1)

    assert movie.genre_list == ["Adventure", "Animation"]
    assert movie.genre_vector == {"Adventure": 1, "Animation": 1}
