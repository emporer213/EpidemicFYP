import numpy as np
from mesa import Agent
import random


class TrainLine:

    def __init__(self, station_list, station_limit=7):
        self.station_list = station_list
        self.station_limit = station_limit


class Train(Agent):

    def __init__(self, current_station, model, speed, unique_id, line):
        super().__init__(unique_id, model)
        self.passengers = []
        self.current_station = current_station
        self.direction = random.randrange(0, 1)
        self.line = line
        self.type = 1
        self.pos = None
        self.velocity = None
        self.heading = None
        self.speed = speed
        self.model = model
        self.wait_timer = 1
        self.route = self.get_connections()
        self.current_dest = (random.choice(self.route)).connection_to

    def get_connections(self):
        connections = self.current_station.get_directional_connections_for_line(self.direction, self.line)
        if connections is None or len(connections) == 0:
            if self.direction == 1:
                self.direction = 0
            else:
                self.direction = 1

        connections = self.current_station.get_directional_connections_for_line(self.direction, self.line)

        return connections

    def calculate_heading(self):
        self.heading = self.model.space.get_heading(self.pos, self.current_dest.pos)

    def move(self):
        self.calculate_heading()
        self.velocity = self.heading
        self.velocity /= np.linalg.norm(self.velocity)
        distance = self.model.space.get_distance(self.pos, self.current_dest.pos)
        if distance < self.speed:
            self.speed = self.speed / distance
        new_position = self.pos + self.velocity * self.speed
        self.model.space.move_agent(self, new_position)
        for agent in self.passengers:
            self.model.space.move_agent(agent, new_position)

    def step(self):
        if self.is_at_station():
            self.current_station = self.current_dest
            self.current_station.train_list.append(self)
            self.route = self.get_connections()
            self.current_dest = random.choice(self.route)
            self.current_dest = self.current_dest.connection_to
            self.speed = 66
            self.wait_timer = 1

        if self.wait_timer != 0:
            self.wait_timer -= 1
        else:
            self.move()

    def is_at_station(self):
        distance = self.model.space.get_distance(self.pos, self.current_dest.pos)
        if distance < 4:
            return True
        return False


class Connection:

    def __init__(self, connection_to_station, connection_from_station, line, direction):
        self.connection_to = connection_to_station
        self.connection_from = connection_from_station
        self.line = line
        self.direction = direction


class Station:

    def __init__(self, pos, line=None):
        self.train_list = []
        self.connections = []
        self.pos = pos
        self.type = 2
        self.line = line

    def is_train_available(self, direction, line=None):
        for train in self.train_list:
            if line is None:
                if train.direction == direction:
                    return True
            else:
                if train.direction == direction and train.line == line:
                    return True
        return False

    def get_available_train(self, direction, line=None):
        for train in self.train_list:
            if line is None:
                if train.direction == direction:
                    return train
            else:
                if train.direction == direction and train.line == line:
                    return train
        return None

    def get_connections_for_line(self, line):
        connections = [connection for connection in self.connections if connection.line == line]
        return connections

    def get_directional_connections_for_line(self, direction, line):
        connections = [connection for connection in self.connections if connection.line == line
                       and connection.direction == direction]
        return connections

    def get_connections(self, direction):
        connections = [connection for connection in self.connections if connection.direction == direction]
        return connections
