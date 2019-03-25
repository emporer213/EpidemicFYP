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
        self.transport_dest = None
        self.transport_final_dest = None
        self.change_station = None
        self.change_direction = 1
        self.current_final_dest = None
        self.home_time = 39
        self.work_time = 21
        self.type = 0
        self.state = "Travelling to Station"
        self.transport_dir = None
        self.train = None
        self.transport_line = None

    def move(self, dest):
            new_position = self.model.calculate_move(self.pos, dest, self.speed)
            self.model.space.move_agent(self, new_position)

    def step(self):
        self.check_infect_condition()

        if self.train is not None:
            if self.train.is_at_station():
                if self.train.current_station == self.transport_final_dest:
                    self.leave_train()
                    self.move(self.current_final_dest)
                    self.state = "Travelling"
                elif self.transport_final_dest.line != self.train.line:
                    connections = self.train.current_station.get_connections_for_line(self.transport_final_dest.line)
                    if len(connections) != 0:
                        self.leave_train()
                        self.transport_dir = connections[0].direction
                        self.transport_dest = connections[0].connection_from
                        self.transport_line = connections[0].line
                        if connections[0].connection_from.is_train_available(self.transport_dir,
                                                                             self.transport_final_dest.line):
                            self.train = connections[0].connection_from.get_available_train(self.transport_dir,
                                                                                            self.transport_final_dest.line)
                            self.train.passengers.append(self)
                            self.state = "On Train"
                        else:
                            self.state = "Waiting for train"
        elif self.state == "Travelling to Station" or self.state == "Waiting for train":
            if self.get_distance(self.pos, self.transport_dest.pos) < 1:
                self.state = "Waiting for train"
                if self.transport_dest.is_train_available(self.transport_dir, self.transport_line):
                    self.train = self.transport_dest.get_available_train(self.transport_dir, self.transport_line)
                    self.train.passengers.append(self)
                    self.state = "On Train"

        if self.get_distance(self.pos, self.current_final_dest) < 1:
            if self.current_final_dest == self.home:
                self.state = "Home"
                self.wait_timer = self.home_time
                self.current_final_dest = self.work
            else:
                self.wait_timer = self.work_time
                self.state = "Work"
                self.current_final_dest = self.home
        elif self.wait_timer != 0:
            self.wait_timer -= 1
        elif self.state == "Travelling to Station":
            self.move(self.transport_dest.pos)
        elif self.state == "Travelling":
            self.move(self.current_final_dest)

    def check_infect_condition(self):

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
        if self.state == "Work":
            return True
        return False

    def is_at_home(self):
        if self.state == "Home":
            return True
        return False

    def is_traveling(self):
        if self.state == "Travelling" or self.state == "Travelling to Station":
            return True
        return False

    def get_distance(self, pos1, pos2):
        return self.model.space.get_distance(pos1, pos2)

    def leave_train(self):
        self.train.passengers.remove(self)
        self.train = None

    def get_transport_goals(self):
        self.transport_dest = self.model.space.get_nearest_station(self.pos, 10, None)
        self.transport_line = self.transport_dest.line
        self.transport_final_dest = self.model.space.get_nearest_station(self.current_final_dest, 10, None)

        connections = self.transport_dest.connections

        if len(connections) > 1:
            distance_1 = self.get_distance(connections[0].connection_to.pos, self.current_final_dest)
            distance_2 = self.get_distance(connections[1].connection_to.pos, self.current_final_dest)

            if distance_1 < distance_2:
                self.transport_dir = connections[0].direction
            else:
                self.transport_dir = connections[1].direction
        else:
            self.transport_dir = connections[0].direction










