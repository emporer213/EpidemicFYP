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
        self.current_final_dest = None
        self.home_time = 39
        self.work_time = 21
        self.type = 0
        self.action = "Travelling"

    def move(self):
            new_position = self.model.calculate_move(self.pos, self.current_final_dest, self.speed)
            self.model.space.move_agent(self, new_position)

    def step(self):
        distance = self.model.space.get_distance(self.pos, self.current_final_dest)

        if distance < 1:
            if self.current_final_dest == self.home:
                self.action = "Home"
                self.wait_timer = self.home_time
                self.current_final_dest = self.work
            else:
                self.wait_timer = self.work_time
                self.action = "Work"
                self.current_final_dest = self.home
        elif self.wait_timer != 0:
            self.wait_timer -= 1
        else:
            self.action = "Travelling"
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

    def is_at_work(self):
        if self.action == "Work":
            return True
        return False

    def is_at_home(self):
        if self.action == "Home":
            return True
        return False

    def is_traveling(self):
        if self.action == "Travelling":
            return True
        return False







