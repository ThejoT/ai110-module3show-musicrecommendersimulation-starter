"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main                                  # all profiles, default mode
    python -m src.main --mode mood-first                # switch ranking strategy
    python -m src.main --diverse                        # apply artist/genre diversity penalty
    python -m src.main --table                          # summary table with reasons
    python -m src.main --profile "Chill Lofi" --table --diverse
    python -m src.main --list-modes
"""

import argparse
import textwrap

try:
    from src.recommender import STRATEGIES, get_strategy, load_songs, recommend_songs
except ImportError:  # also works when run as `python src/main.py`
    from recommender import STRATEGIES, get_strategy, load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Adversarial / edge-case profiles
    "Conflicted: Sad but High-Energy": {"genre": "blues", "mood": "sad", "energy": 0.9},
    "Unknown Genre: K-pop": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
}

# Profiles that use the advanced attributes (popularity, decade, mood tags,
# instrumentalness, speechiness). Run with --profile "<name>".
ADVANCED_PROFILES = {
    "Late-Night Focus (advanced)": {
        "genre": "lofi", "mood": "focused", "energy": 0.4, "likes_acoustic": True,
        "decade": "2020s", "mood_tags": ["late-night", "cozy", "focused"],
        "popularity": "niche", "likes_instrumental": True, "likes_spoken_word": False},
    "Throwback Road Trip (advanced)": {
        "genre": "country", "mood": "nostalgic", "energy": 0.6, "decade": "2000s",
        "mood_tags": ["nostalgic", "driving", "warm"], "popularity": "mainstream",
        "likes_instrumental": False},
}
ALL_PROFILES = {**PROFILES, **ADVANCED_PROFILES}


def describe_prefs(user_prefs: dict) -> str:
    """Turn a preferences dictionary into one readable line."""
    return ", ".join(f"{k}={'/'.join(v) if isinstance(v, list) else v}" for k, v in user_prefs.items())


def print_recommendations(name: str, user_prefs: dict, recommendations) -> None:
    """Print a profile and its ranked recommendations with scores and reasons."""
    print(f"\n=== {name} ===")
    print(f"Profile: {describe_prefs(user_prefs)}\n")
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{rank}. {song['title']} by {song['artist']} ({song['genre']}, {song['mood']})")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")


def print_table(name: str, user_prefs: dict, recommendations, mode: str, diverse: bool) -> None:
    """Print recommendations as an ASCII table, wrapping the reasons column."""
    widths = {"#": 2, "Song": 22, "Artist": 16, "Genre": 10, "Score": 5, "Why": 50}
    border = "+" + "+".join("-" * (w + 2) for w in widths.values()) + "+"

    def row(cells):
        return "| " + " | ".join(f"{str(c):<{w}}" for c, w in zip(cells, widths.values())) + " |"

    print(f"\n{name}  [mode: {mode}{', diversity on' if diverse else ''}]")
    print(f"Profile: {describe_prefs(user_prefs)}")
    print(border)
    print(row(widths.keys()))
    print(border.replace("-", "="))
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        reason_lines = []
        for reason in explanation.split("; "):
            reason_lines += textwrap.wrap(reason, widths["Why"], subsequent_indent="  ")
        first = [rank, song["title"][:22], song["artist"][:16], song["genre"][:10],
                 f"{score:.2f}", reason_lines[0]]
        print(row(first))
        for line in reason_lines[1:]:
            print(row(["", "", "", "", "", line]))
        print(border)


def main() -> None:
    parser = argparse.ArgumentParser(description="VibeFinder music recommender")
    parser.add_argument("--mode", default="genre-first", choices=list(STRATEGIES),
                        help="ranking strategy to use")
    parser.add_argument("--diverse", action="store_true",
                        help="penalize repeated artists and genres in the top results")
    parser.add_argument("--table", action="store_true", help="show results as a summary table")
    parser.add_argument("--profile", choices=list(ALL_PROFILES),
                        help="run one profile (default: the five main profiles)")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations")
    parser.add_argument("--list-modes", action="store_true", help="list the ranking modes")
    args = parser.parse_args()

    if args.list_modes:
        for name, strategy in STRATEGIES.items():
            print(f"{name:<15} {strategy.description}")
        return

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    if args.mode != "genre-first" or args.diverse:
        print(f"Mode: {args.mode} ({get_strategy(args.mode).description})"
              + (" | diversity penalty on" if args.diverse else ""))

    profiles = {args.profile: ALL_PROFILES[args.profile]} if args.profile else PROFILES
    for name, prefs in profiles.items():
        recs = recommend_songs(prefs, songs, k=args.k, mode=args.mode, diverse=args.diverse)
        if args.table:
            print_table(name, prefs, recs, args.mode, args.diverse)
        else:
            print_recommendations(name, prefs, recs)


if __name__ == "__main__":
    main()
