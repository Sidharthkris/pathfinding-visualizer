"""
Pathfinding Algorithm Visualizer
=================================
Visualizes A*, Dijkstra, and BFS on a grid with obstacles.
Outputs a side-by-side comparison PNG.

Usage:
    python visualizer.py                   # default 20x20 grid, random obstacles
    python visualizer.py --size 30 --seed 99
    python visualizer.py --algo astar      # run only one algorithm
"""

import argparse
import heapq
import random
import time
from collections import deque

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    "empty":    "#1e1e2e",
    "wall":     "#45475a",
    "start":    "#a6e3a1",
    "end":      "#f38ba8",
    "visited":  "#313244",
    "frontier": "#89b4fa",
    "path":     "#cba6f7",
    "text":     "#cdd6f4",
    "bg":       "#11111b",
}


# ── Grid helpers ──────────────────────────────────────────────────────────────

def make_grid(size: int, obstacle_rate: float, seed: int) -> np.ndarray:
    """Return a 2-D binary grid: 0 = passable, 1 = wall."""
    rng = random.Random(seed)
    grid = np.zeros((size, size), dtype=int)
    for r in range(size):
        for c in range(size):
            if rng.random() < obstacle_rate:
                grid[r][c] = 1
    # Always keep start / end clear
    grid[0][0] = 0
    grid[size - 1][size - 1] = 0
    return grid


def neighbours(r, c, size):
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            yield nr, nc


def reconstruct(came_from, start, end):
    path, node = [], end
    while node != start:
        path.append(node)
        node = came_from[node]
    path.append(start)
    return list(reversed(path))


# ── Algorithms ────────────────────────────────────────────────────────────────

def bfs(grid):
    size = grid.shape[0]
    start, end = (0, 0), (size - 1, size - 1)
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    visit_order = []

    t0 = time.perf_counter()
    while queue:
        r, c = queue.popleft()
        visit_order.append((r, c))
        if (r, c) == end:
            break
        for nr, nc in neighbours(r, c, size):
            if (nr, nc) not in visited and grid[nr][nc] == 0:
                visited.add((nr, nc))
                came_from[(nr, nc)] = (r, c)
                queue.append((nr, nc))
    elapsed = time.perf_counter() - t0

    path = reconstruct(came_from, start, end) if end in came_from else []
    return visit_order, path, elapsed


def dijkstra(grid):
    size = grid.shape[0]
    start, end = (0, 0), (size - 1, size - 1)
    dist = {start: 0}
    came_from = {start: None}
    pq = [(0, start)]
    visit_order = []

    t0 = time.perf_counter()
    while pq:
        d, (r, c) = heapq.heappop(pq)
        if d > dist.get((r, c), float("inf")):
            continue
        visit_order.append((r, c))
        if (r, c) == end:
            break
        for nr, nc in neighbours(r, c, size):
            if grid[nr][nc] == 0:
                nd = d + 1
                if nd < dist.get((nr, nc), float("inf")):
                    dist[(nr, nc)] = nd
                    came_from[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (nd, (nr, nc)))
    elapsed = time.perf_counter() - t0

    path = reconstruct(came_from, start, end) if end in came_from else []
    return visit_order, path, elapsed


def astar(grid):
    size = grid.shape[0]
    start, end = (0, 0), (size - 1, size - 1)

    def h(r, c):  # Manhattan heuristic
        return abs(r - end[0]) + abs(c - end[1])

    g = {start: 0}
    came_from = {start: None}
    pq = [(h(*start), 0, start)]
    visit_order = []

    t0 = time.perf_counter()
    while pq:
        _, cost, (r, c) = heapq.heappop(pq)
        if cost > g.get((r, c), float("inf")):
            continue
        visit_order.append((r, c))
        if (r, c) == end:
            break
        for nr, nc in neighbours(r, c, size):
            if grid[nr][nc] == 0:
                ng = cost + 1
                if ng < g.get((nr, nc), float("inf")):
                    g[(nr, nc)] = ng
                    came_from[(nr, nc)] = (r, c)
                    heapq.heappush(pq, (ng + h(nr, nc), ng, (nr, nc)))
    elapsed = time.perf_counter() - t0

    path = reconstruct(came_from, start, end) if end in came_from else []
    return visit_order, path, elapsed


