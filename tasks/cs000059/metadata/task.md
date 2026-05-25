# CS142 Project 3: JavaScript and the DOM

## Background

This project focuses on implementing interactive web components using JavaScript and the Document Object Model (DOM). You will build two main components: a DatePicker widget for date selection and a table template processor for dynamic content rendering.

## Setup

You need to have Node.js installed on your system to run the code quality checker. Once Node.js is installed, extract the project files into a directory.

Fetch the ESLint code quality tool by running:
```
npm install
```

Run ESLint on all JavaScript files using:
```
npm run lint
```

**Important:** Your code should start with `'use strict';` in each JavaScript file, and running ESLint should not output any errors or warnings. Any errors or warnings will be used to deduct style points.

## Problem 1: JavaScript Date Picker (25 points)

Implement an interactive `DatePicker` display using HTML, CSS, and JavaScript.

### Task

Create a file `DatePicker.js` that implements a JavaScript class named `DatePicker` that can be used as follows:

```javascript
var datePicker = new DatePicker("div1", function (id, fixedDate) {
   console.log("DatePicker with id", id,
       "selected date:", fixedDate.month + "/" + fixedDate.day + "/" + fixedDate.year);
});
datePicker.render(new Date("July 4, 1776"));
```

### Requirements

1. **Constructor**: Takes two arguments:
   - The `id` attribute for an existing div element
   - A date selection callback function

2. **Callback Function**: When a date is selected, the callback should be called with:
   - The `id` argument
   - An object containing properties `month`, `day`, `year` with number encoding (e.g., `{month: 1, day: 30, year: 2016}` represents January 30, 2016)

3. **Render Method**: Takes one argument consisting of a `Date` object that selects a particular month (the object can refer to any time within the month). When `render` is invoked, it replaces the contents of the date picker's div with HTML that displays a one-month calendar.

### Calendar Display Requirements

- Display days of the selected month in a grid with one line for each week and one column for each day of the week
- Weeks run from Sunday on the left to Saturday on the right
- Include a header row displaying abbreviations for days of the week (e.g., "Su", "Mo", etc.)
- Each day of the month is displayed as a number
- Days not in the selected month should be displayed as numbers but dimmed to indicate they are not part of the current month
- All weeks displayed must contain at least one day belonging to the current month (number of rows should not be fixed - typically 4-6 weeks)
- Display the name of the month and year at the top of the calendar
- Include "<" and ">" controls to navigate to the previous or next month
- Clicking on a valid day of the current month should invoke the callback with the appropriate arguments
- Clicking on days belonging to other months should not invoke the callback

4. **Styling**: Create a stylesheet `datepicker.css` to apply styling to the calendars and make them look nice. The corresponding link tag is already added in the HTML file.

5. **Independence**: Multiple date pickers should work independently (each can change its displayed month independently).

## Problem 2: Simple Table Template Processing (15 points)

Create a file `TableTemplate.js` that implements a JavaScript class named `TableTemplate` with a **static** method `fillIn`.

### Requirements for the `fillIn` method

1. **Method Signature**: Takes three arguments:
   - The `id` attribute for a `<table>` element
   - A dictionary object
   - A string `columnName` (optional)

2. **Header Row Processing**: First, examine the header row of the table and replace any text of the form `{{property}}` with the corresponding `property` value from the dictionary object.

3. **Column Processing**: 
   - Fill in all `{{property}}` elements in the column specified by `columnName` if such a column exists
   - The method assumes that the first row of the table holds the column names
   - Column names are guaranteed to be unique
   - If no `columnName` argument is specified, process the entire table
   - If the specified `columnName` is not matched, return without replacing any text in the columns (but still replace template strings in the header row)

4. **Template Replacement Example**: If a `td` element contains `"The date is the {{day}} day of month {{month}} of the year {{year}}"` and the dictionary is `{month: "January", day: "30", year: "2016"}`, update the text to `"The date is the 30 day of month January of the year 2016"`.

5. **Undefined Properties**: If a template specifies a property that is not defined in the dictionary object, replace the template with an empty string.

6. **Edge Cases**: 
   - You need only handle properly formatted templates
   - Behavior can be left undefined for nested templates (e.g., `{{foo {{bar}}}}`) or unbalanced `{{`
   - You do not need to handle nested tables or complex table cells
   - Note that browsers insert a `<tbody>` element around all `<tr>` elements in a table if the table doesn't already contain a `<tbody>`

7. **Template Processor**: You should use your `cs142-template-processor.js` solution from project 2 to help implement the `fillIn` method.

8. **Visibility**: Once your function has processed the entire table, examine the `visibility` property of the table's style and if it is `hidden`, update it to be `visible`.

## Additional Requirements and Constraints

- You may use either ECMAScript 2015 class syntax or the older style class definition using functions
- **You may not use jQuery or any other JavaScript library package** in this project
- You may use any JavaScript built-in functions (e.g., Date methods, `parseInt`, `parseFloat`, `isNaN`)
- Useful DOM element properties: `cells`, `firstChild`, `nextSibling`, `rows`, `tagName`, `textContent`, `innerHTML`
- Use `console.log` and `debugger` statements for debugging
- Open the JavaScript console in Chrome DevTools to check for errors
- When running ESLint, ensure the `.eslintrc.json` file is present
- You can ask ESLint to fix many style issues by running `npm run lint -- --fix`

## Style Points (10 points)

Your JavaScript must be:
- Clean (appropriate use of classes, no global variables other than constructor functions, etc.)
- Readable
- ESLint warning-free

## Deliverables

Submit the entire `project3` directory containing:
- `DatePicker.js` (Problem 1)
- `datepicker.css` (Problem 1 styling)
- `TableTemplate.js` (Problem 2)
- All supporting files

## Testing

Test your code by opening:
- `datepicker.html` in your browser to test Problem 1
- `cs142-test-table.html` in your browser to test Problem 2

