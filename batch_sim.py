# batch_sim.py
"""
Utility functions for running many simulations head‑less (no Pygame
window) so that experiments.py can sweep parameter values efficiently.

This module does **not** modify global `config` – every Boid is given its
own parameter copy so that parallel runs stay independent.
"""

import numpy as np
import config
from boids import Boid               # same Boid as in your main GUI version
from directed_boids import DirectedBoid
from hetero_boids import HeteroDirectedBoid

# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------
def default_param_dict():
    """Return a dict with the baseline values taken from config.py"""
    return {
        "MAX_SPEED":         config.MAX_SPEED,
        "NEIGHBOR_RADIUS":   config.NEIGHBOR_RADIUS,
        "SEPARATION_RADIUS": config.SEPARATION_RADIUS,
        "ALIGNMENT_WEIGHT":  config.ALIGNMENT_WEIGHT,
        "COHESION_WEIGHT":   config.COHESION_WEIGHT,
        "SEPARATION_WEIGHT": config.SEPARATION_WEIGHT,
    }

# ---------------------------------------------------------------------
# population initialisation
# ---------------------------------------------------------------------
def init_population(test_overrides, n_boids=config.NUM_BOIDS):
    """
    Create a list of boid objects.

    Parameters
    ----------
    test_overrides : dict
        Dict coming from experiments.py. **May only contain a single key**
        (the parameter we sweep), so we merge it with defaults first.
    n_boids : int
        Population size.

    Returns
    -------
    list[HeteroDirectedBoid]
    """
    # 1. build the complete parameter set for *selected* boids
    params = default_param_dict()
    params.update(test_overrides)      # override the one we are sweeping

    # 2. position everything in a random blob around the centre
    centre = np.array([config.WIDTH / 2, config.HEIGHT / 2], dtype=float)
    radius = 50
    boids = []
    for i in range(n_boids):
        angle = np.random.rand() * 2 * np.pi
        r     = np.random.rand() * radius
        pos   = centre + r * np.array([np.cos(angle), np.sin(angle)])

        # Mark 10 % as “selected” so they receive the modified params
        selected = (i < max(1, int(0.1 * n_boids)))
        if selected:
            b = HeteroDirectedBoid(pos, goal=centre, selected=True)
            # apply experimental parameters
            b.max_speed         = params["MAX_SPEED"]
            b.neighbor_radius   = params["NEIGHBOR_RADIUS"]
            b.separation_radius = params["SEPARATION_RADIUS"]
            b.ALIGNMENT_WEIGHT  = params["ALIGNMENT_WEIGHT"]
            b.COHESION_WEIGHT   = params["COHESION_WEIGHT"]
            b.SEPARATION_WEIGHT = params["SEPARATION_WEIGHT"]
        else:
            # ordinary boid with default settings
            b = HeteroDirectedBoid(pos, goal=centre, selected=False)
        boids.append(b)

    return boids

# ---------------------------------------------------------------------
# single‑run wrapper (used by experiments.py)
# ---------------------------------------------------------------------
def run_single_sim(overrides,
                   target=np.array([config.WIDTH*0.8, config.HEIGHT*0.8]),
                   dt=1/60,
                   end_tol=10,
                   max_steps=5000):
    """
    Run one simulation, return (delta_front, delta_radial) metrics.

    Parameters
    ----------
    overrides : dict
        Parameter(s) to change for *selected* boids.
    target : np.ndarray
        2‑D goal location.
    dt : float
        Timestep (s).
    end_tol : float
        Stop when group centroid is within this many pixels of `target`.
    max_steps : int
        Hard stop to avoid infinite loops.

    Returns
    -------
    tuple(float,float)
        Mean ΔFront, ΔRadial of selected group between 1 s after
        goal‑setting and arrival.
    """
    boids = init_population(overrides)

    # statistics containers
    sel_front = []
    sel_rad   = []

    # step loop
    for step in range(max_steps):
        # issue goal at t=0
        for b in boids:
            b.goal = target

        # update all
        for b in boids:
            b.update(boids)

        # centroid of full group
        positions = np.array([b.position for b in boids])
        centroid  = positions.mean(axis=0)

        # vector pointing group → goal = "forward" direction
        forward   = (target - centroid)
        forward_norm = np.linalg.norm(forward)
        if forward_norm < 1e-5:
            forward = np.array([0.0, 1.0])
        else:
            forward = forward / forward_norm

        # log after 1 s to allow settling
        if step * dt >= 1.0:
            for b in boids:
                if b.selected:
                    rel = b.position - centroid
                    # Front/back = projection on forward axis
                    front = np.dot(rel, forward)
                    # Radial distance = orthogonal magnitude
                    radial = np.linalg.norm(rel - front*forward)
                    sel_front.append(front)
                    sel_rad  .append(radial)

        # termination: centroid reached goal
        if np.linalg.norm(centroid - target) <= end_tol:
            break

    # convert to np.array to compute means
    sel_front = np.array(sel_front)
    sel_rad   = np.array(sel_rad)

    # Δ is difference vs. un‑selected mean; for now just return group means
    return sel_front.mean(), sel_rad.mean()
