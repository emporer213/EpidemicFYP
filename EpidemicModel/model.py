# model.py
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random


class EpiAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health_state = 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def infect(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        susceptible_cellmates = [cellmate for cellmate in cellmates if cellmate.health_state == 1]
        if len(susceptible_cellmates) > 1:
            other = random.choice(susceptible_cellmates)
            other.health_state = 2

    def step(self):
        self.move()
        if self.health_state == 2:
            self.infect()


def compute_infections(model):
    agents_infected = [agent.health_state for agent in model.schedule.agents if agent.health_state == 2]
    return len(agents_infected)


def compute_healthy(model):
    agents_healthy = [agent.health_state for agent in model.schedule.agents if agent.health_state == 1]
    return len(agents_healthy)


class SimModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, width, height):
        self.running = True
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Create Agents
        for i in range(self.num_agents):
            a = EpiAgent(i, self)
            self.schedule.add(a)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        patient_zero = random.choice(self.schedule.agents)
        patient_zero.health_state = 2

        self.datacollector = DataCollector(
            model_reporters={"Rate of Infection": compute_infections, "Decline of Health": compute_healthy},
            agent_reporters={"Infected": "health_state"}  # An agent attribute
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
