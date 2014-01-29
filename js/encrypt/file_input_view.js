"use strict";

/* View faking a file input */

var FileInputView = module.exports = function (realFileInput, browseButton, fileDisplay) {
  // all DOM elements
  this.realFileInput = realFileInput;
  this.browseButton = browseButton;
  this.fileDisplay = fileDisplay;

  this.anyFileSelected = false;

  this.realFileInput.onchange = this.handleFileInputChange.bind(this);
  this.browseButton.onclick = this.handleBrowseClick.bind(this);

};

FileInputView.prototype.handleFileInputChange = function () {
  var file = this.realFileInput.files[0] || null;

  if (!file) {
    this.setNoFile();
  } else {
    this.setFile(file);
  }

};

FileInputView.prototype.setNoFile = function () {
  this.anyFileSelected = false;
  this.fileDisplay.value = "";
  this.browseButton.value = "browse";
};

FileInputView.prototype.setFile = function (file) {
  this.anyFileSelected = true;
  this.fileDisplay.value = file.name;
  this.browseButton.value = "change";
};

FileInputView.prototype.handleBrowseClick = function () {
  // click the file input element
  this.realFileInput.click();
};
