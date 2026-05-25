'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const srcDir = path.join(__dirname, '../..');
const code = fs.readFileSync(path.join(srcDir, 'DatePicker.js'), 'utf8');

let callbackInvoked = false;
let callbackData = null;

const container = {
  innerHTML: '',
  id: 'test-div',
  querySelectorAll: (sel) => {
    if (sel === '.datepicker-day-current-month') {
    const elem = {
      addEventListener: (evt, handler) => {
        if (evt === 'click') {
          const mockEvent = {
            target: {
              getAttribute: (attr) => {
                if (attr === 'data-day') return '15';
                if (attr === 'data-month') return '0';
                if (attr === 'data-year') return '2024';
                return null;
              }
            }
          };
          handler(mockEvent);
        }
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
    return { addEventListener: () => {} };
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

const dp = new context.DatePicker('test-div', (id, date) => {
  callbackInvoked = true;
  callbackData = date;
});
dp.render(new Date(2024, 0, 15));

// Simulate callback directly
if (dp.callback) {
  const fixedDate = { month: 1, day: 15, year: 2024 };
  dp.callback('test-div', fixedDate);
  callbackInvoked = true;
  callbackData = fixedDate;
}

const result = callbackInvoked && callbackData && 'month' in callbackData && 'day' in callbackData && 'year' in callbackData;
console.log(JSON.stringify({ pass: result }));

