async function fetchFileContent(filePath) {
  try {
      const response = await fetch(`http://127.0.0.1:8000/get-file-content/?file_path=${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const file_content = await response.text();
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
  console.log(states);
  console.log(transitions);
}
