import xml.etree.ElementTree as ET

class State:
    def __init__(self, name):
        self.name = name

class Transition:
    def __init__(self, source, target, action):
        self.source = source
        self.target = target
        self.action = action


def parse_uml_model(uml_file):
    tree = ET.parse(uml_file)
    root = tree.getroot()
    
    ns = {'uml': 'http://www.omg.org/spec/UML/20090901'}  # Define the namespace

    states = [elem.get('name') for elem in root.findall(".//uml:State", ns)]
    transitions = []
    
    for trans in root.findall(".//uml:Transition", ns):
        source = trans.find(".//uml:Source/uml:State", ns).get('name')
        target = trans.find(".//uml:Target/uml:State", ns).get('name')
        action = trans.find(".//uml:Effect", ns).get('name', 'no_action')
        transitions.append((source, target, action))

    return states, transitions

def uml_to_lts(uml_file):
    lts_transition = {}
    states, transitions = parse_uml_model(uml_file)
    
    for state in states:
        lts_transition[state] = []
    
    for source, target, action in transitions:
        lts_transition[source].append((action, target))
    
    lts = ""
    i = 0
    for state, transition in lts_transition.items():
        lts += f"{state} = "
        for j, temp in enumerate(transition):
            action, end_state = temp[0], temp[1]
            if j == 0: lts+= f"( "
            lts += f"{action} -> {end_state}"
            if j < len(transition)-1: lts += " | "
            elif i==len(lts_transition.items())-1: lts += " )."
            else: lts += " ),\n"
        i+=1
    return lts

def write_in_file(filename, content, content_name):
    file = open(filename, 'w')
    file.write(content)
    file.close()
    print(f"{content_name} saved in {filename}")

# Example usage
uml_file = 'data/vending_machine.xml'  # Path to your UML XML file
lts = uml_to_lts(uml_file)
write_in_file("data/execution_area/sys.lts", lts, "System LTS Model")
write_in_file("data/execution_area/env.lts", lts, "Environment LTS Model")
write_in_file("data/execution_area/p.lts", lts, "Property LTS Model")

