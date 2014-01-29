"use strict";

// Page View for encryption controller

var FileInputView = require("./file_input_view")
  , ProgressBar = require("./progress_bar")
  ;

var Page = module.exports = function () {
  this.encryptForm = document.getElementById("encrypt-form");

  this.passwordInput = document.getElementById("password");

  this.fileInput = document.getElementById("file-select");
  this.fileBrowseButton = document.getElementById("file-select-button");
  this.fileBrowseDisplay = document.getElementById("file-select-display");

  this.fileInputView = new FileInputView(this.fileInput, this.fileBrowseButton, this.fileBrowseDisplay);

  this.errorBox = document.getElementById("error-box");
  this.doneLink = document.getElementById("done-link");
  this.readyBox = document.getElementById("ready-box");
  this.encryptProgressBar = new ProgressBar(document.getElementById("encrypt-progress-bar"));

  this.encryptForm.onsubmit = function (e) {
    if (this.submitCallback) {
      var password = this.passwordInput.value
        , selectedFile = this.fileInput.files[0] || null
        ;
      this.submitCallback(password, selectedFile);
      return false;
    }
  }.bind(this);

};

Page.prototype.showReady = function (url) {
  this.readyBox.style.display = "block";
  this.doneLink.href = url;
};

Page.prototype.hideReady = function () {
  this.readyBox.style.display = "none";
};

Page.prototype.setProgress = function (percent) {
  var rounded = Math.floor(percent * 10000) / 100;
  this.encryptProgressBar.setPercent(rounded);
};

Page.prototype.getDecryptTemplate = function () {
  return document.getElementById("decrypt-template").textContent;
};

Page.prototype.showError = function (errmessage) {
  this.errorBox.style.display = "block";
  this.errorBox.innerHTML = errmessage;
};

Page.prototype.hideError = function () {
  this.errorBox.style.display = "none";
};

Page.prototype.showProgressBar = function () {
  this.encryptProgressBar.show();
};

Page.prototype.hideProgressBar = function () {
  this.encryptProgressBar.hide();
};
