
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
  console.log(states);
  console.log(transitions);
  const automataContainer = document.getElementById('automata-container');
  automataContainer.innerHTML = '';

  const stateWidth = 40;
  const stateHeight = 40;

  const margin = 60;
  const padding = 10;

  const numColumns = Math.ceil(Math.sqrt(states.length));
  const containerWidth = Math.max(automataContainer.offsetWidth, numColumns * (stateWidth + margin) + padding);
  const containerHeight = Math.max(automataContainer.offsetHeight, numColumns * (stateHeight + margin) + padding);

  automataContainer.style.width = `${containerWidth}px`;
  automataContainer.style.height = `${containerHeight}px`;

  const positions = [];

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

  // Create transitions
  const svgNamespace = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNamespace, 'svg');
  svg.style.position = 'absolute';
  svg.style.width = '100%';
  svg.style.height = '100%';
  svg.style.top = '0';
  svg.style.left = '0';
  automataContainer.appendChild(svg);

  transitions.forEach(({ startState, action, endState }) => {
    const startStateDiv = document.getElementById(`${startState}`);
    const endStateDiv = document.getElementById(`${endState}`);
  
    const startX = startStateDiv.offsetLeft + stateWidth / 2;
    const startY = startStateDiv.offsetTop + stateHeight / 2;
    const endX = endStateDiv.offsetLeft + stateWidth / 2;
    const endY = endStateDiv.offsetTop + stateHeight / 2;

    // Creating space between edges randomly
    const controlPointOffsetX = (Math.random() - 0.5) * 100;
    const controlPointOffsetY = (Math.random() - 0.5) * 100;

    const controlPoint1X = (startX + endX) / 2 + controlPointOffsetX;
    const controlPoint1Y = (startY + endY) / 2 + controlPointOffsetY;

    const arrowLine = document.createElementNS(svgNamespace, 'path');
    let path = `M ${startX} ${startY} C ${controlPoint1X} ${controlPoint1Y}, ${controlPoint1X} ${controlPoint1Y}, ${endX} ${endY}`;
    if (startState==endState) {
      const loopRadius = 70;
      const loopOffsetX = startX + loopRadius;
      const loopOffsetY = startY - loopRadius;

      path = `M ${startX} ${startY} C ${loopOffsetX} ${loopOffsetY}, ${loopOffsetX} ${loopOffsetY + 2 * loopRadius}, ${startX} ${startY}`;
    }
    
    arrowLine.setAttribute('d', path);
    arrowLine.setAttribute('stroke', 'black');
    arrowLine.setAttribute('stroke-width', '2');
    arrowLine.setAttribute('fill', 'none');
    arrowLine.setAttribute('marker-end', 'url(#arrowhead)');
  
    svg.appendChild(arrowLine);

    // Add action text along the arrow using SVG text element
    const textElement = document.createElementNS(svgNamespace, 'text');
    textElement.setAttribute('x', controlPoint1X);
    textElement.setAttribute('y', controlPoint1Y);
    textElement.setAttribute('fill', 'black');
    textElement.setAttribute('font-size', '12px');
    textElement.setAttribute('text-anchor', 'middle');
    textElement.setAttribute('dy', '-5'); // Slightly adjust vertical position
    textElement.textContent = action;
  
    svg.appendChild(textElement);
  });
}

function filterNodes() {
  let connectionCounts = [];
  for(let i=0; i<SERVER_STATES.length; i++) connectionCounts.push(0);
  for(let i=0; i<SERVER_TRANSITIONS.length; i++){
    connectionCounts[SERVER_TRANSITIONS[i].startState.split("s")[1]] += 1;
    connectionCounts[SERVER_TRANSITIONS[i].endState.split("s")[1]] += 1
  }
  const sortedConnectionCounts = connectionCounts.toSorted();

  let topNStates = [], N=5;
  for(let i=0; i<N; i++){
    for(j=0; j<connectionCounts.length; j++){
      if(connectionCounts[j]==sortedConnectionCounts[i]) topNStates.push(`s${j}`);
    }
  }

  console.log(`Top ${N} states = ${topNStates}`);

  const states = document.querySelectorAll('.state');
  const transitions = document.querySelectorAll('path');
  const labels = document.querySelectorAll('text');


  states.forEach(state => {
    if (topNStates.includes(state.id)) {
      state.style.display = 'none';
    } else {
      state.style.display = 'block';
      state.onclick = () => toggleConnections(state.id);
    }
  });

  transitions.forEach(transition => {
    const stateMatches = transition.getAttribute('d').match(/(s\d+)/g);
    const startState = stateMatches ? stateMatches[0] : null;
    const endState = stateMatches ? stateMatches[1] : null;

    if (!topNStates.includes(startState) && !topNStates.includes(endState)) {
      transition.style.display = 'none';
    } else {
      transition.style.display = 'block';
    }
  });

  labels.forEach(label => {
    const labelPosition = { x: parseFloat(label.getAttribute('x')), y: parseFloat(label.getAttribute('y')) };
    const labelMatchedTransition = Array.from(transitions).find(transition => {
      const d = transition.getAttribute('d');
      const stateMatches = d.match(/state-(s\d+)/g);
      const startState = stateMatches ? stateMatches[0] : null;
      const endState = stateMatches ? stateMatches[1] : null;
      const controlPoint1X = parseFloat(d.match(/C\s+([\d.]+)\s+/)[1]);
      const controlPoint1Y = parseFloat(d.match(/C\s+[\d.]+\s+([\d.]+),/)[1]);
      
      return controlPoint1X === labelPosition.x && controlPoint1Y === labelPosition.y && (mostConnectedNodes.includes(startState) || mostConnectedNodes.includes(endState));
    });
    
    if (!labelMatchedTransition) {
      label.style.display = 'none';
    } else {
      label.style.display = 'block';
    }
  });
}

function toggleConnections(stateId) {
  const connectedTransitions = document.querySelectorAll(`path[d*="${stateId}"]`);
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
  });
}
