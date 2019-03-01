# server.py
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from EpidemicModel.model import SimModel
from EpidemicModel.ButtonModule import ButtonModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.health_state == 2:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal


infected_chart = ChartModule([{"Label": "Rate of Infection",
                               "Color": "Red"}, {"Label": "Decline of Health", "Color": "Green"}],
                             data_collector_name='datacollector')
n_slider = UserSettableParameter('slider', "Number of Agents", 100, 2, 200, 1)
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)
save_button = ButtonModule()
server = ModularServer(SimModel,
                       [grid, infected_chart, save_button],
                       "Sim Model",
                       {"N": n_slider, "width": 20, "height": 20})
