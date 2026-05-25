'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'DatePicker.js'), 'utf8');

const document = {
  getElementById: (id) => null
};

const context = {
  document: document,
  console: { log: console.log },
  Date: Date
};
vm.createContext(context);
vm.runInContext(code, context);

try {
  const dp = new context.DatePicker('nonexistent', () => {});
  dp.render(new Date(2024, 0, 15));
  console.log(JSON.stringify({ pass: true }));
} catch (e) {
  console.log(JSON.stringify({ pass: false }));
}

