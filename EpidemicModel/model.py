# model.py
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
import random
import pandas as pd
from EpidemicModel.DiseaseModel import DiseaseModel


class EpiAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health_state = 1
        self.infected_step = self.model.steps

    def move(self):
        new_position_x = self.pos[0] + random.randrange(-8, 8)
        new_position_y = self.pos[1] + random.randrange(-8, 8)
        new_position = (new_position_x, new_position_y)
        self.model.space.move_agent(self, new_position)

    def infect(self):
        neighbours = self.model.space.get_neighbors(self.pos, self.model.disease_model.infection_radius,
                                                    include_center=False)
        if len(neighbours) > 1:
            for neighbour in neighbours:
                if neighbour.health_state == 1:
                    neighbour.health_state = 2
                    neighbour.infected_step = self.model.steps

    def step(self):
        self.move()
        if self.health_state == 2:
            self.infect()
            if self.infected_step > self.model.disease_model.infection_duration:
                self.health_state = 3


def compute_infections(model):
    agents_infected = [agent.health_state for agent in model.schedule.agents if agent.health_state == 2]
    return len(agents_infected)


def compute_healthy(model):
    agents_healthy = [agent.health_state for agent in model.schedule.agents if (agent.health_state == 1) or
                      (agent.health_state == 3)]
    return len(agents_healthy)


class SimModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.running = True
        self.num_agents = N
        self.space = ContinuousSpace(width, height, True)
        self.schedule = RandomActivation(self)
        self.disease_model = DiseaseModel()
        self.steps = 0

        # Create Agents
        for i in range(self.num_agents):
            a = EpiAgent(i, self)
            self.schedule.add(a)
            x = random.randrange(self.space.width)
            y = random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))

        patient_zero = random.choice(self.schedule.agents)
        patient_zero.health_state = 2

        self.datacollector = DataCollector(
            model_reporters={"Rate of Infection": compute_infections, "Decline of Health": compute_healthy},
            agent_reporters={"Infected": "health_state"}  # An agent attribute
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1

    def save_data(dataframe, file_name):
        writer = pd.ExcelWriter(file_name + '.xlsx')
        dataframe.to_excel(writer, 'DataFrame')
        writer.save()
