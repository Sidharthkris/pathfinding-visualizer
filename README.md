# 🗺️ Pathfinding Algorithm Visualizer

A clean Python tool that runs **BFS**, **Dijkstra**, and **A\*** on a randomised obstacle grid and outputs a side-by-side visual comparison — including visited cells, optimal path, and per-algorithm performance stats.

![Comparison](pathfinding_comparison.png)

---

## ✨ Features

- **Three algorithms** implemented from scratch — BFS, Dijkstra, A\* (Manhattan heuristic)
- **Side-by-side PNG output** showing visited nodes, shortest path, and timing
- **Fully configurable** via CLI — grid size, obstacle density, random seed, algorithm selection
- **Zero heavyweight dependencies** — only NumPy and Matplotlib required
- Directly related to **agent navigation in simulation environments** (see [Emergency Evacuation Simulation](https://github.com/Sidharthkris/emergency-evacuation-simulation))

---

## 📊 Algorithm Comparison

| Algorithm | Optimal Path | Heuristic | Notes |
|-----------|:---:|:---------:|-------|
| BFS       | ✅ (unweighted) | ✗ | Explores layer by layer |
| Dijkstra  | ✅            | ✗ | Generalises to weighted graphs |
| A\*       | ✅            | ✓ Manhattan | Fewest nodes visited |

> On a 25×25 grid (seed=0, 22% obstacles): BFS visited **469** cells, Dijkstra **470**, A\* only **430** — reaching the same optimal path length of **49** steps in all three cases.

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run (default — all three algorithms, 20×20 grid)
```bash
python visualizer.py
```

### Options
```bash
python visualizer.py --size 30 --seed 7 --obstacles 0.25
python visualizer.py --algo astar           # single algorithm
python visualizer.py --output my_run.png    # custom output file
```

| Flag | Default | Description |
|------|---------|-------------|
| `--size` | `20` | Grid dimension (N×N) |
| `--seed` | `42` | Random seed for reproducibility |
| `--obstacles` | `0.28` | Obstacle density (0.0 – 1.0) |
| `--algo` | `all` | `bfs` · `dijkstra` · `astar` · `all` |
| `--output` | `pathfinding_comparison.png` | Output filename |

---

## 🧠 Implementation Notes

- **BFS** uses a `deque` for O(1) front-pops; guarantees shortest path on unweighted grids.
- **Dijkstra** uses a `heapq` min-heap; identical to BFS here (uniform edge weights) but extensible to weighted graphs.
- **A\*** adds a Manhattan distance heuristic `h(n) = |r − r_goal| + |c − c_goal|`, reducing the explored frontier significantly on open grids.
- Path reconstruction via shared `came_from` dict — O(path_length) traceback.

---

## 📁 Project Structure

```
pathfinding-visualizer/
├── visualizer.py               # All algorithms + rendering
├── pathfinding_comparison.png  # Sample output
├── requirements.txt
└── README.md
```

---

## 🔗 Related

This project complements my master's thesis on [emergency evacuation simulation](https://github.com/Sidharthkris/emergency-evacuation-simulation), where agent pathfinding under crowd pressure is a central challenge.

---

## 📄 License

MIT — free to use, adapt, and build upon.
