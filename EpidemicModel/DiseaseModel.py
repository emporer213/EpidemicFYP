import random


class SIRModel:
    health_state_dictionary = {
        "Susceptible": (0, 1),
        "Infected": (600, 2),
        "Recovered": (0, 3)
    }

    def __init__(self, infection_radius=5):
        self.infection_radius = infection_radius
        self.susceptible = (0, 1)
        self.infected = (10, 2)
        self.recovered = (0, 3)

    def infect(self, agent):
        neighbours = agent.model.space.get_neighbors(agent.pos, self.infection_radius, include_center=True)
        if len(neighbours) > 1:
            for neighbour in neighbours:
                if neighbour.type == 0:
                    if neighbour.health_state == 1:
                        neighbour.health_state = 2
                        neighbour.infected_step = agent.model.steps


class SEIRModel(SIRModel):
    health_state_dictionary = {
        "Susceptible": (0, 1),
        "Exposed": (240, 2),
        "Infected": (600, 3),
        "Recovered": (0, 4)
    }

    def infect(self, agent):
        neighbours = agent.model.space.get_neighbors(agent.pos, self.infection_radius, include_center=False)
        human_neighbours = [neighbour for neighbour in neighbours if neighbour.type == 0]
        if len(neighbours) > 0:
            susceptible_neighbour = [neighbour for neighbour in human_neighbours if neighbour.health_state ==
                                     self.health_state_dictionary.get("Susceptible")[1]]

            if len(susceptible_neighbour) > 0:
                neighbour_to_infect = random.choice(susceptible_neighbour)
                neighbour_to_infect.health_state = self.health_state_dictionary.get("Exposed")[1]
                neighbour_to_infect.exposed_step = agent.model.steps
                neighbour_to_infect.state_when_infected = neighbour_to_infect.state
