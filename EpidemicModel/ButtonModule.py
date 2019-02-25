from mesa.visualization.ModularVisualization import VisualizationElement


class ButtonModule(VisualizationElement):
    local_includes = ["ButtonModule.js"]

    def __init__(self):
        new_element = "new ButtonModule({})"
        self.js_code = "elements.push(" + new_element + ");"

