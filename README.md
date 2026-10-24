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

### Five user profiles

`python -m src.main` runs three normal profiles and two adversarial ones (also saved in `outputs/profile_runs.txt`):

```
Loaded songs: 20

=== High-Energy Pop ===
Profile: genre=pop, mood=happy, energy=0.85, likes_acoustic=False

1. Sunrise City by Neon Echo (pop, happy)
   Score: 4.87
   - genre match: pop (+2.0)
   - mood match: happy (+1.0)
   - energy 0.82 vs target 0.85 (+1.46)
   - electronic/produced sound, acousticness 0.18 (+0.41)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 3.85
   - genre match: pop (+2.0)
   - energy 0.93 vs target 0.85 (+1.38)
   - electronic/produced sound, acousticness 0.05 (+0.47)
3. Fuego Lento by Mar y Sol (latin, happy)
   Score: 2.77
   - mood match: happy (+1.0)
   - energy 0.80 vs target 0.85 (+1.43)
   - electronic/produced sound, acousticness 0.30 (+0.35)
4. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 2.69
   - mood match: happy (+1.0)
   - energy 0.76 vs target 0.85 (+1.36)
   - electronic/produced sound, acousticness 0.35 (+0.33)
5. Storm Runner by Voltline (rock, intense)
   Score: 1.86
   - energy 0.91 vs target 0.85 (+1.41)
   - electronic/produced sound, acousticness 0.10 (+0.45)

=== Chill Lofi ===
Profile: genre=lofi, mood=chill, energy=0.35, likes_acoustic=True

1. Library Rain by Paper Lanterns (lofi, chill)
   Score: 4.93
   - genre match: lofi (+2.0)
   - mood match: chill (+1.0)
   - energy 0.35 vs target 0.35 (+1.50)
   - acoustic sound, acousticness 0.86 (+0.43)
2. Midnight Coding by LoRoom (lofi, chill)
   Score: 4.75
   - genre match: lofi (+2.0)
   - mood match: chill (+1.0)
   - energy 0.42 vs target 0.35 (+1.40)
   - acoustic sound, acousticness 0.71 (+0.35)
3. Focus Flow by LoRoom (lofi, focused)
   Score: 3.81
   - genre match: lofi (+2.0)
   - energy 0.40 vs target 0.35 (+1.42)
   - acoustic sound, acousticness 0.78 (+0.39)
4. Spacewalk Thoughts by Orbit Bloom (ambient, chill)
   Score: 2.85
   - mood match: chill (+1.0)
   - energy 0.28 vs target 0.35 (+1.40)
   - acoustic sound, acousticness 0.92 (+0.46)
5. Coffee Shop Stories by Slow Stereo (jazz, relaxed)
   Score: 1.92
   - energy 0.37 vs target 0.35 (+1.47)
   - acoustic sound, acousticness 0.89 (+0.45)

=== Deep Intense Rock ===
Profile: genre=rock, mood=intense, energy=0.9, likes_acoustic=False

1. Storm Runner by Voltline (rock, intense)
   Score: 4.93
   - genre match: rock (+2.0)
   - mood match: intense (+1.0)
   - energy 0.91 vs target 0.90 (+1.48)
   - electronic/produced sound, acousticness 0.10 (+0.45)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 2.93
   - mood match: intense (+1.0)
   - energy 0.93 vs target 0.90 (+1.46)
   - electronic/produced sound, acousticness 0.05 (+0.47)
3. Bassline Bloom by DJ Kestrel (edm, euphoric)
   Score: 1.91
   - energy 0.95 vs target 0.90 (+1.43)
   - electronic/produced sound, acousticness 0.03 (+0.48)
4. Iron Tide by Grave Signal (metal, angry)
   Score: 1.88
   - energy 0.97 vs target 0.90 (+1.40)
   - electronic/produced sound, acousticness 0.04 (+0.48)
5. Sunrise City by Neon Echo (pop, happy)
   Score: 1.79
   - energy 0.82 vs target 0.90 (+1.38)
   - electronic/produced sound, acousticness 0.18 (+0.41)

=== Conflicted: Sad but High-Energy ===
Profile: genre=blues, mood=sad, energy=0.9

1. Rainy Day Blues by Otis Gray (blues, sad)
   Score: 3.72
   - genre match: blues (+2.0)
   - mood match: sad (+1.0)
   - energy 0.38 vs target 0.90 (+0.72)
2. Storm Runner by Voltline (rock, intense)
   Score: 1.48
   - energy 0.91 vs target 0.90 (+1.48)
3. Gym Hero by Max Pulse (pop, intense)
   Score: 1.46
   - energy 0.93 vs target 0.90 (+1.46)
4. Bassline Bloom by DJ Kestrel (edm, euphoric)
   Score: 1.43
   - energy 0.95 vs target 0.90 (+1.43)
5. Iron Tide by Grave Signal (metal, angry)
   Score: 1.40
   - energy 0.97 vs target 0.90 (+1.40)

=== Unknown Genre: K-pop ===
Profile: genre=k-pop, mood=happy, energy=0.7

1. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 2.41
   - mood match: happy (+1.0)
   - energy 0.76 vs target 0.70 (+1.41)
2. Fuego Lento by Mar y Sol (latin, happy)
   Score: 2.35
   - mood match: happy (+1.0)
   - energy 0.80 vs target 0.70 (+1.35)
3. Sunrise City by Neon Echo (pop, happy)
   Score: 2.32
   - mood match: happy (+1.0)
   - energy 0.82 vs target 0.70 (+1.32)
4. Night Drive Loop by Neon Echo (synthwave, moody)
   Score: 1.42
   - energy 0.75 vs target 0.70 (+1.42)
5. Concrete Verses by Lyric Kade (hip-hop, confident)
   Score: 1.38
   - energy 0.78 vs target 0.70 (+1.38)
```

