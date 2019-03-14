# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from EpidemicModel.SimpleContinuousModule import SimpleCanvas
from EpidemicModel.model import SimModel
from EpidemicModel.ButtonModule import ButtonModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Color": "grey",
                 "r": 3}

    if agent.health_state == agent.model.disease_model.health_state_dictionary.get("Infected")[1]:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
        portrayal["r"] = 2
    elif agent.health_state == agent.model.disease_model.health_state_dictionary.get("Recovered")[1]:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 3
    elif agent.health_state == agent.model.disease_model.health_state_dictionary.get("Exposed")[1]:
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 2
        portrayal["r"] = 2.5
    return portrayal


infected_chart = ChartModule([{"Label": "Rate of Infection",
                               "Color": "Red"}, {"Label": "Decline of Health", "Color": "Green"}],
                             data_collector_name='datacollector')
n_slider = UserSettableParameter('slider', "Number of Agents", 2000, 2, 10000, 1)
space = SimpleCanvas(agent_portrayal, canvas_height=1000, canvas_width=1000)
save_button = ButtonModule()
server = ModularServer(SimModel,
                       [space, infected_chart, save_button],
                       "Sim Model",
                       {"N": n_slider, "width": 1000, "height": 1000})
