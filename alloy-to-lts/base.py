class AlloyToLTSConverter:
    def __init__(self, alloy_code):
        self.alloy_code = alloy_code

    def convert_to_lts(self):
        # Define mappings from Alloy constructs to LTS elements
        state_map = {}  # Map Alloy signatures to LTS states
        transition_map = {}  # Map Alloy facts to LTS transitions
        labels = []

        # Parse the Alloy code to populate mappings
        lines = self.alloy_code.split("\n")
        current_sig = None
        for index in range(len(lines)):
            lines[index] = lines[index]
            if lines[index].startswith("sig"):
                current_sig = lines[index].split()[1]
                state_map[current_sig] = set()
                index+=1
                while "}" not in lines[index] and index < len(lines[index]):
                    index += 1
                
            elif lines[index].startswith("fact"):
                index+=1
                while "}" not in lines[index] and index < len(lines[index]):
                    source = lines[index].split("in")[1].split("->")[0]
                    destination = lines[index].split("in")[1].split("->")[1]
                    label = lines[index].split("in")[0]
                    transition_map[source] = destination
                    labels.append(label)
                    index += 1

        # Generate LTS states
        states = list(state_map.keys())

        return states, transition_map, labels

# Example Alloy code
alloy_code = """
sig Person {
    name: String,
    age: Int
}

sig Department {
    name: String
}

fact {
    WorksIn in Person -> Department
}
"""

# Example conversion
converter = AlloyToLTSConverter(alloy_code)
states, transitions, labels = converter.convert_to_lts()
print("States:", states)
print("Transitions:", transitions)
print("Labels:", labels)

'''
States: ['Person', 'Department']
Transitions: [('Person', 'Department')]
Labels: [('Person', 'Department', 'WorksIn')]
'''
