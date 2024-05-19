from parse_uml_to_lts import uml_to_lts, write_in_file
from set_config import set_config
from execute_fortis import run_fortis
from output_to_uml import save_output_as_uml
from convert_xml_to_image import convert_xml_to_image
import os 

def convert_to_lts(base_path, parallel_sysfile_names, NO_ENV_FLAG):
    sys_lts = ""
    for parallel_system in parallel_sysfile_names:
        sys_lts += uml_to_lts(f"{base_path}/{parallel_system}")
    write_in_file(f"{base_path}/sys.lts", sys_lts, "System LTS Model")

    if NO_ENV_FLAG: write_in_file(f"{base_path}/env.lts", sys_lts, "Environment LTS Model")
    else: write_in_file(f"{base_path}/env.lts", uml_to_lts(f"{base_path}/env.xml"), "Environment LTS Model")

    write_in_file(f"{base_path}/p.lts", uml_to_lts(f"{base_path}/safety.xml"), "Property LTS Model")

# Test
input_path = "data/vending_machine"
progress = ["confirm"]
preferredMap = {
    "3": [
        ["scan", "check_price", "print_cmd", "print"]
    ]
}
controllableMap = {
    "1": ["check_price", "print_cmd"],
    "3": ["print", "scan"]
}
observableMap = {
    "0": ["check_price", "print_cmd"],
    "2": ["print", "scan"]
}

convert_to_lts(input_path, ["barcode-reader.xml","booking-program.xml","printer.xml"], True)
set_config(input_path, progress, preferredMap, controllableMap, observableMap)
run_fortis(input_path)
save_output_as_uml(input_path)
# Converting XML to image
convert_xml_to_image(input_path,"solution.xml")
convert_xml_to_image(input_path,"safety.xml")
for parallel in ["barcode-reader.xml","booking-program.xml","printer.xml"]:
    convert_xml_to_image(input_path,parallel)