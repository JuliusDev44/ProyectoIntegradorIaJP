"""Reentrena los modelos y reproduce las evaluaciones emparejadas."""
import csv
from ecosistema import ROOT, SCENARIOS, MODES, World, forward, init_net, load_models, teacher
import numpy as np

FIELDS = ["escenario","politica","semilla","vida","alimento","capturas","energia_presa","energia_dep","primera_captura","vivas"]


def examples(rng, n, species):
    # Dos objetivos simulados por sensor. El más cercano reduce el exceso de vectores largos.
    vectors = rng.uniform(-1, 1, (n, 2, 2, 2))
    best = (vectors**2).sum(axis=-1).argmin(axis=2)
    chosen = vectors[np.arange(n)[:, None], np.arange(2), best]
    chosen[:n//3, 1] *= 0.25
    if species == "depredador":
        chosen[:, 1] = 0
    x = np.column_stack((chosen.reshape(n, 4), rng.random(n)))
    return x, teacher(x, species)


def train(width, species, index, log):
    rng = np.random.default_rng(410+index)
    x, labels = examples(rng, 4096, species)
    test, target = examples(rng, 1024, species)
    weights = init_net(width, 70+index)
    original = [w.copy() for w in weights]
    for epoch in range(61):
        logits = forward(test, weights)[-1]
        delta = np.sqrt(sum(((a-b)**2).sum() for a,b in zip(weights, original)))
        log.writerow([species,width,epoch,(logits.argmax(1)==target).mean(),delta])
        if epoch == 60:
            break
        for ids in np.array_split(rng.permutation(len(x)), 32):
            h,j,scores = forward(x[ids], weights)
            prob = np.exp(scores-scores.max(1, keepdims=True))
            prob /= prob.sum(1, keepdims=True)
            prob[np.arange(len(ids)),labels[ids]] -= 1
            grad = prob/len(ids)
            dj = (grad @ weights[4].T)*(j>0)
            dh = (dj @ weights[2].T)*(h>0)
            gradients = [x[ids].T@dh, dh.sum(0), h.T@dj, dj.sum(0), j.T@grad, grad.sum(0)]
            for w,g in zip(weights, gradients):
                w -= 0.07*g
    np.savez(ROOT/f"{species}_{width}.npz", *weights)


if __name__ == "__main__":
    with (ROOT/"entrenamiento.csv").open("w",newline="",encoding="utf-8") as f:
        log = csv.writer(f)
        log.writerow(["especie","ancho","epoca","exactitud_validacion","distancia_pesos_L2"])
        for width in (24,48):
            for i,s in enumerate(("presa","depredador")):
                train(width,s,i,log)
    with (ROOT/"episodios.csv").open("w",newline="",encoding="utf-8") as f:
        log = csv.writer(f)
        log.writerow(FIELDS)
        for mode in MODES:
            models = load_models(mode)
            for scenario in SCENARIOS:
                for seed in range(101,111):
                    world = World(scenario,seed,models)
                    while not world.done:
                        world.step()
                    log.writerow([scenario,mode,seed,*world.metrics()])
