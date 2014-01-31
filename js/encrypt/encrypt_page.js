"use strict";

// Page View for encryption controller

var FileInputView = require("./file_input_view")
  , BasePage = require("../core/base_page")
  , inherits = require("../core/utils").inherits
  ;


var EncryptPage = module.exports = function () {};
inherits(EncryptPage, BasePage);

EncryptPage.prototype.init = function () {
  BasePage.prototype.init.call(this);

  this.fileInput = document.getElementById("file-select");
  this.fileBrowseButton = document.getElementById("file-select-button");
  this.fileBrowseDisplay = document.getElementById("file-select-display");

  this.fileInputView = new FileInputView(this.fileInput, this.fileBrowseButton, this.fileBrowseDisplay);

  this.doneLink = document.getElementById("done-link");
  return this;
};

EncryptPage.prototype.showReady = function (url) {
  BasePage.prototype.showReady.call(this);
  this.doneLink.href = url;
};

EncryptPage.prototype.handleFormSubmit = function () {
  if (this.submitCallback) {
    var password = this.passwordInput.value
      , selectedFile = this.fileInput.files[0] || null
      ;
    this.submitCallback(password, selectedFile);
    return false;
  }
};

EncryptPage.prototype.getDecryptTemplate = function () {
  return document.getElementById("decrypt-template").textContent;
};
