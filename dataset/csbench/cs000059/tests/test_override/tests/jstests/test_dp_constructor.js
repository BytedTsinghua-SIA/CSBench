'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'DatePicker.js'), 'utf8');

const context = { console: { log: console.log } };
vm.createContext(context);
vm.runInContext(code, context);

const result = typeof context.DatePicker === 'function';
console.log(JSON.stringify({ pass: result }));

