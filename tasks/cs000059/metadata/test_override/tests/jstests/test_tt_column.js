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
  rows: [
    { cells: [{ textContent: '{{Col1}}', innerText: '{{Col1}}' }, { textContent: '{{Col2}}', innerText: '{{Col2}}' }] },
    { cells: [{ textContent: 'val1', innerText: 'val1' }, { textContent: '{{value}}', innerText: '{{value}}' }] }
  ]
};
context.document.elements['test-table'] = table;

const dict = { Col1: 'Column1', Col2: 'Column2', value: 'test' };
context.TableTemplate.fillIn('test-table', dict, 'Column2');

const result = table.rows[1].cells[1].textContent === 'test';
console.log(JSON.stringify({ pass: result }));

