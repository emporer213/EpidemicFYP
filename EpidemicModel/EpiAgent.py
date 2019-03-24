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
        self.state = "Travelling"
        self.transport_dir = None
        self.train = None

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
                if self.train.current_station == self.change_station:
                    self.leave_train()
                    if self.change_station.is_train_available(self.transport_dir):
                        self.train = self.change_station.get_available_train(self.transport_dir)
                        self.train.passengers.append(self)
                        self.state = "On Train"
        elif self.state == "Travelling to Station":
            if self.get_distance(self.pos, self.transport_dest.pos) < 1:
                if self.transport_dest.is_train_available(self.transport_dir):
                    self.train = self.transport_dest.get_available_train(self.transport_dir)
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
        else:
            self.state = "Travelling to Station"
            self.get_transport_route()
            self.move(self.transport_dest.pos)

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

    def get_transport_route(self):
        nearest_station = self.model.space.get_nearest_station(self.pos, 10, None)
        self.transport_dest = nearest_station
        nearest_final_station = self.model.space.get_nearest_station(self.current_final_dest, 20, None)
        self.transport_final_dest = nearest_final_station

        self.get_change_station(nearest_station)

    '''  if nearest_station.next_station is not None and nearest_station.prev_station is not None:
            dist_to_final_next = self.model.space.get_distance(nearest_station.next_station.pos,
                                                               self.current_final_dest)
            dist_to_final_prev = self.model.space.get_distance(nearest_station.prev_station.pos,
                                                               self.current_final_dest)
            if dist_to_final_next < dist_to_final_prev:
                self.transport_dir = 1
            else:
                self.transport_dir = 0
        elif nearest_station.prev_station is not None:
            self.transport_dir = 0
        else:
            self.transport_dir = 1

        if self.transport_dir == 1:
            current_station = nearest_station.next_station
            prev_distance = self.model.space.get_distance(current_station.pos, self.current_final_dest)
            while current_station.next_station is not None:
                next_station_distance = self.model.space.get_distance(current_station.next_station.pos,
                                                                      self.current_final_dest)
                if next_station_distance < prev_distance:
                    current_station = current_station.next_station
                else:
                    break

        if self.transport_dir == 0:
            current_station = nearest_station.prev_station
            prev_distance = self.model.space.get_distance(current_station.pos, self.current_final_dest)
            while current_station.prev_station is not None:
                prev_station_distance = self.model.space.get_distance(current_station.prev_station.pos,
                                                                      self.current_final_dest)
                if prev_station_distance < prev_distance:
                    current_station = current_station.prev_station
                else:
                    break

        self.transport_final_dest = current_station'''

    def get_change_station(self, nearest_station):
        connections_forward = nearest_station.get_connections_for_line(1, nearest_station.line)
        connections_backward = nearest_station.get_connections_for_line(0, nearest_station.line)

        if len(connections_forward) and len(connections_backward) == 1:
            if (self.get_distance(connections_forward[0].connection_to.pos, self.current_final_dest)) < \
                    (self.get_distance(connections_backward[0].connection_to.pos, self.current_final_dest)):

                self.set_connections_forward(connections_forward)
            else:
                self.set_connections_backward(connections_backward)
        elif len(connections_forward) == 0:
            self.set_connections_backward(connections_backward)
        else:
            self.set_connections_forward(connections_forward)

    def set_connections_forward(self, connections):
        self.transport_dir = 1

        change_connection = self.traverse_connections(connections[0].connection_to,
                                                      self.transport_dest.line, self.transport_final_dest.line, 1)
        self.change_station = change_connection.connection_from
        self.change_direction = change_connection.direction

    def set_connections_backward(self, connections):
        self.transport_dir = 0
        change_connection = self.traverse_connections(connections[0].connection_to,
                                                      self.transport_dest.line, self.transport_final_dest.line, 0)
        self.change_station = change_connection.connection_from
        self.change_direction = change_connection.direction

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

    def traverse_connections(self, start_station, current_line, goal_line, direction_to_traverse):
        connections = start_station.get_connections(direction_to_traverse)
        if len(connections) == 0:
            if direction_to_traverse == 1:
                direction_to_traverse = 0
                connections = start_station.get_connections(direction_to_traverse)
            else:
                direction_to_traverse = 1
                connections = start_station.get_connections(direction_to_traverse)

        for connection in connections:
            if connection.line == goal_line:
                return connection
            elif connection.connection_to == self.transport_final_dest:
                return connection
            elif connection.line == current_line:
                start_station = connection.connection_to

        return self.traverse_connections(start_station, current_line, goal_line, direction_to_traverse)






