"""Commandes CLI prevues pour piloter le systeme.

Les commandes suivent la specification : recommandation, profil, preferences,
evaluation, statistiques dataset, visualisation et test d'inference. La CLI est
le premier point d'entree demonstrable du projet avant la GUI.
"""

from __future__ import annotations

from pathlib import Path

import click

from data_manager.loader import MovieLensLoader
from data_manager.preprocessor import MovieLensPreprocessor
from evaluation.evaluator import Evaluator
from fuzzy.defuzzification import Defuzzifier
from fuzzy.fuzzification import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from fuzzy.linguistic_variables import build_default_v1_system_variables
from fuzzy.rule_base import RuleBase
from recommender.explanation_engine import ExplanationEngine
from recommender.pipeline_factory import (
    build_profile,
    linguistic_level_to_value,
    load_recommender_context,
    parse_genre_preferences,
)
from recommender.user_profile import GenrePreference, UserProfile
from visualization.membership_plots import MembershipPlotter


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
@click.option("--set-genre", "set_genre", default=None, help='Preferences explicites, ex: "Sci-Fi=0.9,Action=0.7".')
@click.option("--data-dir", type=click.Path(path_type=Path), default=Path("data/movie"), show_default=True)
def recommend(user_id: int, top_n: int, explain: bool, set_genre: str | None, data_dir: Path) -> None:
    """Produire les recommandations Top-N pour un utilisateur."""

    if top_n <= 0:
        raise click.ClickException("top-n doit etre strictement positif.")

    context = load_recommender_context(data_dir)
    try:
        profile = build_profile(user_id=user_id, raw_data=context.raw_data, explicit_preferences=set_genre)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    recommender = context.recommender
    recommendations = recommender.recommend(profile, top_n=top_n)

    if not recommendations:
        click.echo("Aucune recommandation produite.")
        return

    click.echo(f"Top-{len(recommendations)} recommandations pour user_id={user_id}")
    for rank, recommendation in enumerate(recommendations, start=1):
        click.echo(
            f"{rank}. {recommendation.movie.movie_id} | "
            f"{recommendation.score:.4f} | {recommendation.movie.title}"
        )

    if explain:
        explanation_engine = ExplanationEngine()
        for rank, recommendation in enumerate(recommendations, start=1):
            explanation = explanation_engine.explain_recommendation(profile, recommendation)
            click.echo("")
            click.echo(f"Explication #{rank}")
            click.echo(explanation.text)


@main.command()
@click.option("--user-id", type=int, required=True)
@click.option("--show", is_flag=True)
@click.option("--set-genre", "set_genre", default=None)
def profile(user_id: int, show: bool, set_genre: str | None) -> None:
    """Afficher un profil flou construit depuis la saisie CLI."""

    if not show and set_genre is None:
        raise click.ClickException("Utilisez --show ou --set-genre.")
    profile = UserProfile(user_id=user_id)
    if set_genre:
        try:
            parsed_preferences = parse_genre_preferences(set_genre)
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
        for genre, value in parsed_preferences.items():
            profile.set_genre_preference(GenrePreference(genre=genre, value=value))

    click.echo(f"Profil utilisateur {user_id}")
    if not profile.genre_preferences:
        click.echo("Aucune preference explicite enregistree dans cette commande.")
        return
    for preference in profile.genre_preferences.values():
        click.echo(f"- {preference.genre}: {preference.value:.3f}")


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
    """Convertir une preference linguistique en valeur crisp V1."""

    if genre is None or level is None:
        raise click.ClickException("--genre et --level sont requis pour la V1.")
    try:
        value = linguistic_level_to_value(level)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"user_id={user_id} genre={genre} level={level} value={value:.3f}")
    if recency is not None or popularity is not None:
        click.echo("recency/popularity sont reserves a une extension future de profil.")


