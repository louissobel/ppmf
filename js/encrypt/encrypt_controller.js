"use strict";

var EncryptPage = require("./encrypt_page")
  , blobs = require("../core/blobs")
  , blobDelivery = require("../core/blob_delivery")
  , unsupportedBrowser = require("../core/unsupported_browser")
  , aes = require("../core/aes")
  , passwordChecking = require("../core/password_checking")
  , HtmlWrapper = require("./html_wrapper")
  ;

var SHOW_PROGRESS_BAR_SIZE_THRESHOLD = aes.CHUNK_SIZE * 4;
var TRIGGER_TOO_BIG_WARNING_SIZE_THRESHOLD = 1000 * 1000 * 24;

var EncryptController = module.exports = function () {
  if (!this.onSupportedBrowser()) {
    return unsupportedBrowser();
  }

  this.page = (new EncryptPage()).init();
  this.page.submitCallback = this.submitEncrypt.bind(this);
};

EncryptController.prototype.submitEncrypt = function (password, file, force) {
  force = force || false;

  if (!file) {
    this.encryptError("You need to pick a file");
    this.page.focusFileBrowse();
    return false;
  }

  if (password === "") {
    this.encryptError("You need to pick a password");
    this.page.focusPassword();
    return false;
  }

  // If our file is huge, we should bork at this point.
  if  (file.size > TRIGGER_TOO_BIG_WARNING_SIZE_THRESHOLD && !force) {
    this.page.showTooBigWarning(file.size);
    // make sure any old error is hidden
    this.page.hideError();
    // make sure any old result is hidden
    this.page.hideReady();
    return false;
  }

  this.page.disableForm();

  if (file.size > SHOW_PROGRESS_BAR_SIZE_THRESHOLD) {
    this.page.setProgress(0);
    this.page.showProgressBar();
  }

  // make sure any old error is hidden
  this.page.hideError();
  // make sure any old result is hidden
  this.page.hideReady();
  // make sure we're not showing a too big warning
  this.page.hideTooBigWarning();

  // turn the file into a binary string
  blobs.blobToBase64(file, function (err, result) {
    this.decryptedObj = {
      b64plaintext: result
    , mimetype: file.type
    , filename: file.name
    };
    var jsonifiedString = JSON.stringify(this.decryptedObj)
      , passwordCheckedString = passwordChecking.wrap(jsonifiedString)
      ;
    aes.encrypt(passwordCheckedString, password, this.encryptProgressCallback.bind(this));
  }.bind(this));

};

EncryptController.prototype.encryptProgressCallback = function (err, percent, done, result) {
  if (err) {
    this.encryptError(err + "");
  } else if (done) {
    var htmlWrapper = new HtmlWrapper(this.page.getDecryptTemplate())
      , htmlString = htmlWrapper.wrap({
                       ciphertext: result
                     , filename: this.decryptedObj.filename
                     })
      , htmlBlob = blobs.binaryStringToBlob(htmlString, "text/html")
      ;

    this.page.showReady({
      filename: this.decryptedObj.filename
    , blob: htmlBlob
    }, function (err) {
      if (err) {
        return this.encryptError(err);
      }
      this.page.hideProgressBar();
      this.page.enableForm();
    }.bind(this));

  } else {
    this.page.setProgress(percent);
  }
};

EncryptController.prototype.encryptError = function (message) {
  // Make sure we don't show an old result.
  this.page.hideReady();
  this.page.showError(message);
  this.page.enableForm();
};

EncryptController.prototype.onSupportedBrowser = function () {
  return blobDelivery.canDeliverBlobDownloads() && blobDelivery.canReadBlob();
};
