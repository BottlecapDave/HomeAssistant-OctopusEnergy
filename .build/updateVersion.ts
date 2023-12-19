import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const manifestFilePath = join(__dirname, '../custom_components/octopus_energy/manifest.json');
const constantFilePath = join(__dirname, '../custom_components/octopus_energy/const.py');

function updateManifestVersion(version: string) {
  const buffer = readFileSync(manifestFilePath);
  const content = JSON.parse(buffer.toString());
  content.version = version;

  writeFileSync(manifestFilePath, JSON.stringify(content, null, 2));
  console.log(`Updated manifest version to '${version}'`);
}

function updateVersionConstant(version: string) {
  const buffer = readFileSync(constantFilePath);
  let content = buffer.toString();

  const versionRegex = /INTEGRATION_VERSION = \"[^\"]+\"/g
  content = content.replace(versionRegex, `INTEGRATION_VERSION = \"${version}\"`);

  writeFileSync(constantFilePath, content);
  console.log(`Updated constant version to '${version}'`);
}

updateManifestVersion(process.argv[2]);
updateVersionConstant(process.argv[2]);