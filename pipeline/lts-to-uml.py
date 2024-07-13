import xml.etree.ElementTree as ET
import pygraphviz as pgv

test = '''ENV = (v.enter -> VOTER | eo.enter -> EO),
VOTER = (password -> VOTER | select -> VOTER | vote -> VOTER | confirm -> VOTER | back -> VOTER | v.exit -> ENV),
EO = (select -> EO | vote -> EO | confirm -> EO | back -> EO | eo.exit -> ENV).
'''

def save_output_as_uml_single_file(filename):
    output = test
    states = set()
    transitions = []

    for line in output.split("\n"):
        if not line.strip():
            continue
        
        line = line.replace(',', '').replace(')', '').replace('.', '')
        parts = line.split("=")
        start_state = parts[0].strip()

        state_transitions = parts[1].split(" | ")
        for transition in state_transitions:
            action_state = transition.split(" -> ")
            action = action_state[0].strip()
            end_state = action_state[1].strip()

            states.add(start_state)
            states.add(end_state)
            transitions.append((start_state, action, end_state))

    UML_BEGIN = '''<?xml version="1.0" encoding="UTF-8"?>
<uml:Model xmlns:uml="http://www.omg.org/spec/UML/20090901">
'''
    UML_EXIT = '''
</uml:Model>'''
    uml = UML_BEGIN

    for state in states:
        uml += f'<uml:State name="{state}"/>\n'
    for transition in transitions:
        start_state = transition[0]
        action = transition[1]
        end_state = transition[2]
        
        uml += f'''
    <uml:Transition>
        <uml:Source>
            <uml:State name="{start_state}"/>
        </uml:Source>
        <uml:Target>
            <uml:State name="{end_state}"/>
        </uml:Target>
        <uml:Effect name="{action}"/>
    </uml:Transition>'''
    uml += UML_EXIT

    with open(f"{filename}.xml", "w") as file:
        file.write(uml)

    print("Converted output to UML.")
    convert_xml_to_image(f"{filename}.xml")

def convert_xml_to_image(filename):
    # Parse the XML
    tree = ET.parse(filename)
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
    output_file = f"{filename.rstrip('.xml')}.png"
    G.draw(output_file, format='png', prog='dot')
    print(f"UML diagram saved as {output_file}")

# Call the function to generate UML and convert to image
save_output_as_uml_single_file("test")
