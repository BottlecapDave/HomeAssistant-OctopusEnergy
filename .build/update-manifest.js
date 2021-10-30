const fs = require('fs');
const path = require('path');
const fileName = path.join(__dirname, '../custom_components/first_bus/manifest.json');
const file = require(fileName);

file.version = process.argv[2];
    
fs.writeFile(fileName, JSON.stringify(file, null, 2), function writeJSON(err) {
  if (err) {
    return console.log(err);
  }

  return `Updated version to ${file.version}`;
});