from lark import Lark, Transformer

uml_grammar = r"""
start: class_associations

class_associations: (class_def association constraint?)*

class_def: "class" NAME "{" attributes "}"

attributes: attribute*

attribute: "attr" NAME ":" TYPE

association: "assoc" NAME ":" class_ref "->" class_ref

constraint: "context" class_ref "inv:" constraint_body

constraint_body: constraint_text

constraint_text: /[^]+/

class_ref: NAME

TYPE: /[a-zA-Z_]\w*/

NAME: /[a-zA-Z_]\w*/
"""


uml_parser = Lark(uml_grammar)

class UMLTransformer(Transformer):
    def class_associations(self, items):
        classes = []
        associations = []
        constraints = []
        for item in items:
            if isinstance(item, tuple):
                if len(item) == 3:
                    constraints.append(item[2])
                associations.append(item[:2])
            else:
                classes.append(item)
        return classes, associations, constraints

    def class_def(self, items):
        class_name, attributes = items
        return class_name, attributes

    def attributes(self, items):
        return items

    def attribute(self, items):
        return items

    def association(self, items):
        return items

    def constraint(self, items):
        return items[0].value.strip()

    def class_ref(self, items):
        return items[0].value

uml_converter = UMLTransformer()

uml_model = """
class Person {
    attr name: string
    attr age: int

    inv AgePositive: age > 0
}

class Department {
    attr name: string
}

assoc WorksIn: Person -> Department

context Person inv:
    self.age >= 18
"""

tree = uml_parser.parse(uml_model)
classes, associations, constraints = uml_converter.transform(tree)

print("Classes:")
for class_name, attributes in classes:
    print(class_name)
    for attr_name, attr_type in attributes:
        print(f"  {attr_name}: {attr_type}")

print("\nAssociations:")
for assoc_name, source_class, target_class in associations:
    print(f"{assoc_name}: {source_class} -> {target_class}")

print("\nConstraints:")
for constraint in constraints:
    print(constraint)
