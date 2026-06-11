# Multi-Criteria Decision Analysis - Web Application

A Flask-based web application implementing four multi-criteria decision analysis (MCDA) methods:
**Borda Count**, **Nanson**, **ELECTRE I**, **TOPSIS**, and the interactive method **CBIM**.

Built as a university project for course **CSCB803 - Decision Support Systems** at New Bulgarian University.

---

## Features

| Endpoint | Method | Description |
|---|---|---|
| `POST /calculate` | Borda + Nanson | Group ranking from voter preferences |
| `POST /topsis` | TOPSIS | Rank alternatives by closeness to ideal solution |
| `POST /electre` | ELECTRE I | Outranking-based kernel selection |
| `POST /api/cbim` | CBIM | Interactive Chebyshev-based search |

---

## Tech Stack

- **Python 3.13** - Flask, NumPy
- **Frontend** - Jinja2 template (`templates/index.html`) with vanilla JS and CSS
- **Static assets** - `static/css/style.css`, `static/js/main.js`, example CSV files

---

## Project Structure

```
src/
|-- app.py                      # Flask routes and input validation
|-- requirements.txt
|-- algorithms/
|   |-- borda.py                # Borda count and winner selection
|   |-- nanson.py               # Nanson elimination procedure
|   |-- electre.py              # ELECTRE I (concordance/discordance)
|   |-- topsis.py               # TOPSIS (ideal solution proximity)
|   |-- weights.py              # Criteria weighting logic (New!)
|   --- cbim.py                 # CBIM (Chebyshev interactive method)
|-- templates/
|   --- index.html              # Jinja2 template - single-page UI
--- static/
    |-- css/
    |   --- style.css           # Main platform styles
    |-- js/
    |   --- main.js             # Frontend API calls and UI handlers
    |-- votes_example.csv       # Example input for Borda/Nanson
    |-- mca_example.csv         # Example input for TOPSIS/ELECTRE
    --- criteria_example.csv    # Example input for criteria text
```

---

## Setup

```bash
python -m venv .venv
```

**Windows:**
```bat
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Then install dependencies and run:

```bash
pip install -r requirements.txt
python app.py
```

The app runs at `http://127.0.0.1:5000`.

---

## API Reference

### `POST /calculate` - Borda + Nanson

Accepts a list of voter rankings, returns Borda scores, Nanson winner, and a paradox flag.

```json
{
  "votes": [
    ["A", "B", "C"],
    ["B", "C", "A"],
    ["C", "A", "B"]
  ]
}
```

**Response:**
```json
{
  "borda":  { "scores": {"A": 3, "B": 3, "C": 3}, "winner": "A" },
  "nanson": { "rounds": [...], "winner": "A" },
  "paradox": false
}
```

---

### `POST /topsis` - TOPSIS

```json
{
  "alternatives": [
    { "name": "Car A", "values": [250, 16, 12] },
    { "name": "Car B", "values": [200, 20,  9] }
  ],
  "weights":        [0.4, 0.4, 0.2],
  "criteria_types": ["max", "min", "max"]
}
```

**Response:**
```json
{
  "results": [
    { "rank": 1, "name": "Car A", "score": 0.62, "dist_best": 0.04, "dist_worst": 0.07, "values": [...] }
  ]
}
```

---

### `POST /electre` - ELECTRE I

```json
{
  "alternatives": [
    { "name": "A1", "values": [80, 7] },
    { "name": "A2", "values": [65, 9] }
  ],
  "weights":        [0.4, 0.6],
  "criteria_types": ["max", "max"],
  "c_threshold": 0.6,
  "d_threshold": 0.4
}
```

**Response:**
```json
{
  "names":       ["A1", "A2"],
  "weights":     [0.4, 0.6],
  "concordance": [[0.0, 0.6], [0.4, 0.0]],
  "discordance": [[0.0, 0.3], [0.5, 0.0]],
  "relations":   [{ "from": "A1", "to": "A2" }],
  "kernel":      ["A1"]
}
```

> Weights are normalised internally - you may pass `[4, 6]` or `[0.4, 0.6]`.

---

### `POST /api/cbim` - CBIM

```json
{
  "matrix":         [[80, 7], [65, 9], [83, 5]],
  "alternatives":   ["A1", "A2", "A3"],
  "criteria_types": ["max", "max"],
  "base_idx":       0,
  "preferences": [
    { "action": "improve", "delta": 5 },
    { "action": "worsen",  "delta": 1 }
  ],
  "l_count": 2
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    { "index": 2, "name": "A3", "values": [83, 5], "score": -3.0 }
  ]
}
```

---

## Algorithm Notes

**Borda** - assigns `m-1, m-2, …, 0` points per ranking; highest sum wins.

**Nanson** - iterative Borda elimination: at each round, all candidates tied for the *minimum* score are removed until one remains.

**ELECTRE I** - builds concordance and discordance matrices, applies threshold-based outranking, returns the non-dominated kernel.

**TOPSIS** - normalises the decision matrix, computes weighted distances to ideal best (A⁺) and ideal worst (A⁻), ranks by closeness coefficient `C* = d⁻ / (d⁺ + d⁻)`.

**CBIM** - Chebyshev scalarisation around a decision-maker-chosen base alternative; ranks alternatives by `S(i) = max_j(−diff_j)` on improvement criteria, subject to allowed-worsening constraints.

---

## Error Handling

All endpoints return `400` for invalid or missing input, `500` for unexpected errors. Error shape:

```json
{ "error": "Description of the problem" }
```

CBIM additionally wraps errors in `{ "success": false, "error": "..." }`.
