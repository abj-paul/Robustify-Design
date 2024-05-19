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
    lts = {}
    states, transitions = parse_uml_model(uml_file)
    
    for state in states:
        lts[state] = []
    
    for source, target, action in transitions:
        lts[source].append((action, target))
    
    return lts

# Example usage
uml_file = 'data/test_uml.xml'  # Path to your UML XML file
lts = uml_to_lts(uml_file)
print(lts)
