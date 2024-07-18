
let SERVER_STATES = [];
let SERVER_TRANSITIONS = [];

async function fetchFileContent(filePath) {
  try {
      const response = await fetch(`http://127.0.0.1:8000/get-file-content/?file_path=${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const file_content = await response.text();
      console.log(file_content);
      parse_automata(file_content);
  } catch (error) {
      console.error('Error fetching file content:', error);
  }
}


function handleFetch() {
  const filePath = document.getElementById("file-path").value;
  fetchFileContent(filePath);
}

function parse_automata(output) {
  const lines = output.split('\n');
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

  SERVER_STATES = states;
  SERVER_TRANSITIONS = transitions;
  visualize_automata(states, transitions);
}

function visualize_automata(states, transitions) {
  const automataContainer = document.getElementById('automata-container');
  automataContainer.innerHTML = '';

  const stateWidth = 40;
  const stateHeight = 40;
  const margin = 60;
  const padding = 10;
  const numColumns = Math.ceil(Math.sqrt(states.length));
  const containerWidth = Math.max(automataContainer.offsetWidth, numColumns * (stateWidth + margin) + padding);
  const containerHeight = Math.max(automataContainer.offsetHeight, numColumns * (stateHeight + margin) + padding);

  //automataContainer.style.width = `${containerWidth}px`;
  //automataContainer.style.height = `${containerHeight}px`;

  const positions = [];

  // Create states
  states.forEach((state, index) => {
    const stateDiv = document.createElement('div');
    stateDiv.className = 'state';
    stateDiv.textContent = state;
    stateDiv.id = `${state}`;

    const row = Math.floor(index / numColumns);
    const col = index % numColumns;
    const left = col * 2 * (stateWidth + margin) + padding;
    const top = row * 2 * (stateHeight + margin) + padding;

    positions.push({ left, top });

    stateDiv.style.position = 'absolute';
    stateDiv.style.left = `${left}px`;
    stateDiv.style.top = `${top}px`;

    automataContainer.appendChild(stateDiv);
  });

  // Create SVG for transitions
  const svgNamespace = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNamespace, 'svg');
  svg.style.position = 'absolute';
  svg.style.width = '100%';
  svg.style.height = '100%';
  svg.style.top = '0';
  svg.style.left = '0';
  automataContainer.appendChild(svg);

  states.forEach((state, index) => {
    let outgoingEdgeCountForCurrentState = 0;
    for(let i=0; i<transitions.length; i++){
      if(transitions[i].startState == state) {
        startState = transitions[i].startState;
        action = transitions[i].action;
        endState = transitions[i].endState;

        const startStateDiv = document.getElementById(`${startState}`);
        const endStateDiv = document.getElementById(`${endState}`);

        const startX = startStateDiv.offsetLeft + stateWidth / 2;
        const startY = startStateDiv.offsetTop + stateHeight / 2;
        const endX = endStateDiv.offsetLeft + stateWidth / 2;
        const endY = endStateDiv.offsetTop + stateHeight / 2;

        let controlPoint1X = (startX + endX) / 2 + outgoingEdgeCountForCurrentState * 20;
        let controlPoint1Y = (startY + endY) / 2 + outgoingEdgeCountForCurrentState * 20;
        if(outgoingEdgeCountForCurrentState%2){
          controlPoint1X = (startX + endX) / 2 - outgoingEdgeCountForCurrentState * 20;
          controlPoint1Y = (startY + endY) / 2 - outgoingEdgeCountForCurrentState * 20;
        }

        // Create a path element for the transition
        const pathId = `${startState}-${endState}-path`;
        const path = document.createElementNS(svgNamespace, 'path');
        let pathData = `M ${startX} ${startY} C ${controlPoint1X},${controlPoint1Y} ${controlPoint1X+50},${controlPoint1Y+50} ${endX},${endY}`;

        if (startState === endState) {
          const loopRadius = 70;
          const loopOffsetX = startX + loopRadius;
          const loopOffsetY = startY - loopRadius;

          pathData = `M ${startX} ${startY} C ${loopOffsetX} ${loopOffsetY}, ${loopOffsetX} ${loopOffsetY + 2 * loopRadius}, ${startX} ${startY}`;
        }

        path.setAttribute('d', pathData);
        path.setAttribute('id', pathId);
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('marker-end', 'url(#arrowhead)');

        svg.appendChild(path);

        // Create text element along the path
        const textElement = document.createElementNS(svgNamespace, 'text');
        const textPath = document.createElementNS(svgNamespace, 'textPath');
        textPath.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', `#${pathId}`);
        textPath.setAttribute('startOffset', '50%'); // Adjust as needed

        textPath.textContent = action;
        textElement.setAttribute('font-size', '12px');
        textElement.setAttribute('text-anchor', 'middle');
        textElement.setAttribute('dy', '-5'); // Slightly adjust vertical position

        const colors = ['black', 'blue', 'green', 'purple', 'red', 'yellow', 'brown'];
        const colorIndex = outgoingEdgeCountForCurrentState % colors.length;
        path.setAttribute('stroke', colors[colorIndex]);
        textElement.setAttribute('fill', colors[colorIndex]);


        textElement.appendChild(textPath);
        svg.appendChild(textElement);
        outgoingEdgeCountForCurrentState+=1;
      }
    }
  })
}

