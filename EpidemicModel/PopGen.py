from mesa import Agent
import random


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

    def step(self):
        self.move()
        if self.health_state == self.model.disease_model.health_state_dictionary.get("Infected")[1]:
            self.model.disease_model.infect(self)
            infection_duration = self.model.disease_model.health_state_dictionary.get("Infected")[0]
            if (self.model.steps - self.infected_step) > infection_duration:
                self.health_state = self.model.disease_model.health_state_dictionary.get("Recovered")[1]

        elif self.health_state == self.model.disease_model.health_state_dictionary.get("Exposed")[1]:
                exposed_duration = self.model.disease_model.health_state_dictionary.get("Exposed")[0]
                if (self.model.steps - self.exposed_step) > exposed_duration:
                    self.health_state = self.model.disease_model.health_state_dictionary.get("Infected")[1]
                    self.infected_step = self.model.steps


class Area:

    def __init__(self, location, percentage, location_radius):
        self.location = location
        self.percentage = percentage
        self.location_radius = location_radius
        self.agents = []


def pop_gen(pop_size, model):
    agent_count = 0
    area_list = [Area((200, 800), 20, 100),
                 Area((800, 200), 30, 200),
                 Area((800, 800), 15, 50),
                 Area((100, 200), 15, 50),
                 Area((500, 500), 20, 100)]

    for i in range(pop_size):
        a = EpiAgent(i, model)
        model.schedule.add(a)
        /,,,




