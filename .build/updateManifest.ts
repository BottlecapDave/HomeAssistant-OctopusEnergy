import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const filePath = join(__dirname, '../custom_components/octopus_energy/manifest.json');

function updateManifest(version: string) {

  const buffer = readFileSync(filePath);
  const content = JSON.parse(buffer.toString());
  content.version = version;

  writeFileSync(filePath, JSON.stringify(content, null, 2));
  console.log(`Updated version to '${version}'`);
}

updateManifest(process.argv[2]);