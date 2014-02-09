"use strict";

/* View faking a file input */

var FileInputView = module.exports = function (realFileInput, browseButton, fileDisplay) {
  // all DOM elements
  this.realFileInput = realFileInput;
  this.browseButton = browseButton;
  this.originalButtonHTML = browseButton.innerHTML;
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

  if (this.onchange) {
    this.onchange(!!file);
  }

};

FileInputView.prototype.setNoFile = function () {
  this.anyFileSelected = false;
  this.fileDisplay.innerHTML = "";
  this.fileDisplay.style.display = "none";
  this.browseButton.innerHTML = this.originalButtonHTML;
};

FileInputView.prototype.setFile = function (file) {
  this.anyFileSelected = true;
  this.fileDisplay.innerHTML = file.name;
  this.fileDisplay.style.display = "inline-block";
  this.browseButton.innerHTML = "Change file";
};

FileInputView.prototype.handleBrowseClick = function () {
  // click the file input element
  this.realFileInput.click();
  return false;
};
