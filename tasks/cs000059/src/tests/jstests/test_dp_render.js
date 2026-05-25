'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'DatePicker.js'), 'utf8');

const container = { 
  innerHTML: '', 
  id: 'test-div',
  querySelectorAll: () => []
};
const document = {
  getElementById: (id) => {
    if (id === 'test-div') return container;
    if (id === 'test-div-prev' || id === 'test-div-next') {
      return { addEventListener: () => {} };
    }
    return null;
  }
};

const context = {
  document: document,
  console: { log: console.log },
  Date: Date,
  parseInt: parseInt
};
vm.createContext(context);
vm.runInContext(code, context);

const dp = new context.DatePicker('test-div', () => {});
dp.render(new Date(2024, 0, 15));

const result = container.innerHTML.includes('table') && container.innerHTML.includes('January');
console.log(JSON.stringify({ pass: result }));