function filterNodes() {
  let connectionCounts = [];
  for(let i = 0; i < SERVER_STATES.length; i++) connectionCounts.push(0);
  for(let i = 0; i < SERVER_TRANSITIONS.length; i++) {
    connectionCounts[parseInt(SERVER_TRANSITIONS[i].startState.split("s")[1])] += 1;
    connectionCounts[parseInt(SERVER_TRANSITIONS[i].endState.split("s")[1])] += 1;
  }
  const sortedConnectionCounts = connectionCounts.toSorted(); // Descendeding
  sortedConnectionCounts.reverse();

  let topNStates = [], N=5;
  for(let i=0; i<N; i++){
    for(j=0; j<connectionCounts.length; j++){
      if(connectionCounts[j]==sortedConnectionCounts[i]) topNStates.push(`s${j}`);
    }
  }  
  console.log(`Connection counts = ${connectionCounts}`);

  console.log(`Top ${N} states = ${topNStates}`);

  const states = document.querySelectorAll('.state');
  const transitions = document.querySelectorAll('path');
  const labels = document.querySelectorAll('text');

  states.forEach(state => {
    if (!topNStates.includes(state.id)) {
      state.style.display = 'none';
    } else {
      //state.style.display = 'block';
      state.style.border = "2px solid red";
      document.getElementById(state.id).onclick = () => toggleConnections(state.id);
      console.log(state);
    }
  });

  transitions.forEach(transition => {
    const dAttr = transition.getAttribute('d');
    const startMatch = dAttr.match(/M\s(\d+)\s(\d+)/);
    const endMatch = dAttr.match(/C\s(\d+)\s(\d+),\s(\d+)\s(\d+),\s(\d+)\s(\d+)/);
    if (startMatch && endMatch) {
      const startX = startMatch[1];
      const startY = startMatch[2];
      const endX = endMatch[5];
      const endY = endMatch[6];
      
      const startState = getStateIdByPosition(startX, startY);
      const endState = getStateIdByPosition(endX, endY);
      
      if (!topNStates.includes(startState) && !topNStates.includes(endState)) {
        transition.style.display = 'none';
      } else {
        transition.style.display = 'block';
      }
    }
  });

  /*labels.forEach(label => {
    label.style.display = 'none';
    transitions.forEach(transition => {
      if (transition.style.display === 'block') {
        const dAttr = transition.getAttribute('d');
        const controlPointMatch = dAttr.match(/C\s(\d+)\s(\d+)/);
        if (controlPointMatch) {
          const controlPointX = parseFloat(controlPointMatch[1]);
          const controlPointY = parseFloat(controlPointMatch[2]);
          if (parseFloat(label.getAttribute('x')) === controlPointX && parseFloat(label.getAttribute('y')) === controlPointY) {
            label.style.display = 'block';
          }
        }
      }
    });
  });*/
}

function getStateIdByPosition(x, y) {
  const states = document.querySelectorAll('.state');
  for (const state of states) {
    const stateX = parseFloat(state.style.left) + state.offsetWidth / 2;
    const stateY = parseFloat(state.style.top) + state.offsetHeight / 2;
    if (Math.abs(stateX - x) < 5 && Math.abs(stateY - y) < 5) {
      return state.id;
    }
  }
  return null;
}


function toggleConnections(stateId) {
  console.log(`Log: Triggered toggleConnections for state = ${stateId}`);
  /*const connectedTransitions = document.querySelectorAll(`path[d*="${stateId}"]`);
  const labels = document.querySelectorAll('text');

  connectedTransitions.forEach(transition => {
    const displayStyle = transition.style.display === 'none' ? 'block' : 'none';
    transition.style.display = displayStyle;
    
    const d = transition.getAttribute('d');
    const controlPoint1X = parseFloat(d.match(/C\s+([\d.]+)\s+/)[1]);
    const controlPoint1Y = parseFloat(d.match(/C\s+[\d.]+\s+([\d.]+),/)[1]);
    
    labels.forEach(label => {
      const labelPosition = { x: parseFloat(label.getAttribute('x')), y: parseFloat(label.getAttribute('y')) };
      if (labelPosition.x === controlPoint1X && labelPosition.y === controlPoint1Y) {
        label.style.display = displayStyle;
      }
    });
  });*/
}
