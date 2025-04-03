import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const manifestFilePath = join(__dirname, '../custom_components/octopus_germany/manifest.json');
const constantFilePath = join(__dirname, '../custom_components/octopus_germany/const.py');

function updateManifestVersion(version: string) {
  const buffer = readFileSync(manifestFilePath);
  const content = JSON.parse(buffer.toString());
  content.version = version;

  writeFileSync(manifestFilePath, JSON.stringify(content, null, 2));
  console.log(`Updated manifest version to '${version}'`);
}

function updateVersionConstant(version: string) {
  const buffer = readFileSync(constantFilePath);
  const oldContent = buffer.toString();

  const versionRegex = /INTEGRATION_VERSION = \"[^\"]+\"/g
  const newContent = oldContent.replace(versionRegex, `INTEGRATION_VERSION = \"${version}\"`);

  if (oldContent != newContent) {
    writeFileSync(constantFilePath, newContent);
    console.log(`Updated constant version to '${version}'`);
  } else {
    console.log(`Failed to update constant version to '${version}'`);
  }
}

updateManifestVersion(process.argv[2]);
updateVersionConstant(process.argv[2]);
