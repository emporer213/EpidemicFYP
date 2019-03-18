# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
import random
import pandas as pd
from EpidemicModel.DiseaseModel import *
from EpidemicModel.PopGen import pop_gen
from EpidemicModel.Transport import *


def compute_infections(model):
    agents_infected = [agent.health_state for agent in model.schedule.agents if agent.health_state ==
                       model.disease_model.health_state_dictionary.get("Infected")[1]]
    return len(agents_infected)


def compute_healthy(model):
    agents_healthy = [agent.health_state for agent in model.schedule.agents if (agent.health_state ==
                     model.disease_model.health_state_dictionary.get("Recovered")[1]) or
                     (agent.health_state == model.disease_model.health_state_dictionary.get("Susceptible")[1])]
    return len(agents_healthy)


class SimModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height, train_line_num=5, wrk_location_num=20):
        self.work_loc_num = wrk_location_num
        self.home_loc_num = round(N/2)
        self.work_locations = []
        self.home_locations = []
        self.running = True
        self.num_agents = N
        self.space = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.disease_model = SEIRModel(infection_radius=10)
        self.steps = 0
        self.train_lines = []
        self.num_train_lines = train_line_num

        for l in range(0, self.work_loc_num):
            self.work_locations.append((random.randrange(self.space.width), random.randrange(self.space.height)))

        for lh in range(0, self.home_loc_num):
            self.home_locations.append((random.randrange(self.space.width), random.randrange(self.space.height)))

        stationlist = []
        for s in range(0, random.randrange(0, 10)):
            stationlist.append(Station())

        for t in range(self.num_train_lines):
            self.train_lines.append(TrainLine())
        pop_gen(N, self)

        '''
        # Create Agents
        for i in range(self.num_agents):
            a = EpiAgent(i, self)
            self.schedule.add(a)
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
        '''

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
