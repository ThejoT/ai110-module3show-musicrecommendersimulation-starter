"""VibeFinder: a content-based music recommender.

score_song() judges one song against a user's preferences; recommend_songs() ranks the
whole catalog with it and returns the top k.
"""

import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

# Algorithm recipe weights (see README "Algorithm recipe").
GENRE_POINTS = 2.0
MOOD_POINTS = 1.0
ENERGY_POINTS = 1.5
ACOUSTIC_POINTS = 0.5

NUMERIC_FIELDS = {"id": int, "energy": float, "tempo_bpm": float, "valence": float,
                  "danceability": float, "acousticness": float}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert the profile into the user_prefs dictionary used by score_song()."""
        return {"genre": self.favorite_genre, "mood": self.favorite_mood,
                "energy": self.target_energy, "likes_acoustic": self.likes_acoustic}


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the k highest-scoring Song objects for this user."""
        prefs = user.to_prefs()
        ranked = sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation of how a song's score was calculated."""
        score, reasons = score_song(user.to_prefs(), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dictionaries, converting numeric columns to numbers."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field, cast in NUMERIC_FIELDS.items():
                if field in row:
                    row[field] = cast(row[field])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences; return (score, list of reasons)."""
    score = 0.0
    reasons: List[str] = []

    if user_prefs.get("genre") and song["genre"].lower() == user_prefs["genre"].lower():
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS:.1f})")

    if user_prefs.get("mood") and song["mood"].lower() == user_prefs["mood"].lower():
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS:.1f})")

    if user_prefs.get("energy") is not None:
        gap = abs(song["energy"] - user_prefs["energy"])
        points = ENERGY_POINTS * (1 - gap)
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f} "
                       f"(+{points:.2f})")

    if user_prefs.get("likes_acoustic") is not None:
        if user_prefs["likes_acoustic"]:
            points = ACOUSTIC_POINTS * song["acousticness"]
            label = "acoustic sound"
        else:
            points = ACOUSTIC_POINTS * (1 - song["acousticness"])
            label = "electronic/produced sound"
        score += points
        reasons.append(f"{label}, acousticness {song['acousticness']:.2f} (+{points:.2f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort from highest to lowest, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    # sorted() returns a new list and leaves `songs` untouched; ties keep catalog order.
    return sorted(scored, key=lambda item: item[1], reverse=True)[:k]
