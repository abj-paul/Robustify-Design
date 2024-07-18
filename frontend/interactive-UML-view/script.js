async function fetchFileContent(filePath) {
  try {
      const response = await fetch(`http://127.0.0.1:8000/get-file-content/?file_path=${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const file_content = await response.text();
      console.log(file_content);
      parse_automata(file_content);
      document.getElementById("file-content").innerText = file_content;
  } catch (error) {
      console.error('Error fetching file content:', error);
      document.getElementById("file-content").innerText = "Error fetching file content.";
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
    stateDiv.id = `state-${state}`;
  
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
    const startStateDiv = document.getElementById(`state-${startState}`);
    const endStateDiv = document.getElementById(`state-${endState}`);
  
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
