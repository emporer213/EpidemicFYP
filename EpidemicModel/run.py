# run.py
from EpidemicModel.model import *
from mesa.batchrunner import BatchRunner
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from EpidemicModel.server import server

from tqdm import tqdm

# Use this to run a simulation with visualization
server.port = 8521
server.launch()

# Uncomment this section and comment the above section to run multiple simulations with no visualisation.
'''model = SimModel(10000, 4000, 4000)
total_steps = 3000
for iteration in range(10):
    step_iterator = tqdm(range(total_steps))
    for steps in step_iterator:
        model.step()
    step_iterator.close()
    filename = "results" + str(iteration)
    model.save_data(filename)
    model = SimModel(10000, 4000, 4000)'''
