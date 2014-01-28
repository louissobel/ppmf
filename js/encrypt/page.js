"use strict";

// Page View for encryption controller

var Page = module.exports = function () {
  this.encryptForm = document.getElementById("encrypt-form");

  this.passwordInput = document.getElementById("password");
  this.fileInput = document.getElementById("file-select");

  this.doneLink = document.getElementById("done-link");
  this.encryptStatus = document.getElementById("encrypt-status");

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

Page.prototype.setResultUrl = function (url) {
  this.doneLink.href = url;
};

Page.prototype.setProgress = function (percent) {
  this.encryptStatus.innerHTML = Math.floor(percent * 10000) / 100 + "%";
};

Page.prototype.getDecryptTemplate = function () {
  return document.getElementById("decrypt-template").innerText;
};
