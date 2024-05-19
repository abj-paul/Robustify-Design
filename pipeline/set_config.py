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

#config["options"]["algorithm"] = "CustomAlgorithm"
#config["options"]["controllableMap"]["1"].append("new_action")
#config["env"].append("new_env.lts")

filename = "data/execution_area/config-pareto.json"
with open(filename, 'w') as json_file:
    json.dump(config, json_file, indent=4)

print(f"Configuration written to {filename}")
