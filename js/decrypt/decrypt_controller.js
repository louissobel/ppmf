"use strict";

var DecryptPage = require("./decrypt_page")
  , CryptoJS = require("../core/cryptojs")
  , aes = require("../core/aes")
  , base64 = require("../core/base64")
  ;

var DecryptController = module.exports = function () {
  // Setup page
  this.page = (new DecryptPage()).init();

  this.page.submitCallback = this.submitDecrypt.bind(this);

  this.page.hideLoader();
  this.page.showDecryptForm();

};

DecryptController.prototype.submitDecrypt = function (password) {
  var b64ciphertext = this.page.getB64CipherText();

  // TODO CHECK LENGTH?
  this.page.showProgressBar();
  this.page.hideError();
  this.page.hideReady();

  aes.decrypt(b64ciphertext, password, this.decryptProgressCallback.bind(this));
};

DecryptController.prototype.decryptProgressCallback = function (error, percent, done, result) {
  if (error) {
    // for now, assume this means password was bad
    this.badPassword();
  } else if (done) {

    var binaryResult
      , decryptedObject
      , blob
      , blobUrl
      ;

    try {
      binaryResult = atob(result);
    } catch (err) {
      return this.badPassword();
    }

    try {
      decryptedObject = JSON.parse(binaryResult);
    } catch (err) {
      return this.badPassword();
    }

    try {
      blob = base64.b64ToBlob(decryptedObject.b64plaintext, decryptedObject.mimetype);
    } catch (err) {
      return this.badPassword();
    }

    blobUrl = URL.createObjectURL(blob);
    this.page.showReady(blobUrl);
    this.page.hideDecryptForm();
    this.page.hideProgressBar();

  } else {
    this.page.setProgress(percent);
  }

};

DecryptController.prototype.badPassword = function (a) {
  this.page.hideProgressBar();
  this.page.showError("Incorrect Password!");
};