**What the differences show:**

- **High-Energy Pop vs. Chill Lofi:** the pop list is all high-energy songs (0.76–0.93), while the lofi list shifts to calm, acoustic tracks (0.28–0.42 energy, acousticness 0.71–0.92). Their target energies and acoustic preferences are opposite, so they share no songs.
- **High-Energy Pop vs. Deep Intense Rock:** both are loud, and *Gym Hero* appears in both: pop fans get it for the genre match, rock fans for the "intense" mood and 0.93 energy.
- **Chill Lofi vs. Deep Intense Rock:** once the genre runs out, the lofi list falls back to ambient and jazz, and the rock list falls back to EDM and metal. Energy acts as the "vibe".
- **Adversarial, Conflicted (sad blues at 0.9 energy):** *Rainy Day Blues* still wins with an energy of 0.38, because genre + mood (3.0) outweigh the whole energy score (1.5). The system can be "tricked" into ignoring a stated preference.
- **Adversarial, Unknown genre (K-pop):** with no genre match possible, the top score drops from 4.87 to 2.41, and the order is decided by tiny energy differences.

### Weight shift: energy ×2, genre ×0.5

(also saved in `outputs/weight_experiment.txt`)

```
Experiment: GENRE_POINTS 2.0 -> 1.0, ENERGY_POINTS 1.5 -> 3.0 (max possible score becomes 5.5 instead of 5.0)

High-Energy Pop
  Baseline                               | Experiment
  Sunrise City (4.87)                    | Sunrise City (5.32)
  Gym Hero (3.85)                        | Gym Hero (4.23)
  Fuego Lento (2.77)                     | Fuego Lento (4.20)
  Rooftop Lights (2.69)                  | Rooftop Lights (4.05)
  Storm Runner (1.86)                    | Storm Runner (3.27)

Conflicted: Sad but High-Energy
  Baseline                               | Experiment
  Rainy Day Blues (3.72)                 | Rainy Day Blues (3.44)
  Storm Runner (1.48)                    | Storm Runner (2.97)
  Gym Hero (1.46)                        | Gym Hero (2.91)
  Bassline Bloom (1.43)                  | Bassline Bloom (2.85)
  Iron Tide (1.40)                       | Iron Tide (2.79)

Chill Lofi
  Baseline                               | Experiment
  Library Rain (4.93)                    | Library Rain (5.43)
  Midnight Coding (4.75)                 | Midnight Coding (5.14)
  Focus Flow (3.81)                      | Spacewalk Thoughts (4.25)
  Spacewalk Thoughts (2.85)              | Focus Flow (4.24)
  Coffee Shop Stories (1.92)             | Coffee Shop Stories (3.38)
```

The results became **different, not clearly better**: *Gym Hero*'s lead over the happy latin song *Fuego Lento* shrank from 1.08 points to 0.03, and for the lofi fan the ambient *chill* song passed the lofi *focused* song. The conflicted blues fan still got the slow blues song first. I kept the original weights.

---

## Limitations and Risks

- **Tiny, uneven catalog:** 20 songs, and 15 of 17 genres have only one song, so genre fans quickly run out of matches.
- **Genre dominates:** a +2.0 label match beats mood and energy, which is why *Gym Hero* shows up for happy-pop fans.
- **Exact text matching:** "indie pop" doesn't count as pop, and "relaxed" doesn't count as chill.
- **No understanding of lyrics, language or listening history**, and no learning from feedback.
- **Unequal treatment of users:** fans of genres that aren't in the catalog can only ever reach about half the maximum score.

More detail is in the [model card](model_card.md).

---

## Reflection

Read the full [**Model Card**](model_card.md).

Building VibeFinder showed me that a recommender is really two decisions: a *scoring rule* that turns data into a number for one song, and a *ranking rule* that compares all the numbers. Real platforms do the same thing at a much bigger scale, with learned weights and listening history instead of my hand-picked points. What made the system feel smart was mostly the choice of features and weights, not complicated code.

It also showed me where unfairness creeps in without anyone intending it. Because genre is worth the most and most genres have only one song, the system quietly favors listeners whose taste matches what's already common in the catalog (pop, lofi), and gives everyone else weaker, more generic lists. In a real app, that same pattern could keep pushing already-popular genres and artists and make it harder for smaller ones to be discovered.
