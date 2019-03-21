

class SIRModel:
    health_state_dictionary = {
        "Susceptible": (0, 1),
        "Infected": (10, 2),
        "Recovered": (0, 3)
    }

    def __init__(self, infection_radius=5):
        self.infection_radius = infection_radius
        self.susceptible = (0, 1)
        self.infected = (10, 2)
        self.recovered = (0, 3)

    def infect(self, agent):
        neighbours = agent.model.space.get_neighbors(agent.pos, self.infection_radius, include_center=False)
        if len(neighbours) > 1:
            for neighbour in neighbours:
                if neighbour.type == 0:
                    if neighbour.health_state == 1:
                        neighbour.health_state = 2
                        neighbour.infected_step = agent.model.steps


class SEIRModel(SIRModel):
    health_state_dictionary = {
        "Susceptible": (0, 1),
        "Exposed": (5, 2),
        "Infected": (10, 3),
        "Recovered": (0, 4)
    }

    def infect(self, agent):
        neighbours = agent.model.space.get_neighbors(agent.pos, self.infection_radius, include_center=False)
        if len(neighbours) > 1:
            for neighbour in neighbours:
                if neighbour.type == 0:
                    if neighbour.health_state == agent.model.disease_model.health_state_dictionary.get("Susceptible")[1]:
                        neighbour.health_state = agent.model.disease_model.health_state_dictionary.get("Exposed")[1]
                        neighbour.exposed_step = agent.model.steps




