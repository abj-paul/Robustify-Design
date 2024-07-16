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
  const stateCount = parseInt(lines[0].split(',')[1], 10);
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

function isOverlap(x1, y1, w1, h1, x2, y2, w2, h2) {
  return !(x2 > x1 + w1 || 
           x2 + w2 < x1 || 
           y2 > y1 + h1 || 
           y2 + h2 < y1);
}

function visualize_automata(states, transitions) {
  const automataContainer = document.getElementById('automata-container');
  automataContainer.innerHTML = '';

  const stateWidth = 40;
  const stateHeight = 40;

  const margin = 20;
  const padding = 10;

  // Calculate the required container dimensions
  const numStates = states.length;
  const containerWidth = Math.max(automataContainer.offsetWidth, numStates/4 * (stateWidth + margin) + padding);
  const containerHeight = Math.max(automataContainer.offsetHeight, numStates/4 * (stateHeight + margin) + padding);

  automataContainer.style.width = `${containerWidth}px`;
  automataContainer.style.height = `${containerHeight}px`;


  const positions = [];

  states.forEach(state => {
    const stateDiv = document.createElement('div');
    stateDiv.className = 'state';
    stateDiv.textContent = state;
  
    let randomLeft, randomTop;
    let isOverlapping;
  
    do {
      isOverlapping = false;
      randomLeft = Math.random() * (containerWidth - stateWidth - padding);
      randomTop = Math.random() * (containerHeight - stateHeight - padding);
  
      for (let pos of positions) {
        if (isOverlap(randomLeft, randomTop, stateWidth, stateHeight, pos.left, pos.top, stateWidth, stateHeight)) {
          isOverlapping = true;
          break;
        }
      }
    } while (isOverlapping);
  
    // Save the position
    positions.push({ left: randomLeft, top: randomTop });
  
    // Set the position
    stateDiv.style.position = 'absolute';
    stateDiv.style.left = `${randomLeft}px`;
    stateDiv.style.top = `${randomTop}px`;
  
    automataContainer.appendChild(stateDiv);
  });
  console.log("Created states");

  /*
  // Create transitions
  transitions.forEach(({ startState, action, endState }) => {
    const startStateDiv = document.querySelector(`.state[data-state="${startState}"]`);
    const endStateDiv = document.querySelector(`.state[data-state="${endState}"]`);

    const transitionDiv = document.createElement('div');
    transitionDiv.className = 'transition';
    transitionDiv.textContent = action;
    startStateDiv.appendChild(transitionDiv);

    // Adjust arrow position (not a real arrow, just styling)
    const arrowDiv = document.createElement('div');
    arrowDiv.className = 'arrow';
    startStateDiv.appendChild(arrowDiv);
});
*/
}
