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

    const left = col * (stateWidth + margin) + padding;
    const top = row * (stateHeight + margin) + padding;
  
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

  // Define arrowhead marker
  const defs = document.createElementNS(svgNamespace, 'defs');
  const marker = document.createElementNS(svgNamespace, 'marker');
  marker.setAttribute('id', 'arrowhead');
  marker.setAttribute('markerWidth', '10');
  marker.setAttribute('markerHeight', '7');
  marker.setAttribute('refX', '10');
  marker.setAttribute('refY', '3.5');
  marker.setAttribute('orient', 'auto');

  const arrowHead = document.createElementNS(svgNamespace, 'polygon');
  arrowHead.setAttribute('points', '0 0, 10 3.5, 0 7');
  arrowHead.setAttribute('fill', 'black');

  marker.appendChild(arrowHead);
  defs.appendChild(marker);
  svg.appendChild(defs);

  transitions.forEach(({ startState, action, endState }) => {
    const startStateDiv = document.getElementById(`state-${startState}`);
    const endStateDiv = document.getElementById(`state-${endState}`);
  
    const startX = startStateDiv.offsetLeft + stateWidth / 2;
    const startY = startStateDiv.offsetTop + stateHeight / 2;
    const endX = endStateDiv.offsetLeft + stateWidth / 2;
    const endY = endStateDiv.offsetTop + stateHeight / 2;

    const arrowLine = document.createElementNS(svgNamespace, 'path');
    const path = `M ${startX} ${startY} Q ${(startX + endX) / 2} ${(startY + endY) / 2 - 30}, ${endX} ${endY}`;
    arrowLine.setAttribute('d', path);
    arrowLine.setAttribute('stroke', 'black');
    arrowLine.setAttribute('stroke-width', '2');
    arrowLine.setAttribute('fill', 'none');
    arrowLine.setAttribute('marker-end', 'url(#arrowhead)');
  
    svg.appendChild(arrowLine);

    // Add action text along the arrow using SVG text element
    const textElement = document.createElementNS(svgNamespace, 'text');
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2 - 30; // Offset to avoid overlap with the curve
    textElement.setAttribute('x', midX);
    textElement.setAttribute('y', midY);
    textElement.setAttribute('fill', 'black');
    textElement.setAttribute('font-size', '12px');
    textElement.setAttribute('text-anchor', 'middle');
    textElement.setAttribute('dy', '-5'); // Slightly adjust vertical position
    textElement.textContent = action;
  
    svg.appendChild(textElement);
  });
}
