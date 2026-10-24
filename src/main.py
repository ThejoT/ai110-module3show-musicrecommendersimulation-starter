"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

try:
    from src.recommender import load_songs, recommend_songs
except ImportError:  # also works when run as `python src/main.py`
    from recommender import load_songs, recommend_songs


def print_recommendations(name: str, user_prefs: dict, recommendations) -> None:
    """Print a profile and its ranked recommendations with scores and reasons."""
    prefs = ", ".join(f"{k}={v}" for k, v in user_prefs.items())
    print(f"\n=== {name} ===")
    print(f"Profile: {prefs}\n")
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{rank}. {song['title']} by {song['artist']} ({song['genre']}, {song['mood']})")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    print_recommendations("Default: Pop / Happy", user_prefs, recommend_songs(user_prefs, songs, k=5))


if __name__ == "__main__":
    main()
