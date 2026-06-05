"""Tests de l'interface CLI."""

from pathlib import Path

from click.testing import CliRunner
import pandas as pd

from ui.cli.commands import main


def test_infer_command_runs_pipeline() -> None:
    """La commande infer expose un scenario terminal du pipeline V1."""

    result = CliRunner().invoke(
        main,
        [
            "infer",
            "--genre-pref",
            "0.9",
            "--rating",
            "4.8",
            "--popularity",
            "300",
            "--explain",
        ],
    )

    assert result.exit_code == 0
    assert "score=" in result.output
    assert "output_memberships=" in result.output
    assert "R1" in result.output


def test_recommend_command_outputs_top_n_and_explanations(tmp_path: Path) -> None:
    """La commande recommend charge les donnees et affiche les explications."""

    _write_cli_movielens_dataset(tmp_path)

    result = CliRunner().invoke(
        main,
        [
            "recommend",
            "--user-id",
            "1",
            "--top-n",
            "1",
            "--set-genre",
            "Sci-Fi=0.9,Action=0.9",
            "--data-dir",
            str(tmp_path),
            "--explain",
        ],
    )

    assert result.exit_code == 0
    assert "Top-1 recommandations" in result.output
    assert "Matrix Test (1999)" in result.output
    assert "Explication #1" in result.output
    assert "Regles floues activees" in result.output


def test_profile_command_parses_explicit_genres() -> None:
    """La commande profile affiche les preferences explicites."""

    result = CliRunner().invoke(main, ["profile", "--user-id", "7", "--set-genre", "Drama=0.8", "--show"])

    assert result.exit_code == 0
    assert "Profil utilisateur 7" in result.output
    assert "Drama: 0.800" in result.output


def _write_cli_movielens_dataset(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {"movieId": 1, "title": "Matrix Test (1999)", "genres": "Action|Sci-Fi"},
            {"movieId": 2, "title": "Weak Test (2001)", "genres": "Sci-Fi"},
            {"movieId": 3, "title": "Comedy Test (2002)", "genres": "Comedy"},
        ]
    ).to_csv(directory / "movies.csv", index=False)
    pd.DataFrame(
        [
            {"userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 1},
            {"userId": 2, "movieId": 1, "rating": 5.0, "timestamp": 2},
            {"userId": 1, "movieId": 2, "rating": 1.0, "timestamp": 3},
            {"userId": 2, "movieId": 2, "rating": 1.0, "timestamp": 4},
            {"userId": 3, "movieId": 3, "rating": 5.0, "timestamp": 5},
        ]
    ).to_csv(directory / "ratings.csv", index=False)
    pd.DataFrame(
        [{"userId": 1, "movieId": 1, "tag": "demo", "timestamp": 6}]
    ).to_csv(directory / "tags.csv", index=False)
    pd.DataFrame(
        [
            {"movieId": 1, "imdbId": "0000001", "tmdbId": "1"},
            {"movieId": 2, "imdbId": "0000002", "tmdbId": "2"},
            {"movieId": 3, "imdbId": "0000003", "tmdbId": "3"},
        ]
    ).to_csv(directory / "links.csv", index=False)
