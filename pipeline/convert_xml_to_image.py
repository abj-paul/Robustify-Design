import xml.etree.ElementTree as ET
import pygraphviz as pgv

# Parse the XML
tree = ET.parse('data/execution_area/solution.xml')
root = tree.getroot()

# Create a directed graph
G = pgv.AGraph(strict=False, directed=True)

# Iterate through transitions and add them to the graph
for transition in root.findall('.//{http://www.omg.org/spec/UML/20090901}Transition'):
    source_state = transition.find('.//{http://www.omg.org/spec/UML/20090901}Source/{http://www.omg.org/spec/UML/20090901}State').attrib['name']
    target_state = transition.find('.//{http://www.omg.org/spec/UML/20090901}Target/{http://www.omg.org/spec/UML/20090901}State').attrib['name']
    effect = transition.find('.//{http://www.omg.org/spec/UML/20090901}Effect').attrib['name']
    
    G.add_edge(source_state, target_state, label=effect)

# Set layout and render the graph to an image file
G.layout(prog='dot')
output_file = "uml_diagram.png"
G.draw(output_file, format='png', prog='dot')
print(f"UML diagram saved as {output_file}")
