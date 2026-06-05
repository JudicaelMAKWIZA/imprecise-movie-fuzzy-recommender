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
from fuzzy.config_loader import load_fuzzy_system_config
from fuzzy.defuzzification import Defuzzifier
from fuzzy.fuzzifier import Fuzzifier
from fuzzy.inference_engine import MamdaniInferenceEngine
from recommender.explanation_engine import ExplanationEngine
from recommender.fuzzy_recommender import PrefilterEmptyError
from recommender.pipeline_factory import build_profile, load_recommender_context, parse_genre_preferences, parse_value
from recommender.user_profile import GenrePreference, IntervalGenrePreference, LinguisticGenrePreference, UserProfile
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
@click.option("--data-dir", type=click.Path(path_type=Path), default=Path("data/movie"), show_default=True)
@click.pass_context
def main(ctx: click.Context, config_path: str, verbose: bool, data_dir: Path) -> None:
    """CLI du systeme de recommandation flou."""

    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["verbose"] = verbose
    ctx.obj["data_dir"] = data_dir


@main.command()
@click.option("--user-id", type=int, required=True)
@click.option("--top-n", type=int, default=10, show_default=True)
@click.option("--explain", is_flag=True)
@click.option("--set-genre", "set_genre", default=None, help='Preferences explicites, ex: "Sci-Fi=forte,Action=moyenne".')
@click.option("--data-dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def recommend(
    ctx: click.Context,
    user_id: int,
    top_n: int,
    explain: bool,
    set_genre: str | None,
    data_dir: Path | None,
) -> None:
    """Produire les recommandations Top-N pour un utilisateur."""

    if top_n <= 0:
        raise click.ClickException("top-n doit etre strictement positif.")

    context = load_recommender_context(_resolve_data_dir(ctx, data_dir), config_path=ctx.obj["config_path"])
    try:
        profile = build_profile(user_id=user_id, raw_data=context.raw_data, explicit_preferences=set_genre)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    recommender = context.recommender
    try:
        recommendations = recommender.recommend(profile, top_n=top_n)
    except PrefilterEmptyError as exc:
        raise click.ClickException(str(exc)) from exc

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
        click.echo(f"- {preference.genre}: {_format_preference_value(preference.value)}")


@main.command()
@click.option("--metric", default="all", show_default=True)
@click.option("--user-id", type=int, required=True)
@click.option("--top-n", type=int, default=10, show_default=True)
@click.option("--output", default=None)
@click.option("--data-dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def evaluate(ctx: click.Context, metric: str, user_id: int, top_n: int, output: str | None, data_dir: Path | None) -> None:
    """Evaluer une liste de demonstration avec les metriques V1."""

    context = load_recommender_context(_resolve_data_dir(ctx, data_dir), config_path=ctx.obj["config_path"])
    report = Evaluator(top_n=top_n).evaluate_user(
        user_id=user_id,
        raw_data=context.raw_data,
        recommender=context.recommender,
    )
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
@click.option("--data-dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def dataset_stats(ctx: click.Context, show_genres: bool, show_ratings_dist: bool, data_dir: Path | None) -> None:
    """Afficher les statistiques descriptives du dataset MovieLens."""

    raw_data = MovieLensLoader(raw_dir=_resolve_data_dir(ctx, data_dir)).load_all()
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
@click.option("--data-dir", type=click.Path(path_type=Path), default=None, help="Reserve pour garder les commandes coherentes.")
@click.pass_context
def visualize(ctx: click.Context, variable: str, save: str | None, data_dir: Path | None) -> None:
    """Visualiser les fonctions d'appartenance d'une variable V1."""

    del data_dir
    fuzzy_config = load_fuzzy_system_config(ctx.obj["config_path"])
    variables = {**fuzzy_config.input_variables, **fuzzy_config.output_variables}
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
@click.option("--data-dir", type=click.Path(path_type=Path), default=None)
@click.pass_context
def gui_command(ctx: click.Context, data_dir: Path | None) -> None:
    """Lancer l'interface graphique Tkinter de demonstration."""

    from ui.gui.main_window import MainWindow

    MainWindow(raw_dir=_resolve_data_dir(ctx, data_dir)).show()


@main.command("infer")
@click.option("--genre-pref", type=str, required=True)
@click.option("--rating", type=str, required=True)
@click.option("--popularity", type=str, required=True)
@click.option("--explain", is_flag=True)
@click.pass_context
def infer_command(
    ctx: click.Context,
    genre_pref: str,
    rating: str,
    popularity: str,
    explain: bool,
) -> None:
    """Tester manuellement le pipeline flou V1 sur des valeurs crisp."""

    fuzzy_config = load_fuzzy_system_config(ctx.obj["config_path"])
    fuzzifier = Fuzzifier(fuzzy_config.input_variables)
    inference_engine = MamdaniInferenceEngine(fuzzy_config.rule_base)
    defuzzifier = Defuzzifier(method=fuzzy_config.defuzzification_method)
    try:
        parsed_genre_pref = parse_value("genre_preference", genre_pref, mode="crisp")
        parsed_rating = parse_value("average_rating", rating, mode="crisp")
        parsed_popularity = parse_value("popularity", popularity, mode="crisp")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    fuzzy_inputs = fuzzifier.fuzzify_inputs(
        user_inputs={"genre_preference": parsed_genre_pref},
        movie_inputs={"average_rating": parsed_rating, "popularity": parsed_popularity},
    )
    inference = inference_engine.infer(fuzzy_inputs)
    score = defuzzifier.defuzzify(
        dict(inference.output_memberships),
        variable=fuzzy_config.output_variables["recommendation_score"],
    )
    inference.crisp_score = score

    click.echo(f"score={'indetermine' if score is None else f'{score:.4f}'}")
    click.echo(f"output_memberships={dict(inference.output_memberships)}")
    if explain:
        for activation in inference.activated_rules:
            click.echo(f"{activation.rule.identifier} degree={activation.degree:.4f} -> {activation.consequent_term}")


def _format_preference_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, LinguisticGenrePreference):
        return value.term
    if isinstance(value, IntervalGenrePreference):
        return f"{value.lower:.3f}..{value.upper:.3f}"
    return str(value)


def _resolve_data_dir(ctx: click.Context, data_dir: Path | None) -> Path:
    return data_dir or ctx.obj.get("data_dir", Path("data/movie"))
