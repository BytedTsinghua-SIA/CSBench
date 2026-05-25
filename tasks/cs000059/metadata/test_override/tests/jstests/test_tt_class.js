'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'TableTemplate.js'), 'utf8');

const context = { 
  console: { log: console.log },
  document: { getElementById: () => null }
};
vm.createContext(context);
vm.runInContext(code, context);

// TableTemplate is defined as a function in global scope, check if it exists
const result = typeof context.TableTemplate === 'function' && typeof context.TableTemplate.fillIn === 'function';
console.log(JSON.stringify({ pass: result }));

