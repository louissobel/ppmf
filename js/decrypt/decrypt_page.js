"use strict";

// The main view for the page
// Interfaces with DOM

var BasePage = require("../core/base_page")
  , inherits = require("../core/utils").inherits
  , mimeTypes = require("./mime_types")
  ;

var DecryptPage = module.exports = function () {};
inherits(DecryptPage, BasePage);

DecryptPage.prototype.init = function () {
  BasePage.prototype.init.call(this);
  this.fileLink = document.getElementById("file-link");
  this.viewLink = document.getElementById("view-link");
  this.loader = document.getElementById("loader");
  return this;
};

DecryptPage.prototype.handleFormSubmit = function () {
  if (this.submitCallback) {
    var password = this.passwordInput.value;
    this.submitCallback(password);
    return false;
  }
};

DecryptPage.prototype.showDecryptForm = function () {
  this.actionForm.style.display = "block";
  this.passwordInput.focus();
};

DecryptPage.prototype.hideDecryptForm = function () {
  this.actionForm.style.display = "none";
};

DecryptPage.prototype.showLoader = function () {
  this.loader.style.display = "block";
};

DecryptPage.prototype.hideLoader = function () {
  this.loader.style.display = "none";
};

DecryptPage.prototype.getB64CipherText = function () {
  var ciphertextHolder = document.getElementById("ciphertext");
  return ciphertextHolder.textContent.split("\n").join("");
};

DecryptPage.prototype.showReady = function (url, decryptedObj) {

  if (mimeTypes.canViewInWindow(decryptedObj.mimetype)) {
    this.viewLink.href = url;
    this.viewLink.style.display = "inline-block";
  } else {
    this.viewLink.style.display = "none";
  }

  this.fileLink.href = url;
  this.fileLink.download = decryptedObj.filename;
  BasePage.prototype.showReady.call(this);
};
