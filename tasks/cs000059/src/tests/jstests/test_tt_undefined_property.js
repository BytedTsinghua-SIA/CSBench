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

// Create mock table with undefined property in template
const table = {
  id: 'test-table',
  style: { visibility: 'visible' },
  querySelector: function() { return null; },
  rows: [
    { cells: [{ textContent: '{{name}}', innerText: '{{name}}' }] },
    { cells: [{ textContent: 'Value is {{undefinedProp}} here', innerText: 'Value is {{undefinedProp}} here' }] }
  ]
};
context.document.elements['test-table'] = table;

const dict = { name: 'Test' };
// undefinedProp is not in dictionary, should be replaced with empty string
context.TableTemplate.fillIn('test-table', dict);

// Check that undefined property is replaced with empty string
const result = table.rows[0].cells[0].textContent === 'Test' &&
               table.rows[1].cells[0].textContent === 'Value is  here';
console.log(JSON.stringify({ pass: result }));

