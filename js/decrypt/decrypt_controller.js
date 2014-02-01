"use strict";

var DecryptPage = require("./decrypt_page")
  , CryptoJS = require("../core/cryptojs")
  , aes = require("../core/aes")
  , blobs = require("../core/blobs")
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

DecryptController.prototype.decryptProgressCallback = function (error, percent, done, binaryResult) {
  if (error) {
    // for now, assume this means password was bad
    this.badPassword(error);
  } else if (done) {

    var decryptedObject
      , blob
      , blobUrl
      ;

    try {
      decryptedObject = JSON.parse(binaryResult);
    } catch (err) {
      return this.badPassword(err);
    }

    try {
      blob = blobs.binaryStringToBlob(atob(decryptedObject.b64plaintext), decryptedObject.mimetype);
    } catch (err) {
      return this.badPassword(err);
    }

    blobUrl = URL.createObjectURL(blob);
    this.page.showReady(blobUrl, decryptedObject.filename);
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