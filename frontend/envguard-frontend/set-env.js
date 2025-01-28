const fs = require('fs');
const path = require('path');

// Read the environment variables
const hostAddress = process.env.HOST_ADDRESS || 'localhost';

// Path to the environment files
const envFilePath = path.join(__dirname, 'src', 'environments', 'environment.ts');

console.log(`Discovered server address of ${hostAddress}`);

// Replace the placeholder with the actual value
const envFileContent = `export const environment = {
    production: false,
    HOST_ADDRESS: '${hostAddress}',
    recaptchaKey_v3: '6LfwSsIqAAAAAGg575xOQk1XXLxuetg-rJaJGS7h',
    recaptchaKey_v2: '6LeYy8IqAAAAAAI-yqTPH2obOkF0ibld5LGG5cuZ',
    recaptchaKey_v2_localhost: '6LfwSsIqAAAAAGg575xOQk1XXLxuetg-rJaJGS7h'
  };
  //Updated
  `;


// Write the updated content to the environment files
fs.writeFileSync(envFilePath, envFileContent);

console.log('Environment files updated with HOST_ADDRESS:', hostAddress);