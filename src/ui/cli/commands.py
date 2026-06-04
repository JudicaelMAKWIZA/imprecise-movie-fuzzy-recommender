"""Commandes CLI prevues pour piloter le systeme.

Les commandes suivent la specification : recommandation, profil, preferences,
evaluation, statistiques dataset, visualisation et test d'inference. Elles sont
declarees pour stabiliser le contrat utilisateur, mais elles ne branchent pas
encore la logique metier.
"""

from __future__ import annotations

import click


def _not_implemented(feature: str) -> None:
    """Signaler qu'une commande est reservee pour une phase future."""

    raise click.ClickException(f"TODO: {feature} n'est pas encore implemente.")


@click.group()
@click.option(
    "--config",
    "config_path",
    default="config/fuzzy_config.yaml",
    show_default=True,
    help="Chemin vers la configuration floue.",
)
@click.option("--verbose", is_flag=True, help="Afficher les details d'execution.")
@click.pass_context
def main(ctx: click.Context, config_path: str, verbose: bool) -> None:
    """CLI du systeme de recommandation flou."""

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["verbose"] = verbose


@main.command()
@click.option("--user-id", type=int, required=True)
@click.option("--top-n", type=int, default=10, show_default=True)
@click.option("--explain", is_flag=True)
def recommend(user_id: int, top_n: int, explain: bool) -> None:
    """Prevoir les recommandations Top-N pour un utilisateur."""

    _not_implemented("la recommandation Top-N")


@main.command()
@click.option("--user-id", type=int, required=True)
@click.option("--show", is_flag=True)
@click.option("--set-genre", "set_genre", default=None)
def profile(user_id: int, show: bool, set_genre: str | None) -> None:
    """Prevoir l'affichage ou la modification d'un profil flou."""

    _not_implemented("la gestion du profil utilisateur")


@main.command()
@click.option("--user-id", type=int, required=True)
@click.option("--genre", default=None)
@click.option("--level", default=None)
@click.option("--recency", default=None)
@click.option("--popularity", default=None)
def preferences(
    user_id: int,
    genre: str | None,
    level: str | None,
    recency: str | None,
    popularity: str | None,
) -> None:
    """Prevoir la saisie des preferences linguistiques."""

    _not_implemented("la saisie des preferences linguistiques")


@main.command()
@click.option("--metric", default="all", show_default=True)
@click.option("--top-n", type=int, default=10, show_default=True)
@click.option("--output", default=None)
def evaluate(metric: str, top_n: int, output: str | None) -> None:
    """Prevoir l'evaluation du systeme."""

    _not_implemented("l'evaluation du systeme")


@main.command("dataset-stats")
@click.option("--show-genres", is_flag=True)
@click.option("--show-ratings-dist", is_flag=True)
def dataset_stats(show_genres: bool, show_ratings_dist: bool) -> None:
    """Prevoir les statistiques descriptives du dataset."""

    _not_implemented("les statistiques du dataset")


@main.command()
@click.option("--variable", required=True)
@click.option("--save", default=None)
def visualize(variable: str, save: str | None) -> None:
    """Prevoir la visualisation des fonctions d'appartenance."""

    _not_implemented("la visualisation des fonctions d'appartenance")


@main.command("infer")
@click.option("--genre-pref", type=float, required=True)
@click.option("--rating", type=float, required=True)
@click.option("--popularity", type=float, required=True)
@click.option("--explain", is_flag=True)
def infer_command(
    genre_pref: float,
    rating: float,
    popularity: float,
    explain: bool,
) -> None:
    """Prevoir un test manuel du moteur d'inference."""

    _not_implemented("le moteur d'inference Mamdani")
