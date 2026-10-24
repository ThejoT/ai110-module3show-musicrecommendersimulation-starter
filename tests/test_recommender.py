from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ----- Functional API (load_songs / score_song / recommend_songs) ----------- #
from src.recommender import load_songs, recommend_songs, score_song  # noqa: E402

SONGS = load_songs("data/songs.csv")


def test_load_songs_reads_all_rows_with_numeric_values():
    assert len(SONGS) == 20
    assert isinstance(SONGS[0]["energy"], float)
    assert isinstance(SONGS[0]["id"], int)


def test_score_song_returns_number_and_reasons_for_every_song():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    for song in SONGS:
        score, reasons = score_song(prefs, song)
        assert isinstance(score, float) and 0 <= score <= 5.0
        assert reasons


def test_perfect_match_scores_highest_possible_points():
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.0}
    score, _ = score_song({"genre": "pop", "mood": "happy", "energy": 0.8,
                           "likes_acoustic": False}, song)
    assert score == 5.0


def test_energy_rewards_closeness_not_just_high_values():
    prefs = {"energy": 0.4}
    calm, _ = score_song(prefs, {"genre": "x", "mood": "x", "energy": 0.4, "acousticness": 0})
    intense, _ = score_song(prefs, {"genre": "x", "mood": "x", "energy": 0.95, "acousticness": 0})
    assert calm > intense


def test_recommend_songs_is_sorted_and_returns_k_results():
    recs = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.4}, SONGS, k=5)
    scores = [score for _, score, _ in recs]
    assert len(recs) == 5
    assert scores == sorted(scores, reverse=True)
    assert recs[0][0]["genre"] == "lofi"


# ----- Stretch features ----------------------------------------------------- #
import pytest  # noqa: E402

from src.recommender import STRATEGIES, get_strategy  # noqa: E402

POP = {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False}


def test_dataset_has_five_advanced_attributes():
    for field in ("popularity", "release_decade", "mood_tags", "instrumentalness", "speechiness"):
        assert all(field in song for song in SONGS)
    assert isinstance(SONGS[0]["popularity"], int)


def test_advanced_preferences_change_the_score():
    song = next(s for s in SONGS if s["title"] == "Midnight Coding")
    base, _ = score_song({"genre": "lofi"}, song)
    advanced, reasons = score_song({"genre": "lofi", "decade": "2020s",
                                    "mood_tags": ["late-night", "cozy"],
                                    "likes_instrumental": True}, song)
    assert advanced > base
    assert any("mood tags: late-night, cozy" in r for r in reasons)


def test_unset_advanced_preferences_are_ignored():
    song = SONGS[0]
    assert score_song(POP, song) == score_song({**POP, "decade": None}, song)


def test_there_are_three_switchable_modes():
    assert set(STRATEGIES) == {"genre-first", "mood-first", "energy-focused"}
    with pytest.raises(ValueError):
        get_strategy("random")


def test_mood_first_removes_gym_hero_from_happy_pop_top_three():
    genre_first = [s["title"] for s, _, _ in recommend_songs(POP, SONGS, 3)]
    mood_first = [s["title"] for s, _, _ in recommend_songs(POP, SONGS, 3, mode="mood-first")]
    assert "Gym Hero" in genre_first
    assert "Gym Hero" not in mood_first


def test_energy_focused_prefers_energy_over_genre_label():
    prefs = {"genre": "blues", "mood": "sad", "energy": 0.9}
    top = recommend_songs(prefs, SONGS, 1, mode="energy-focused")[0][0]
    assert top["energy"] >= 0.85


def test_diversity_penalty_limits_repeated_artists_and_genres():
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    plain = recommend_songs(prefs, SONGS, 5)
    diverse = recommend_songs(prefs, SONGS, 5, diverse=True)
    count = lambda recs, key, value: sum(s[key] == value for s, _, _ in recs)  # noqa: E731
    assert count(plain, "artist", "LoRoom") == 2 and count(diverse, "artist", "LoRoom") == 1
    assert count(diverse, "genre", "lofi") < count(plain, "genre", "lofi")
    assert any("diversity:" in why for _, _, why in diverse)
