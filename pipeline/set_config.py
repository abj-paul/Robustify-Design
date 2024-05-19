import json
config = {
    "sys": ["sys.lts"],
    "env": [],
    "dev": ["env.lts"],
    "safety": ["p.lts"],
    "method": "supervisory",
    "options": {
        "progress": ["confirm"],
        "preferredMap": {
            "3": [
                ["scan", "check_price", "print_cmd", "print"]
            ]
        },
        "controllableMap": {
            "1": ["check_price", "print_cmd"],
            "3": ["print", "scan"]
        },
        "observableMap": {
            "0": ["check_price", "print_cmd"],
            "2": ["print", "scan"]
        },
        "algorithm": "Pareto"
    }
}

def set_config(project_path, progress_list, preferredMap, controllableMap, observableMap):
    config["options"]["progress"] = progress_list
    config["options"]["preferredMap"] = preferredMap
    config["options"]["controllableMap"] = controllableMap
    config["options"]["observableMap"] = observableMap

    filename = f'{project_path}/config-pareto.json' 

    with open(filename, 'w') as json_file:
        json.dump(config, json_file, indent=4)

    print(f"Configuration written to {filename}")
