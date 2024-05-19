import os

def run_fortis(project_path):
    os.chdir(project_path)

    jar_path = os.path.abspath(os.path.join("../../../existing-codebase/bin/fortis.jar"))
    config_path = "config-pareto.json"
    os.system(f"java -jar {jar_path} robustify {config_path}")

    os.chdir("../..")
    print(f"Fortis generated robust designs in {project_path}/solutions.")

# Example usage
#run_fortis("vending_machine")
