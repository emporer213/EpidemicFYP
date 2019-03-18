from mesa import Agent
import random
import numpy as np
import traceback


class EpiAgent(Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, velocity, speed):
        super().__init__(unique_id, model)
        self.health_state = 1
        self.infected_step = self.model.steps
        self.velocity = velocity
        self.speed = speed
        self.wait_timer = 0
        self.home = None
        self.work = None
        self.current_dest = None
        self.home_time = 39
        self.work_time = 21

    def move(self):
            self.velocity = self.model.space.get_heading(self.pos, self.current_dest)
            self.velocity /= np.linalg.norm(self.velocity)
            new_position = self.pos + self.velocity * self.speed
            self.model.space.move_agent(self, new_position)

    def step(self):
        distance = self.model.space.get_distance(self.pos, self.current_dest)

        if distance < 1:
            if self.current_dest == self.home:
                self.wait_timer = self.home_time
                self.current_dest = self.work
            else:
                self.wait_timer = self.work_time
                self.current_dest = self.home
        elif self.wait_timer != 0:
            self.wait_timer -= 1
        else:
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
    agent_id = 1
    area_list = [Area((250, 250), 20, 50),
                 Area((50, 50), 30, 75),
                 Area((300, 50), 15, 25),
                 Area((400, 400), 15, 25),
                 Area((500, 600), 20, 50)]
    for al in area_list:
        pop_range = round((pop_size/100) * al.percentage)
        for i in range(pop_range):
            velocity = np.random.random(2) * 2 - 1
            a = EpiAgent(agent_id, model, velocity, 2)
            model.schedule.add(a)
            x = random.randrange(al.location[0] - al.location_radius, al.location[0] + al.location_radius)
            y = random.randrange(al.location[1] - al.location_radius, al.location[1] + al.location_radius)
            while (x - al.location[0]) ** 2 + (y - al.location[1]) ** 2 > al.location_radius ** 2:
                x = random.randrange(al.location[0] - al.location_radius, al.location[0] + al.location_radius)
                y = random.randrange(al.location[1] - al.location_radius, al.location[1] + al.location_radius)
            model.space.place_agent(a, (x, y))

            a.home = random.choice(model.home_locations)
            a.work = random.choice(model.work_locations)
            a.current_dest = a.work

            al.agents.append(a)
            agent_id += 1

    patient_zero = random.choice(model.schedule.agents)
    patient_zero.health_state = model.disease_model.health_state_dictionary.get("Infected")[1]







