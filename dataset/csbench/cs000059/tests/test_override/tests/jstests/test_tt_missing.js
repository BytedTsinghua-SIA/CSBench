'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'TableTemplate.js'), 'utf8');

const context = {
  document: { getElementById: function() { return null; } },
  console: { log: console.log }
};
vm.createContext(context);
vm.runInContext(code, context);

try {
  context.TableTemplate.fillIn('nonexistent', {});
  console.log(JSON.stringify({ pass: true }));
} catch (e) {
  console.log(JSON.stringify({ pass: false }));
}

