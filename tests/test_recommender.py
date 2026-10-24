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
