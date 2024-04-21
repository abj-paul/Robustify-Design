class UMLToAlloyConverter:
    def __init__(self, uml_text):
        self.uml_text = uml_text

    def convert_to_alloy(self):
        alloy_code = "module UMLModel\n\n"
        classes = self.extract_classes()
        for class_name, attributes in classes.items():
            alloy_code += f"abstract sig {class_name} {{\n"
            for attr_name, attr_type in attributes.items():
                alloy_code += f"\t{attr_name}: {attr_type},\n"
            alloy_code += "}\n\n"
        alloy_code += "fact {\n"
        associations = self.extract_associations()
        for association in associations:
            alloy_code += f"{association}\n"
        alloy_code += "}"
        return alloy_code

    def extract_classes(self):
        classes = {}
        lines = self.uml_text.split("\n")
        current_class = None
        for line in lines:
            line = line.strip()
            if line.startswith("class"):
                class_name = line.split(":")[0].strip().split()[1]
                classes[class_name] = {}
                current_class = class_name
            elif line.startswith("attr"):
                if current_class:
                    attr_line = line.split(":")
                    attr_type = attr_line[1]
                    attr_name = attr_line[0].split("attr")[1]

                    if len(attr_line) == 2:
                        classes[current_class][attr_name] = attr_type
                    else:
                        print("Invalid attribute format:", attr_line)
        return classes



    def extract_associations(self):
        associations = []
        lines = self.uml_text.split("\n")
        for index in range(len(lines)):
            if lines[index].startswith("assoc"):
                association = lines[index].split()[1].split(":")[0] + " in "
                index += 1
                while index<len(lines) and not lines[index].startswith("assoc"):
                    association += lines[index]
                    index+=1
                associations.append(association)
        return associations


uml_text = """
class Person:
    attr name: string
    attr age: int

class Department:
    attr name: string

assoc WorksIn:
    Person -> Department
"""

converter = UMLToAlloyConverter(uml_text)
alloy_code = converter.convert_to_alloy()
print(alloy_code)

'''
module UMLModel

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

'''
