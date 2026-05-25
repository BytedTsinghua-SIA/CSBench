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

// Create mock table with multiple columns and rows
const table = {
  id: 'test-table',
  style: { visibility: 'hidden' },
  querySelector: function() { return null; },
  rows: [
    { cells: [{ textContent: '{{Col1}}', innerText: '{{Col1}}' }, { textContent: '{{Col2}}', innerText: '{{Col2}}' }] },
    { cells: [{ textContent: '{{val1}}', innerText: '{{val1}}' }, { textContent: '{{val2}}', innerText: '{{val2}}' }] },
    { cells: [{ textContent: '{{val3}}', innerText: '{{val3}}' }, { textContent: '{{val4}}', innerText: '{{val4}}' }] }
  ]
};
context.document.elements['test-table'] = table;

const dict = { Col1: 'Column1', Col2: 'Column2', val1: 'value1', val2: 'value2', val3: 'value3', val4: 'value4' };
// Call fillIn without columnName to process entire table
context.TableTemplate.fillIn('test-table', dict);

// Check that all cells in all rows are processed
const result = table.rows[0].cells[0].textContent === 'Column1' &&
               table.rows[0].cells[1].textContent === 'Column2' &&
               table.rows[1].cells[0].textContent === 'value1' &&
               table.rows[1].cells[1].textContent === 'value2' &&
               table.rows[2].cells[0].textContent === 'value3' &&
               table.rows[2].cells[1].textContent === 'value4';
console.log(JSON.stringify({ pass: result }));