@main.command()
@click.option("--metric", default="all", show_default=True)
@click.option("--top-n", type=int, default=10, show_default=True)
@click.option("--output", default=None)
def evaluate(metric: str, top_n: int, output: str | None) -> None:
    """Evaluer une liste de demonstration avec les metriques V1."""

    context = load_recommender_context()
    raw_data = context.raw_data
    recommender = context.recommender
    profile = build_profile(user_id=1, raw_data=raw_data, explicit_preferences=None)
    recommendations = recommender.recommend(profile, top_n=top_n)
    recommended_ids = [recommendation.movie.movie_id for recommendation in recommendations]
    user_ratings = raw_data["ratings"].loc[raw_data["ratings"]["userId"] == 1]
    relevant_ids = user_ratings.loc[user_ratings["rating"] >= 4.0, "movieId"].astype(int).tolist()
    full_catalog = raw_data["movies"]["movieId"].astype(int).tolist()
    genres_by_movie = {
        movie.movie_id: set(movie.genre_list)
        for movie in recommender.repository.movies
        if movie.movie_id in recommended_ids
    }
    report = Evaluator(top_n=top_n).evaluate_lists(recommended_ids, relevant_ids, full_catalog, genres_by_movie)
    if metric != "all" and metric not in report.metrics:
        raise click.ClickException(f"Metrique inconnue: {metric}. Choix: {sorted(report.metrics)}")
    selected_metrics = report.metrics if metric == "all" else {metric: report.metrics[metric]}
    lines = [f"{name}={value:.4f}" for name, value in selected_metrics.items()]
    rendered = "\n".join(lines)
    if output:
        Path(output).write_text(rendered + "\n", encoding="utf-8")
        click.echo(f"Resultats sauvegardes dans {output}")
    else:
        click.echo(rendered)


@main.command("dataset-stats")
@click.option("--show-genres", is_flag=True)
@click.option("--show-ratings-dist", is_flag=True)
def dataset_stats(show_genres: bool, show_ratings_dist: bool) -> None:
    """Afficher les statistiques descriptives du dataset MovieLens."""

    raw_data = MovieLensLoader().load_all()
    click.echo(f"movies={len(raw_data['movies'])}")
    click.echo(f"ratings={len(raw_data['ratings'])}")
    click.echo(f"tags={len(raw_data['tags'])}")
    click.echo(f"links={len(raw_data['links'])}")
    if show_genres:
        genres = sorted(
            {
                genre
                for genre_string in raw_data["movies"]["genres"]
                for genre in MovieLensPreprocessor().split_genres(genre_string)
            }
        )
        click.echo("genres=" + ",".join(genres))
    if show_ratings_dist:
        distribution = raw_data["ratings"]["rating"].value_counts().sort_index()
        for rating, count in distribution.items():
            click.echo(f"rating_{rating}={count}")


@main.command()
@click.option("--variable", required=True)
@click.option("--save", default=None)
def visualize(variable: str, save: str | None) -> None:
    """Visualiser les fonctions d'appartenance d'une variable V1."""

    variables = build_default_v1_system_variables()
    if variable not in variables:
        raise click.ClickException(f"Variable inconnue: {variable}. Choix: {sorted(variables)}")
    if save is None:
        save = f"{variable}_membership.png"
    output_path = MembershipPlotter(output_dir=Path(save).parent).save_variable_plot(
        variables[variable],
        filename=Path(save).name,
    )
    click.echo(f"Figure sauvegardee dans {output_path}")


@main.command("gui")
def gui_command() -> None:
    """Lancer l'interface graphique Tkinter de demonstration."""

    from ui.gui.main_window import MainWindow

    MainWindow().show()


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
    """Tester manuellement le pipeline flou V1 sur des valeurs crisp."""

    fuzzifier = Fuzzifier.default_v1()
    inference_engine = MamdaniInferenceEngine(RuleBase.load_minimal_v1())
    defuzzifier = Defuzzifier()

    fuzzy_inputs = fuzzifier.fuzzify_inputs(
        user_inputs={"genre_preference": genre_pref},
        movie_inputs={"average_rating": rating, "popularity": popularity},
    )
    inference = inference_engine.infer(fuzzy_inputs)
    score = defuzzifier.defuzzify(dict(inference.output_memberships))
    inference.crisp_score = score

    click.echo(f"score={score:.4f}")
    click.echo(f"output_memberships={dict(inference.output_memberships)}")
    if explain:
        for activation in inference.activated_rules:
            click.echo(f"{activation.rule.identifier} degree={activation.degree:.4f} -> {activation.consequent_term}")
