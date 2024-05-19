#!/bin/bash
cd data/execution_area
java -jar ../../../existing-codebase/bin/fortis.jar robustify config-pareto.json
cd ../..
echo "Fortis generated robust designs in /data/execution_area/solutions."
