'use strict';

function Cs142TemplateProcessor(template) {
  this.template = template;
}

Cs142TemplateProcessor.prototype.fillIn = function(dictionary) {
  var result = this.template;
  var propertyPattern = /\{\{(\w+)\}\}/g;
  
  result = result.replace(propertyPattern, function(match, property) {
    if (dictionary.hasOwnProperty(property)) {
      return dictionary[property];
    }
    return '';
  });
  
  return result;
};

