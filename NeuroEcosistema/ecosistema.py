"""Motor compartido por la aplicación y los experimentos."""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
SCENARIOS = {"Abundancia": (24, 2), "Escasez": (5, 2), "Presión": (24, 5)}
HORIZON = 100
ACTIONS = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])
MODES = ["Reglas", "Inicial 24", "Red 24", "Red 48"]


def teacher(x, species):
    direction = x[:, :2].copy()
    if species == "presa":
        flee = np.linalg.norm(x[:, 2:4], axis=1) < 0.30
        direction[flee] = -x[flee, 2:4]
    return (direction @ ACTIONS.T).argmax(axis=1)


def init_net(width, seed):
    rng = np.random.default_rng(seed)
    layers = [5, width, 24, 4]
    params = []
    for a, b in zip(layers, layers[1:]):
        params.extend([rng.normal(0, np.sqrt(2 / a), (a, b)), np.zeros(b)])
    return params


def forward(x, weights):
    w, b, v, c, u, d = weights
    h = np.maximum(0, x @ w + b)
    j = np.maximum(0, h @ v + c)
    return h, j, j @ u + d


def load_models(mode):
    if mode == "Reglas":
        return {}
    width = int(mode.split()[-1])
    result = {}
    for i, species in enumerate(("presa", "depredador")):
        if mode.startswith("Inicial"):
            result[species] = init_net(width, 70+i)
        else:
            with np.load(ROOT / f"{species}_{width}.npz") as data:
                result[species] = [data[key] for key in data.files]
    return result


def nearest(points, targets):
    if len(targets) == 0:
        return np.ones((len(points), 2))
    delta = (targets[None, :, :] - points[:, None, :] + 20) % 40 - 20
    index = (delta**2).sum(axis=2).argmin(axis=1)
    return delta[np.arange(len(points)), index] / 20


class World:
    def __init__(self, scenario, seed, models):
        plants, predators = SCENARIOS[scenario]
        self.rng = np.random.default_rng(seed)
        self.models = models
        self.pos = [self.rng.uniform(0, 40, (12, 2)), self.rng.uniform(0, 40, (5, 2))[:predators]]
        self.food = self.rng.uniform(0, 40, (plants, 2))
        self.energy = [np.full(len(p), 45.) for p in self.pos]
        self.age = np.zeros(12)
        self.time = self.meals = self.kills = 0
        self.first = None
        self.trace = {}

    @property
    def done(self):
        return self.time >= HORIZON or not (self.energy[0] > 0).any()

    def step(self):
        if self.done:
            return
        self.time += 1
        moves = []
        for s, species in enumerate(("presa", "depredador")):
            ids = np.flatnonzero(self.energy[s] > 0)
            p = self.pos[s][ids]
            other = self.pos[1-s][self.energy[1-s] > 0]
            goal = nearest(p, self.food if s == 0 else other)
            danger = nearest(p, other) if s == 0 else np.zeros_like(goal)
            x = np.column_stack((goal, danger, self.energy[s][ids]/80))
            if species in self.models:
                scores = forward(x, self.models[species])[-1]
                actions = scores.argmax(axis=1)
            else:
                scores = None
                actions = teacher(x, species)
            if len(ids):
                self.trace[species] = (int(ids[0]), x[0].round(2), None if scores is None else scores[0].round(2), int(actions[0]))
            else:
                self.trace.pop(species, None)
            moves.append((ids, ACTIONS[actions] * (1.0 if s == 0 else 1.25)))
        for s, (ids, motion) in enumerate(moves):
            self.pos[s][ids] = (self.pos[s][ids] + motion) % 40
            self.energy[s][ids] -= 1
        self.age[moves[0][0]] += 1
        for i in moves[0][0]:
            dist = ((self.food - self.pos[0][i] + 20) % 40 - 20)**2
            j = dist.sum(axis=1).argmin()
            if dist[j].sum() <= 1.1**2:
                self.energy[0][i] = min(80, self.energy[0][i]+15)
                self.food[j] = self.rng.uniform(0, 40, 2)
                self.meals += 1
        for i in moves[1][0]:
            ids = np.flatnonzero(self.energy[0] > 0)
            if len(ids):
                dist = ((self.pos[0][ids] - self.pos[1][i] + 20) % 40 - 20)**2
                j = dist.sum(axis=1).argmin()
                if dist[j].sum() <= 1.4**2:
                    self.energy[0][ids[j]] = 0
                    self.energy[1][i] = min(80, self.energy[1][i]+24)
                    self.kills += 1
                    if self.first is None:
                        self.first = self.time

    def metrics(self):
        return [self.age.mean(), self.meals, self.kills, self.energy[0].mean(),
                self.energy[1].mean(), self.first, int((self.energy[0]>0).sum())]
