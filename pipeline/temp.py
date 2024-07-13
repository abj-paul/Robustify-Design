from libs.parse_uml_to_lts import uml_to_lts, write_in_file
from libs.set_config import set_config
from libs.execute_fortis import run_fortis
from libs.output_to_uml import save_output_as_uml
from libs.convert_xml_to_image import convert_xml_to_image    
from wrapper import convert_to_lts

convert_to_lts("./projects/Vending-Machine", ["barcode-reader.xml","booking-program.xml","printer.xml"], True)
run_fortis("./projects/Vending-Machine")
