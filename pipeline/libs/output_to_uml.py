'''des (0, 3, 4)
(0, "scan", 1)
(2, "print_cmd", 3)
(1, "check_price", 2)
'''


NEW_LINE="\n"
EMPTY_LINE = ""

import os
def save_output_as_uml(project_path):
    index = 1
    for filename in os.listdir(f"{project_path}/solutions"):
        if filename.endswith(".aut"):
            save_output_as_uml_single_file(project_path,index)
            index += 1


def save_output_as_uml_single_file(project_path, solution_index):
    f = open(f"{project_path}/solutions/sol{solution_index}.aut","r")
    output = f.read()
    states = [f"s{i}" for i in range(int(output.split("\n")[0].split(",")[1]))]
    transitions = []
    for transition in output.split("\n")[1:]:
        if transition==NEW_LINE or transition==EMPTY_LINE: continue
        start_state = f's{int(transition.split(",")[0][1:])}'
        action = transition.split(",")[1].replace('"', '').replace(" ", "")
        end_state = f's{int(transition.split(",")[2][:-1])}'

        transitions.append((start_state, action, end_state))

    UML_BEGIN = '''<?xml version="1.0" encoding="UTF-8"?>
    <uml:Model xmlns:uml="http://www.omg.org/spec/UML/20090901">
    '''
    UML_EXIT='''
    </uml:Model>'''
    uml = UML_BEGIN

    for state in states:
        uml+= f'<uml:State name="{state}"/>\n'
    for transition in transitions:
        start_state = transition[0]
        action = transition[1]
        end_state = transition[2]
        
        uml+= f'''
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

    print(states)
    print(transitions)

    file = open(f"{project_path}/solution_{solution_index}.xml", "w")
    file.write(uml)
    file.close()
    print("Converted output to UML.")