# ── Rendering ─────────────────────────────────────────────────────────────────

def grid_to_rgb(grid, visit_order, path, size):
    """Build an RGB image array for one result."""
    img = np.full((size, size, 3), _hex(C["empty"]), dtype=float)

    # walls
    for r in range(size):
        for c in range(size):
            if grid[r][c] == 1:
                img[r][c] = _hex(C["wall"])

    # visited cells
    for r, c in visit_order:
        if grid[r][c] == 0:
            img[r][c] = _hex(C["visited"])

    # path
    for r, c in path:
        img[r][c] = _hex(C["path"])

    # start / end
    img[0][0] = _hex(C["start"])
    img[size - 1][size - 1] = _hex(C["end"])

    return img


def _hex(h):
    h = h.lstrip("#")
    return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]


def render(grid, results, output_path="pathfinding_comparison.png"):
    size = grid.shape[0]
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 6.5))
    fig.patch.set_facecolor(C["bg"])
    if n == 1:
        axes = [axes]

    for ax, (label, visit_order, path, elapsed) in zip(axes, results):
        img = grid_to_rgb(grid, visit_order, path, size)
        ax.imshow(img, interpolation="nearest", aspect="equal")
        ax.set_title(
            f"{label}",
            color=C["text"], fontsize=14, fontweight="bold", pad=10
        )
        stats = (
            f"Visited: {len(visit_order)}   "
            f"Path: {len(path) if path else '✗'}   "
            f"Time: {elapsed*1000:.2f} ms"
        )
        ax.set_xlabel(stats, color="#a6adc8", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    # Legend
    legend_items = [
        mpatches.Patch(color=C["start"],    label="Start"),
        mpatches.Patch(color=C["end"],      label="End"),
        mpatches.Patch(color=C["wall"],     label="Wall"),
        mpatches.Patch(color=C["visited"],  label="Visited"),
        mpatches.Patch(color=C["path"],     label="Path"),
    ]
    fig.legend(
        handles=legend_items,
        loc="lower center",
        ncol=5,
        frameon=False,
        labelcolor=C["text"],
        fontsize=9,
        bbox_to_anchor=(0.5, 0.01),
    )

    fig.suptitle(
        "Pathfinding Algorithm Comparison",
        color=C["text"], fontsize=16, fontweight="bold", y=1.01
    )
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=C["bg"])
    print(f"[✓] Saved → {output_path}")
    plt.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

ALGO_MAP = {"bfs": bfs, "dijkstra": dijkstra, "astar": astar}
LABELS   = {"bfs": "BFS", "dijkstra": "Dijkstra", "astar": "A*"}

def main():
    parser = argparse.ArgumentParser(description="Pathfinding Algorithm Visualizer")
    parser.add_argument("--size",          type=int,   default=20,    help="Grid size (NxN)")
    parser.add_argument("--seed",          type=int,   default=42,    help="Random seed")
    parser.add_argument("--obstacles",     type=float, default=0.28,  help="Obstacle density 0–1")
    parser.add_argument("--algo",          type=str,   default="all", help="bfs | dijkstra | astar | all")
    parser.add_argument("--output",        type=str,   default="pathfinding_comparison.png")
    args = parser.parse_args()

    grid = make_grid(args.size, args.obstacles, args.seed)

    algos = list(ALGO_MAP.keys()) if args.algo == "all" else [args.algo]
    results = []
    for name in algos:
        visit_order, path, elapsed = ALGO_MAP[name](grid)
        found = "found" if path else "no path"
        print(f"[{LABELS[name]:>8}]  visited={len(visit_order):>4}  path={len(path):>3}  {elapsed*1000:.2f}ms  ({found})")
        results.append((LABELS[name], visit_order, path, elapsed))

    render(grid, results, args.output)


if __name__ == "__main__":
    main()
