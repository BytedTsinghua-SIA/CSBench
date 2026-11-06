'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'DatePicker.js'), 'utf8');

let querySelectorAllCalls = [];

const container = {
  innerHTML: '',
  id: 'test-div',
  querySelectorAll: (sel) => {
    // Track what selectors are queried
    querySelectorAllCalls.push(sel);
    
    // The implementation only adds listeners to .datepicker-day-current-month
    if (sel === '.datepicker-day-current-month') {
      const elem = {
        addEventListener: (evt, handler) => {
          // Listener added only to current month cells
        },
        getAttribute: (attr) => {
          if (attr === 'data-day') return '15';
          if (attr === 'data-month') return '0';
          if (attr === 'data-year') return '2024';
          return null;
        }
      };
      return [elem];
    }
    return [];
  }
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

// Verify that querySelectorAll was only called with '.datepicker-day-current-month'
// This means other month cells have no event listeners and cannot trigger callbacks
const onlyCurrentMonthQueried = querySelectorAllCalls.length > 0 && 
                                 querySelectorAllCalls.every(sel => sel === '.datepicker-day-current-month');

const result = onlyCurrentMonthQueried;
console.log(JSON.stringify({ pass: result }));

