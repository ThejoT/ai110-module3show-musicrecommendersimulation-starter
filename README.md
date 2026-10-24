# 🎵 Music Recommender Simulation

## Project Summary

**VibeFinder 1.0** is a small, content-based music recommender. It reads a catalog of 20 songs from `data/songs.csv`, compares each song with a user's "taste profile" (favorite genre, favorite mood, target energy and whether they like acoustic sound), gives every song a score with a list of human-readable reasons, and returns the top matches. It's a simulation of how apps like Spotify decide what to play next, built to show how data becomes a recommendation and where that process can be biased.

---

## How The System Works

### How real-world recommenders work

Platforms like Spotify and YouTube combine two main approaches. **Collaborative filtering** uses *other people's behavior*: if many listeners who liked songs A and B also liked song C, then someone who likes A and B is likely to enjoy C, even if the system knows nothing about how C sounds. **Content-based filtering** uses *the song's own attributes*, such as genre, mood, tempo, energy, danceability and acousticness (Spotify computes audio features like these for every track), and recommends songs whose attributes are close to what the user already likes.

Both rely on three different kinds of information, which are easy to mix up:

1. **Input data (about the items):** the catalog and its features, for example `genre = lofi`, `energy = 0.42`, `tempo_bpm = 78`.
2. **User preferences (about the person):** either stated explicitly (a chosen genre) or learned implicitly from history: likes, skips, replays, playlist adds and listening time. A skip within a few seconds is a strong negative signal; adding a song to a playlist is a strong positive one.
3. **Ranking and selection (the decision):** a model scores every candidate song for this user, sorts the candidates, and selects the top few. Real systems then re-rank for business and quality goals, such as mixing in new releases, avoiding five songs by the same artist in a row, or exploring something new.

Real systems learn their scoring from millions of interactions. VibeFinder is a **content-based** system with a **hand-written scoring rule**, so every decision can be explained.

### What VibeFinder uses

**`Song` features** (from `data/songs.csv`):

| Feature | Type | Used in scoring? |
|---------|------|------------------|
| `genre` | text | ✅ exact match |
| `mood` | text | ✅ exact match |
| `energy` | 0.0–1.0 | ✅ closeness to the user's target |
| `acousticness` | 0.0–1.0 | ✅ if the user has an acoustic preference |
| `title`, `artist`, `id` | text / int | for display |
| `tempo_bpm`, `valence`, `danceability` | numbers | loaded, not scored in the base recipe |

**`UserProfile` / `user_prefs`:** `genre` (favorite genre), `mood` (favorite mood), `energy` (target energy, 0–1) and `likes_acoustic` (optional, True/False).

### Algorithm recipe

**Scoring rule (one song):**

| Rule | Points |
|------|--------|
| Genre matches the user's favorite genre | **+2.0** |
| Mood matches the user's favorite mood | **+1.0** |
| Energy closeness: `1.5 × (1 − |song energy − target energy|)` | **0 to +1.5** |
| Acoustic preference: `0.5 × acousticness` if they like acoustic, `0.5 × (1 − acousticness)` if they don't | **0 to +0.5** |

The maximum possible score is **5.0**. Energy uses *closeness* rather than "higher is better": a user who wants 0.4 energy gets the most points from a 0.4 song, and points shrink evenly as the gap grows, so both very calm and very intense songs are penalized for a mid-energy listener.

**Ranking rule (the whole list):** score every song in the catalog with the scoring rule, sort from highest to lowest score, and return the top *k* (5 by default). A scoring rule alone can only judge one song in isolation; you need the ranking rule to compare all of them and decide which ones the user actually sees.

```
User prefs ──► for each of the 20 songs: score_song() ──► (score, reasons) ──► sort high→low ──► top k
```

### Biases I expect

- **Genre dominates.** A genre match (+2.0) is worth more than a perfect mood match plus near-perfect energy, so a great song in a neighboring genre (e.g. "indie pop" for a "pop" fan) can lose to a mediocre song in the exact genre.
- **Exact text matching is brittle.** "indie pop" ≠ "pop" and "chill" ≠ "relaxed", even though people hear them as close.
- **Uneven catalog.** Some genres have three songs (lofi) and many have one, so fans of rare genres will quickly run out of genre matches.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   source .venv/Scripts/activate  # Git Bash on Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default "pop / happy" profile:

```
Loaded songs: 20

=== Default: Pop / Happy ===
Profile: genre=pop, mood=happy, energy=0.8

1. Sunrise City by Neon Echo (pop, happy)
   Score: 4.47
   - genre match: pop (+2.0)
   - mood match: happy (+1.0)
   - energy 0.82 vs target 0.80 (+1.47)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 3.30
   - genre match: pop (+2.0)
   - energy 0.93 vs target 0.80 (+1.30)
3. Fuego Lento by Mar y Sol (latin, happy)
   Score: 2.50
   - mood match: happy (+1.0)
   - energy 0.80 vs target 0.80 (+1.50)
4. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 2.44
   - mood match: happy (+1.0)
   - energy 0.76 vs target 0.80 (+1.44)
5. Concrete Verses by Lyric Kade (hip-hop, confident)
   Score: 1.47
   - energy 0.78 vs target 0.80 (+1.47)
```

These results match my intuition: *Sunrise City* is the only song that is pop **and** happy **and** close to 0.8 energy, so it wins clearly. *Gym Hero* comes second only because of the +2.0 genre match, even though its mood is "intense", which is the first sign that genre carries a lot of weight.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



