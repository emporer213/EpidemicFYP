# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
import random
import pandas as pd
from EpidemicModel.DiseaseModel import *
from EpidemicModel.PopGen import EpiAgent


def compute_infections(model):
    agents_infected = [agent.health_state for agent in model.schedule.agents if agent.health_state ==
                       model.disease_model.health_state_dictionary.get("Infected")[1]]
    return len(agents_infected)


def compute_healthy(model):
    agents_healthy = [agent.health_state for agent in model.schedule.agents if (agent.health_state == model.disease) or
                      (agent.health_state == 3)]
    return len(agents_healthy)


class SimModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.running = True
        self.num_agents = N
        self.space = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.disease_model = SEIRModel(infection_radius=10)
        self.steps = 0

        # Create Agents
        for i in range(self.num_agents):
            a = EpiAgent(i, self)
            self.schedule.add(a)
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))

        patient_zero = random.choice(self.schedule.agents)
        patient_zero.health_state = self.disease_model.health_state_dictionary.get("Infected")[1]

        self.datacollector = DataCollector(
            model_reporters={"Rate of Infection": compute_infections, "Decline of Health": compute_healthy},
            agent_reporters={"Infected": "health_state", "Movement": "pos"}  # An agent attribute
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1

    def save_data(dataframe, file_name):
        writer = pd.ExcelWriter(file_name + '.xlsx')
        dataframe.to_excel(writer, 'DataFrame')
        writer.save()
