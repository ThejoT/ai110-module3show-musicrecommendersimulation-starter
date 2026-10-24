# 🎧 Model Card: VibeFinder 1.0

## 1. Model Name

**VibeFinder 1.0**, a content-based music recommender simulation.

---

## 2. Intended Use

VibeFinder suggests songs from a small catalog that fit a listener's stated taste: a favorite genre, a favorite mood, a target energy level and, optionally, whether they like acoustic sound. It returns the top 5 songs with a score and a plain-language reason for each one.

- **Assumptions about the user:** they can describe their taste with one genre and one mood, and their taste doesn't change with time of day or activity.
- **Intended use:** classroom exploration of how recommenders turn data into rankings, and where bias comes from.
- **Not intended for:** real users or a real product. It has no listening history, no learning from feedback, only 20 songs, and it shouldn't be used to judge which artists or genres are "better".

---

## 3. How the Model Works

Think of VibeFinder as a judge that gives every song points, then lines the songs up from most to fewest points.

- If the song's **genre** is your favorite genre, it gets **2 points**.
- If the song's **mood** is your favorite mood, it gets **1 point**.
- For **energy**, it gets up to **1.5 points** for being *close* to the energy you asked for. A song with exactly your energy gets all 1.5; a song that's far away gets fewer. Being louder or calmer than you wanted both cost points, so "higher" isn't automatically "better".
- If you said whether you like **acoustic** music, it gets up to **0.5 points** for matching that (lots of acoustic sound if you like it, very little if you don't).

With these four rules, the best possible score is 5 points. After every song is scored, VibeFinder sorts them and shows the top 5, along with the list of reasons that added up to each score.

**Optional extras (stretch features):**

- **More preferences:** a user can also ask for a release decade (+0.5), specific mood tags like "cozy" or "late-night" (+0.25 each), popular or lesser-known songs, instrumental or vocal songs, and more or less rap/spoken word (up to +0.5 each). These only count if the user sets them.
- **Three ranking modes:** *genre-first* (the rules above), *mood-first* (mood is worth 2.5 points and genre only 1) and *energy-focused* (energy closeness is worth up to 3 points, genre and mood only 0.5 each).
- **Diversity mode:** builds the list one song at a time and takes away points from songs whose artist or genre is already in the list (see section 6b).

**Changes from the starter:** the starter's functions were empty placeholders. I implemented CSV loading (turning the number columns into real numbers), the scoring rule above with a reason for every point, the ranking, and the `Recommender` class used by the tests. I also expanded the catalog from 10 to 20 songs, added 5 new attributes, three switchable ranking modes, the diversity penalty and a summary table.

---

## 4. Data

- **Size:** 20 songs in `data/songs.csv`. The starter had 10; I added 10 more to cover genres and moods that were missing.
- **Genres (17):** pop, indie pop, lofi, rock, ambient, jazz, synthwave, edm, hip-hop, classical, country, metal, r&b, folk, reggae, latin, blues.
- **Moods:** happy, chill, intense, relaxed, moody, focused, euphoric, confident, calm, nostalgic, angry, romantic, melancholy, sad.
- **Attributes per song:** title, artist, genre, mood, energy, tempo (BPM), valence, danceability and acousticness, plus 5 advanced attributes I added: popularity (0–100), release decade (1970s–2020s), mood tags (3 per song, e.g. "cozy;rainy;peaceful"), instrumentalness and speechiness.
- **What's missing:** lyrics, language, how songs actually sound beyond a few numbers, and any information about real listeners. The songs and artists are fictional, and the numbers were chosen by hand to be realistic. **Most genres have exactly one song**; only lofi (3) and pop (2) have more than one.

---

## 5. Strengths

- **Clear, specific tastes work well.** The *Chill Lofi* profile gets all three lofi songs first, in a sensible order (the calmest, most acoustic one on top), followed by ambient and jazz, which "feel" right as backups.
- **Energy closeness behaves like a vibe.** When the genre runs out, the fallback songs have similar energy, so a rock fan's list fills up with other loud songs (EDM, metal) rather than random ones.
- **Every score is explainable.** Each recommendation lists exactly which rules gave it points, so it's easy to see *why* a song ranked where it did.

---

## 6. Limitations and Bias

The biggest weakness I found is that **the genre weight is so large that genre wins arguments it shouldn't**. In the *Conflicted* profile (a blues fan who wants sad music at 0.9 energy), *Rainy Day Blues* comes first with 3.72 points even though its energy is 0.38, far from what the user asked for, because the genre and mood points (3.0 together) outweigh the full energy score (1.5). The same effect makes *Gym Hero*, an intense workout song, the #2 pick for a "happy pop" fan, purely because it's labeled pop. Because the catalog has only one song in most genres, the genre bonus also behaves like a **filter bubble**: a rock fan gets the one rock song and then nothing else from their genre, and a fan of a genre that isn't in the catalog (like K-pop) never gets the 2-point bonus at all, so their scores are capped at about half of what a pop or lofi fan can get. Exact text matching makes this worse: "indie pop" earns nothing for a "pop" fan, and "relaxed" earns nothing for a "chill" fan, even though people hear them as close.

---

## 6b. Diversity and Fairness

**The problem:** without any variety rule, a small catalog creates a **filter bubble**. The Chill Lofi listener gets three lofi songs, two of them by the same artist (LoRoom), and every lofi fan would hear the same few artists over and over. In a real app this is also unfair to artists: whoever already ranks well keeps getting recommended, and similar but less-matched artists rarely get a chance to be heard.

**What I implemented:** with `--diverse`, VibeFinder picks songs one at a time. Each remaining candidate loses **1.0 point for every song by the same artist** and **0.5 points for every song in the same genre** already in the list, and the penalty is shown in the reasons so the user can see it happened.

**The effect:** for Chill Lofi, *Focus Flow* (LoRoom's second song and the third lofi song) gets −2.00 and drops out, and *Pine Cabin Letters*, a folk song by a different artist with a similar calm, acoustic sound, enters the top 5. The list goes from **4 artists across 3 genres** (three lofi songs, two of them by LoRoom) to **5 different artists across 4 genres**, while the top two picks stay the same.

**How it improves fairness:** no single artist can take over a user's list, and songs from smaller genres that fit the same vibe get exposure they'd never get under pure score sorting. **The trade-off:** a user who really only wants lofi gets slightly less of what they asked for, which is why diversity is an option instead of the default.

---

## 7. Evaluation

I tested **five profiles** (full output in `outputs/profile_runs.txt` and the README): three normal ones (*High-Energy Pop*, *Chill Lofi*, *Deep Intense Rock*) and two adversarial ones designed to trick the scoring (*Conflicted: Sad but High-Energy* and *Unknown Genre: K-pop*). For each, I checked whether the top 5 matched my own sense of the music, and why.

**Comparing profiles:**

- **High-Energy Pop vs. Chill Lofi:** the pop list is all high-energy songs (0.76–0.93), while the lofi list shifts to calm, acoustic songs (0.28–0.42 energy, acousticness 0.71–0.92). This makes sense: their target energies are far apart (0.85 vs. 0.35) and they have opposite acoustic preferences, so almost no song scores well for both.
- **High-Energy Pop vs. Deep Intense Rock:** both lists are loud, and *Gym Hero* appears in both. Pop fans get it for the genre match; rock fans get it for the "intense" mood and 0.93 energy. One song can rank highly for very different reasons.
- **Chill Lofi vs. Deep Intense Rock:** they share no songs at all. The lofi list fills its gaps with ambient and jazz, while the rock list fills them with EDM and metal, which shows energy acting as the "vibe" once the genre runs out.
- **Deep Intense Rock vs. Conflicted (sad, high-energy):** both want 0.9 energy, so positions 2–5 are nearly the same loud songs (*Storm Runner*, *Gym Hero*, *Bassline Bloom*, *Iron Tide*). The only difference is the #1 song, which is decided by genre and mood, not energy.
- **High-Energy Pop vs. Unknown Genre (K-pop):** both like happy music, so they share *Sunrise City*, *Fuego Lento* and *Rooftop Lights*, but the K-pop fan never gets a genre match, so the top score drops from 4.87 to 2.41 and the order is decided almost entirely by small energy differences.

**Why does *Gym Hero* keep showing up for people who just want happy pop?** In plain terms: the system gives the biggest prize (2 points) just for being labeled "pop", and *Gym Hero* is one of only two pop songs. It also has high energy, which a high-energy pop fan asked for. The system doesn't know that a workout song *feels* very different from a sunny pop song, because it only checks the label, not the mood behind it. Across my five profiles, *Gym Hero*, *Sunrise City* and *Storm Runner* each appear 3 times, which shows how a small catalog keeps recycling the same few loud songs.

**Data experiment: weight shift.** I doubled the energy weight (1.5 → 3.0) and halved the genre weight (2.0 → 1.0). Results are in `outputs/weight_experiment.txt`:

- *High-Energy Pop:* the same five songs in the same order, but *Gym Hero*'s lead over *Fuego Lento* (a happy latin song with a perfect energy match) shrank from 1.08 points to 0.03, nearly a tie.
- *Chill Lofi:* *Spacewalk Thoughts* (ambient, **chill**) moved ahead of *Focus Flow* (lofi, **focused**), so mood and energy started to beat the genre label.
- *Conflicted:* *Rainy Day Blues* still won, because genre + mood is still worth more than the energy gap costs it.

The change made the results **different and a bit more "vibe-based", but not clearly more accurate**: it fixed some genre-label problems, but it also made genre fans more likely to get songs outside their genre. I kept the original weights as the default.

**Tests:** `pytest` runs 14 automated checks: the CSV loads 20 songs with numeric values and all 5 advanced attributes, every song gets a numeric score between 0 and 5 with reasons, a perfect match scores exactly 5.0, energy rewards closeness, recommendations are sorted, advanced preferences change the score only when set, mood-first removes *Gym Hero* from the happy-pop top 3, energy-focused puts a high-energy song first for the conflicted profile, and the diversity penalty limits repeated artists and genres.

**Ranking modes:** I ran the three modes on three profiles (`outputs/mode_comparison.txt`). Mood-first fixed the *Gym Hero* problem for happy-pop fans, and energy-focused fixed the conflicted blues profile. But each mode also creates new trade-offs: energy-focused still ranks *Gym Hero* second for pop fans, and mood-first lets non-lofi songs into a lofi fan's top 3.

---

## 8. Future Work

- **Similar-genre and similar-mood credit:** give partial points for related labels (e.g. "indie pop" for a pop fan, "relaxed" for a chill fan) instead of all-or-nothing matches.
- **Use more features:** tempo and valence are in the data but still not scored; valence could separate a happy pop song from an intense one like *Gym Hero* without changing modes.
- **Learn from feedback:** let users like or skip songs and adjust the weights, which is how real systems personalize.
- **A bigger, more balanced catalog** so every genre has several songs.

---

## 9. Personal Reflection

**Biggest learning moment:** seeing *Gym Hero*, a workout song, ranked #2 for a "happy pop" fan. Nothing in the code was broken; every point was added exactly as designed. The problem was in the *weights* I chose, which made one label (genre) more important than how a song actually feels. That showed me that a recommender can be "correct" and still give a bad recommendation.

**How AI helped, and when I double-checked:** I used Claude as an AI coding assistant to explain collaborative vs. content-based filtering, expand the dataset, implement the loading, scoring and ranking functions, and suggest adversarial profiles. I double-checked by running `python -m src.main` and doing the math by hand for the top songs. For example, *Sunrise City* for the pop profile is 2.0 + 1.0 + 1.5 × (1 − 0.03) + 0.5 × (1 − 0.18) = 4.87, which matches the output. I also checked that every comparison I wrote in this model card matches the saved output files instead of trusting a summary.

**What surprised me:** how much a few hand-picked rules already *feel* like a real recommendation. The Chill Lofi list honestly looks like a playlist I'd play while studying, even though the system only compares four numbers and two labels. It made me realize that "feeling personalized" and "understanding the music" are very different things.

**What I'd try next:** partial credit for similar genres and moods, using valence to tell happy and intense songs apart, and adding likes/skips so the weights adjust to each user instead of being fixed by me.
