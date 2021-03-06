"use strict";

var DecryptPage = require("./decrypt_page")
  , CryptoJS = require("../core/cryptojs")
  , aes = require("../core/aes")
  , blobs = require("../core/blobs")
  , blobDelivery = require("../core/blob_delivery")
  , unsupportedBrowser = require("../core/unsupported_browser")
  , passwordChecking = require("../core/password_checking")
  ;

var DecryptController = module.exports = function () {

  if (!this.onSupportedBrowser()) {
    return unsupportedBrowser();
  }

  // Setup page
  this.page = (new DecryptPage()).init();
  this.page.submitCallback = this.submitDecrypt.bind(this);

  this.page.hideLoader();
  this.page.showForm();
  this.page.passwordInput.focus();
};

DecryptController.prototype.submitDecrypt = function (password) {
  if (password === "") {
    this.decryptError("You need to enter a password");
    this.page.focusPassword();
    return false;
  }

  this.page.disableForm();

  // TODO CHECK LENGTH?
  this.page.setProgress(0);
  this.page.showProgressBar();
  this.page.hideError();
  this.page.hideReady();

  // Schedule this for next tick so that progress bar shows up.
  setTimeout(function () {
    var b64ciphertext = this.page.getB64CipherText();
    aes.decrypt(b64ciphertext, password, this.decryptProgressCallback.bind(this));
  }.bind(this), 10);
};

DecryptController.prototype.decryptProgressCallback = function (error, percent, done, binaryResult, inProgress) {
  if (error) {
    // Assume this means bad password.
    this.badPassword();
  } else if (done) {

    if (!passwordChecking.checkString(binaryResult)) {
      return this.badPassword();
    }
    var jsonifiedObject = passwordChecking.unwrap(binaryResult)
      , decryptedObject = JSON.parse(jsonifiedObject)
      , blob = blobs.binaryStringToBlob(atob(decryptedObject.b64plaintext), decryptedObject.mimetype)
      ;

    this.page.showReady(blob, decryptedObject, function (err) {
      if (err) {
        return this.decryptError(err);
      }
      this.page.hideForm();
      this.page.hideProgressBar();
    }.bind(this));

  } else {
    if (!passwordChecking.checkString(inProgress)) {
      this.badPassword();
      return false;
    }
    this.page.setProgress(percent);
  }

};

DecryptController.prototype.badPassword = function () {
  this.decryptError("Incorrect Password");
  this.page.focusPassword();
};

DecryptController.prototype.decryptError = function (message) {
  this.page.hideProgressBar();
  this.page.enableForm();
  this.page.showError(message);
};

DecryptController.prototype.onSupportedBrowser = function () {
  return blobDelivery.canDeliverBlobDownloads();
};
