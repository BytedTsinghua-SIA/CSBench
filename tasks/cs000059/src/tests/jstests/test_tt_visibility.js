'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');

// Load template processor
const templateCode = fs.readFileSync(path.join(srcDir, 'cs142-template-processor.js'), 'utf8');
const templateContext = { console: { log: console.log } };
vm.createContext(templateContext);
vm.runInContext(templateCode, templateContext);

// Load TableTemplate
const tableCode = fs.readFileSync(path.join(srcDir, 'TableTemplate.js'), 'utf8');
const context = {
  Cs142TemplateProcessor: templateContext.Cs142TemplateProcessor,
  console: { log: console.log },
  document: {
    elements: {},
    getElementById: function(id) { return this.elements[id] || null; }
  }
};
vm.createContext(context);
vm.runInContext(tableCode, context);

// Create mock table
const table = {
  id: 'test-table',
  style: { visibility: 'hidden' },
  querySelector: function() { return null; },
  rows: [{ cells: [{ textContent: 'test', innerText: 'test' }] }]
};
context.document.elements['test-table'] = table;

context.TableTemplate.fillIn('test-table', {});

const result = table.style.visibility === 'visible';
console.log(JSON.stringify({ pass: result }));

