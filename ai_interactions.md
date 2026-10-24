# AI Interactions Log

Stretch features attempted: **Additional Song Attributes via Agentic AI (SF8)**, **Multiple Ranking Modes and Design Patterns (SF10)**, plus the diversity penalty and the summary table (documented in the README and model card).

I used Claude as an AI coding agent working directly in my GitHub repo. It edited files, ran `python -m src.main` and `pytest` after each change, and committed each phase separately.

---

## Agentic Workflow (SF8)

**What task did you give the agent?**

Add at least 5 new meaningful attributes to the song dataset and update the scoring logic so it uses them consistently, without breaking the existing profiles or the starter tests.

**Prompts used:**

I gave Claude the project instructions and the grading rubric and asked it to complete the project step by step. The key requirement it worked from was:

```
Introduce 5 or more complex attributes to your dataset that are not currently present
in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood
Tags (e.g., "nostalgic," "aggressive," "euphoric"). Update both data/songs.csv and the
scoring logic in src/recommender.py so scoring accounts for the new attributes.
```

**What did the agent generate or change?**

| File | Change |
|------|--------|
| `data/songs.csv` | Added 5 columns to all 20 songs: `popularity` (0–100), `release_decade`, `mood_tags` (3 semicolon-separated tags), `instrumentalness` (0–1) and `speechiness` (0–1). |
| `src/recommender.py` | `load_songs()` converts the new numeric columns; `Song` got the 5 fields with defaults so the starter tests still construct songs the old way; scoring awards points for a decade match (+0.5), each shared mood tag (+0.25), popular vs. lesser-known (up to +0.5), instrumental vs. vocal (up to +0.5) and spoken word vs. not (up to +0.5), each with its own reason. |
| `src/main.py` | Two advanced profiles ("Late-Night Focus" and "Throwback Road Trip") that use every new preference, runnable with `--profile`. |
| `tests/test_recommender.py` | Tests that all 5 attributes load, that advanced preferences raise the score with the right reason, and that unset preferences change nothing. |

A key design decision: the new preferences are **optional**. A profile that doesn't set them scores exactly as before, so all the earlier evaluation results stay valid.

**What did you verify or fix manually?**

- **Earlier results didn't change:** I compared the five main profiles' output before and after the change. The only difference was formatting (`+2.0` became `+2.00`); every score and ranking was identical.
- **Math check by hand:** *Focus Flow* for the Late-Night Focus profile is 2.00 + 1.00 + 1.50 + 0.39 + 0.50 + 0.25 + 0.21 + 0.44 + 0.49 = 6.78, which matches the table output.
- **A misleading reason label was fixed:** for users who don't want rap/spoken word, the first version labeled songs "sung/melodic", so the instrumental *Focus Flow* was described as "sung". The label now says "little spoken word/rap", which is true for both sung and instrumental songs.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

The **Strategy pattern**. Each ranking mode is a strategy object that knows how to score a song, and the recommender doesn't care which one it's given.

**How did AI help you brainstorm or implement it?**

The project suggested trying a "simple Strategy pattern". Claude compared two options:

1. **One `score_song()` with `if mode == ...` branches.** This is quick, but every new mode makes the function longer, and the modes' weights get scattered through the code.
2. **A `RankingStrategy` base class that holds the scoring logic and a `weights` dictionary, with one small subclass per mode.** Each mode only overrides the weights it changes.

Option 2 was chosen because the modes differ only in *how much* each rule counts, not in *which* rules exist, so the weights dictionary is the only thing a subclass needs to change. Claude then suggested the three modes based on the weaknesses found in my evaluation: **mood-first** to fix *Gym Hero* showing up for happy-pop fans, and **energy-focused** to fix the conflicted "sad but high-energy" profile, where a slow blues song won.

**How does the pattern appear in your final code?**

- `RankingStrategy.score()` in `src/recommender.py`: the shared scoring logic, reading every point value from `self.weights`.
- `GenreFirst`, `MoodFirst`, `EnergyFocused`: subclasses that set `name`, `description` and their own `weights`.
- `STRATEGIES` and `get_strategy()`: a registry that looks up a mode by name and raises a clear error for unknown names.
- `score_song(..., mode=...)` and `recommend_songs(..., mode=...)` take the mode name, and `main.py` exposes it as `--mode` (`python -m src.main --list-modes` shows all three).

Adding a fourth mode means writing one subclass and adding it to `STRATEGIES`; nothing else changes. Results for each mode are in `outputs/mode_comparison.txt` and the README.
