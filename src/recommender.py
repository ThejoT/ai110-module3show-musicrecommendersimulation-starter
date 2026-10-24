"""VibeFinder: a content-based music recommender.

score_song() judges one song against a user's preferences; recommend_songs() ranks the
whole catalog with it and returns the top k.

Ranking modes use the Strategy pattern: each RankingStrategy subclass sets its own weights,
and score_song()/recommend_songs() take a mode name ("genre-first", "mood-first",
"energy-focused") without any other code changing.
"""

import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

NUMERIC_FIELDS = {"id": int, "energy": float, "tempo_bpm": float, "valence": float,
                  "danceability": float, "acousticness": float, "popularity": int,
                  "instrumentalness": float, "speechiness": float}

# Diversity re-ranking penalties (per song already in the list).
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5


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
    # Advanced attributes (Challenge 1); defaults keep the starter tests working.
    popularity: int = 50             # 0-100
    release_decade: str = ""         # e.g. "2010s"
    mood_tags: str = ""              # semicolon-separated, e.g. "cozy;rainy;peaceful"
    instrumentalness: float = 0.0    # 0.0-1.0, 1.0 = no vocals
    speechiness: float = 0.0         # 0.0-1.0, higher = more spoken words/rap


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


# --------------------------------------------------------------------------- #
# Ranking strategies (Strategy pattern)
# --------------------------------------------------------------------------- #
class RankingStrategy:
    """Base strategy: scores a song using this strategy's weights."""

    name = "base"
    description = ""
    weights = {
        "genre": 2.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5,
        "decade": 0.5, "mood_tag": 0.25, "popularity": 0.5,
        "instrumental": 0.5, "spoken": 0.5,
    }

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Return (score, reasons) for one song; only preferences the user set are scored."""
        w = self.weights
        score, reasons = 0.0, []

        def add(points: float, reason: str) -> None:
            nonlocal score
            score += points
            reasons.append(f"{reason} (+{points:.2f})")

        if user_prefs.get("genre") and song["genre"].lower() == user_prefs["genre"].lower():
            add(w["genre"], f"genre match: {song['genre']}")
        if user_prefs.get("mood") and song["mood"].lower() == user_prefs["mood"].lower():
            add(w["mood"], f"mood match: {song['mood']}")
        if user_prefs.get("energy") is not None:
            gap = abs(song["energy"] - user_prefs["energy"])
            add(w["energy"] * (1 - gap),
                f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f}")
        if user_prefs.get("likes_acoustic") is not None:
            if user_prefs["likes_acoustic"]:
                add(w["acoustic"] * song["acousticness"],
                    f"acoustic sound, acousticness {song['acousticness']:.2f}")
            else:
                add(w["acoustic"] * (1 - song["acousticness"]),
                    f"electronic/produced sound, acousticness {song['acousticness']:.2f}")

        # ----- advanced attributes (only if the song and the user have them) -----
        if user_prefs.get("decade") and song.get("release_decade") == user_prefs["decade"]:
            add(w["decade"], f"from the {song['release_decade']}")
        if user_prefs.get("mood_tags") and song.get("mood_tags"):
            shared = [t for t in user_prefs["mood_tags"] if t in song["mood_tags"].split(";")]
            if shared:
                add(w["mood_tag"] * len(shared), f"mood tags: {', '.join(shared)}")
        if user_prefs.get("popularity") in ("mainstream", "niche") and "popularity" in song:
            share = song["popularity"] / 100
            if user_prefs["popularity"] == "mainstream":
                add(w["popularity"] * share, f"popular, {song['popularity']}/100")
            else:
                add(w["popularity"] * (1 - share), f"lesser-known, {song['popularity']}/100")
        if user_prefs.get("likes_instrumental") is not None and "instrumentalness" in song:
            value = song["instrumentalness"]
            if user_prefs["likes_instrumental"]:
                add(w["instrumental"] * value, f"instrumental, {value:.2f}")
            else:
                add(w["instrumental"] * (1 - value), f"has vocals, instrumentalness {value:.2f}")
        if user_prefs.get("likes_spoken_word") is not None and "speechiness" in song:
            value = song["speechiness"]
            if user_prefs["likes_spoken_word"]:
                add(w["spoken"] * value, f"spoken/rap vocals, speechiness {value:.2f}")
            else:
                add(w["spoken"] * (1 - value), f"little spoken word/rap, speechiness {value:.2f}")

        return round(score, 2), reasons


class GenreFirst(RankingStrategy):
    """Default: genre counts most, then energy, then mood."""

    name = "genre-first"
    description = "genre +2.0, mood +1.0, energy up to +1.5"


class MoodFirst(RankingStrategy):
    """Mood counts most: for listeners who care how a song feels more than its label."""

    name = "mood-first"
    description = "mood +2.5, genre +1.0, energy up to +1.5, mood tags +0.5 each"
    weights = {**RankingStrategy.weights, "genre": 1.0, "mood": 2.5, "mood_tag": 0.5}


class EnergyFocused(RankingStrategy):
    """Energy closeness counts most: for workouts, studying or sleep playlists."""

    name = "energy-focused"
    description = "energy up to +3.0, genre +0.5, mood +0.5"
    weights = {**RankingStrategy.weights, "genre": 0.5, "mood": 0.5, "energy": 3.0}


STRATEGIES: Dict[str, RankingStrategy] = {s.name: s() for s in (GenreFirst, MoodFirst, EnergyFocused)}
DEFAULT_MODE = "genre-first"


def get_strategy(mode: Optional[str]) -> RankingStrategy:
    """Look up a ranking strategy by name (default: genre-first)."""
    mode = mode or DEFAULT_MODE
    if mode not in STRATEGIES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(STRATEGIES)}")
    return STRATEGIES[mode]


# --------------------------------------------------------------------------- #
# OOP interface used by the starter tests
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Functional interface used by main.py
# --------------------------------------------------------------------------- #
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


def score_song(user_prefs: Dict, song: Dict, mode: Optional[str] = None) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences; return (score, list of reasons)."""
    return get_strategy(mode).score(user_prefs, song)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: Optional[str] = None,
                    diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort from highest to lowest, and return the top k as (song, score, explanation).

    With diverse=True, the list is built one song at a time and each candidate loses
    ARTIST_PENALTY for every chosen song by the same artist and GENRE_PENALTY for every
    chosen song in the same genre, so one artist or genre can't fill the whole list.
    """
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]

    if not diverse:
        # sorted() returns a new list and leaves `songs` untouched; ties keep catalog order.
        ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked]

    chosen: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)
    while remaining and len(chosen) < k:
        best = None
        for song, score, reasons in remaining:
            same_artist = sum(c[0]["artist"] == song["artist"] for c in chosen)
            same_genre = sum(c[0]["genre"] == song["genre"] for c in chosen)
            penalty = ARTIST_PENALTY * same_artist + GENRE_PENALTY * same_genre
            notes = list(reasons)
            if same_artist:
                notes.append(f"diversity: {song['artist']} already in list (-{ARTIST_PENALTY * same_artist:.2f})")
            if same_genre:
                notes.append(f"diversity: {same_genre} {song['genre']} song(s) already in list "
                             f"(-{GENRE_PENALTY * same_genre:.2f})")
            adjusted = round(score - penalty, 2)
            if best is None or adjusted > best[1]:
                best = (song, adjusted, "; ".join(notes))
        chosen.append(best)
        remaining = [r for r in remaining if r[0] is not best[0]]
    return chosen
