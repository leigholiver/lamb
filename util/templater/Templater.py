import os
from jinja2 import Template

class Templater():
    templates_folder = os.path.dirname(os.path.realpath(__file__)) + "/templates/"

    def write(self, template, outputFile, params):
        with open(self.templates_folder + template, 'r') as file:
            data = file.read()
            t = Template(data)
            output = t.render(params)
            with open(outputFile, "w") as file:
                file.write(output)
