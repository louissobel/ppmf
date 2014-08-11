"use strict";

// Page View for encryption controller

var BasePage = require("../core/base_page")
  , blobDelivery = require("../core/blob_delivery")
  , inherits = require("../core/utils").inherits
  ;

var ChromeExtensionPage = module.exports = function () {};
inherits(ChromeExtensionPage, BasePage);

ChromeExtensionPage.prototype.init = function () {
  BasePage.prototype.init.call(this);

  this.doneLink = document.getElementById("done-link");

  this.whatNowLink = document.getElementById("what-now-link");
  this.whatNowBox = document.getElementById("what-now-box");
  this.whatNowLink.onclick = this.handleWhatNowClick.bind(this);

  this.tooBigWarning = document.getElementById("too-big-warning");
  this.tooBigSize = document.getElementById("too-big-size");
  this.tooBigEncryptAnyway = document.getElementById("too-big-encrypt-anyway");
  this.tooBigEncryptAnyway.onclick = this.handleEncryptAnywayClick.bind(this);

  // TODO: what if it is not there?
  this.fileUrl = window.location.hash.substr(1);

  return this;
};

ChromeExtensionPage.prototype.showReady = function (options, callback) {
  var filename = (options.filename || "save") + "__encrypted.html";
  var url = window.URL.createObjectURL(options.blob);
  window.chrome.downloads.download({
    url: url
  , filename: filename
  });
  BasePage.prototype.showReady.call(this);
  setTimeout(callback.bind(this, null), 0);
};

ChromeExtensionPage.prototype.handleFormSubmit = function () {
  this.doSubmitForm({
    force: false
  });
  return false;
};

ChromeExtensionPage.prototype.doSubmitForm = function (options) {
  if (this.submitCallback) {
    var password = this.passwordInput.value;
    this.submitCallback(password, options.force);
  }
};

ChromeExtensionPage.prototype.getDecryptTemplate = function () {
  return document.getElementById("decrypt-template").textContent;
};

ChromeExtensionPage.prototype.handleFileChange = function () {
  // Clear out the password if we're showing a ready.
  if (this.readyShowing) {
    this.clearPassword();
  }
  this.focusPassword();
};

ChromeExtensionPage.prototype.handleLearnMore = function () {
  this.slideView.rotateLeft();
  return false;
};

ChromeExtensionPage.prototype.handleWhatNowClick = function () {
  this.whatNowBox.style.display = "block";
};

ChromeExtensionPage.prototype.handleEncryptAnywayClick = function () {
  this.hideTooBigWarning();
  this.doSubmitForm({
    force: true
  });
  return false;
};

ChromeExtensionPage.prototype.showTooBigWarning = function (bytes) {
  var megabytes = Math.floor(100 * bytes / (1000 * 1000)) / 100;
  this.tooBigSize.innerHTML = megabytes;
  this.tooBigWarning.style.display = "block";
};

ChromeExtensionPage.prototype.hideTooBigWarning = function () {
  this.tooBigWarning.style.display = "none";
};
