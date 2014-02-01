"use strict";

var HtmlWrapper = module.exports = function (template) {
  this.LINE_LENGTH = 128;
  this.template = template;
};

HtmlWrapper.prototype.wrap = function (b64ciphertext) {
  // Returns HTML Blob
  var splitCiphertext = this.splitIntoLines(b64ciphertext, this.LINE_LENGTH)
    , wrapped = this.template.replace("{{ ciphertext }}", splitCiphertext)
    ;
  return wrapped;
};

HtmlWrapper.prototype.splitIntoLines = function (text, length) {
  return text.match(new RegExp(".{1," + length +"}", "g")).join("\n");
};
