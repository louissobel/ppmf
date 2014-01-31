"use strict";

var EncryptPage = require("./encrypt_page")
  , base64 = require("../core/base64")
  , aes = require("../core/aes")
  , HtmlWrapper = require("./html_wrapper")
  ;

var SHOW_PROGRESS_BAR_SIZE_THRESHOLD = 1024;

var EncryptController = module.exports = function () {
  this.page = (new EncryptPage()).init();
  this.page.submitCallback = this.submitEncrypt.bind(this);
};

EncryptController.prototype.submitEncrypt = function (password, file) {
  if (password === "") {
    this.page.showError("You have to pick a password!");
    return;
  }

  if (!file) {
    this.page.showError("Select a file!");
    return;
  }

  if (file.size > SHOW_PROGRESS_BAR_SIZE_THRESHOLD) {
    this.page.setProgress(0);
    this.page.showProgressBar();
  }

  // make sure any old error is hidden
  this.page.hideError();
  // make sure any old result is hidden
  this.page.hideReady();

  // turn the file into a base64 string
  base64.blobToB64(file, function (err, result) {
    var decryptedObj = {
          b64plaintext: result
        , mimetype: file.type
        }
      , jsonifiedString = JSON.stringify(decryptedObj)
      , b64jsonifiedString = btoa(jsonifiedString)
      ;
    aes.encrypt(b64jsonifiedString, password, this.encryptProgressCallback.bind(this));
  }.bind(this));

};

EncryptController.prototype.encryptProgressCallback = function (err, percent, done, result) {
  if (err) {
    this.page.showError(err + "");
  } else if (done) {
    var htmlWrapper = new HtmlWrapper(this.page.getDecryptTemplate())
      , htmlBlob = htmlWrapper.wrap(result)
      , blobUrl = URL.createObjectURL(htmlBlob)
      ;

    this.page.hideProgressBar();
    this.page.showReady(blobUrl);

  } else {
    this.page.setProgress(percent);
  }
};
