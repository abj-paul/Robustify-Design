const fs = require('fs');
const path = require('path');

function saveOutputAsUMLSingleFile(filePath) {
    const output = fs.readFileSync(filePath, 'utf8');
    const lines = output.split('\n');
    console.log(lines[0])
    const stateCount = parseInt(lines[0].split(',')[2], 10);
    const states = Array.from({ length: stateCount }, (_, i) => `s${i}`);
    const transitions = [];

    for (let i = 1; i < lines.length; i++) {
        const transition = lines[i];
        if (transition === '\n' || transition === '') continue;
        
        const parts = transition.split(',');
        const startState = `s${parseInt(parts[0].substring(1), 10)}`;
        const action = parts[1].replace(/"/g, '').trim();
        const endState = `s${parseInt(parts[2].slice(0, -1), 10)}`;

        transitions.push({ startState, action, endState });
    }

    uml = ""
    console.log(states);
    console.log(transitions);

    return uml;
}

// Example usage:
//saveOutputAsUMLSingleFile('/home/abhijit/Robustify-Design/frontend/interactive-UML-view/sol12.aut');
test = "s21";
console.log(test.split("s")[1]);
