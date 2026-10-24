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


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Adversarial / edge-case profiles
    "Conflicted: Sad but High-Energy": {"genre": "blues", "mood": "sad", "energy": 0.9},
    "Unknown Genre: K-pop": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, recommend_songs(prefs, songs, k=5))


if __name__ == "__main__":
    main()
