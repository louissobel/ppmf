"use strict";

// Page View for encryption controller

var FileInputView = require("./file_input_view")
  , BasePage = require("../core/base_page")
  , blobDelivery = require("../core/blob_delivery")
  , inherits = require("../core/utils").inherits
  , SlideView = require("./slide_view")
  ;

var EncryptPage = module.exports = function () {};
inherits(EncryptPage, BasePage);

EncryptPage.prototype.init = function () {
  BasePage.prototype.init.call(this);

  this.fileInput = document.getElementById("file-select");
  this.fileBrowseButton = document.getElementById("file-select-button");
  this.fileBrowseDisplay = document.getElementById("file-select-display");

  this.fileInputView = new FileInputView(this.fileInput, this.fileBrowseButton, this.fileBrowseDisplay);
  this.fileInputView.onchange = this.handleFileChange.bind(this);

  this.doneLink = document.getElementById("done-link");
  this.dropboxLinkContainer = document.getElementById("dropbox-saver-link-container");

  this.slideView = new SlideView(document.getElementById("div-slide-wrapper"));
  this.learnMoreLink = document.getElementById("learn-more-link");
  this.leaveFaqLink = document.getElementById("leave-faq-link");
  this.learnMoreLink.onclick = this.handleLearnMore.bind(this);
  this.leaveFaqLink.onclick = this.handleLeaveFaq.bind(this);

  this.whatNowLink = document.getElementById("what-now-link");
  this.whatNowBox = document.getElementById("what-now-box");
  this.whatNowLink.onclick = this.handleWhatNowClick.bind(this);

  this.tooBigWarning = document.getElementById("too-big-warning");
  this.tooBigSize = document.getElementById("too-big-size");
  this.tooBigEncryptAnyway = document.getElementById("too-big-encrypt-anyway");
  this.tooBigEncryptAnyway.onclick = this.handleEncryptAnywayClick.bind(this);

  return this;
};

EncryptPage.prototype.showReady = function (options, callback) {
  var filename = options.filename + "__encrypted.html";

  blobDelivery.makeLink({
    link: this.doneLink
  , filename: filename
  , blob: options.blob
  , onready: function (err) {
      if (err) {
        return callback(err);
      }

      // Make the dropbox link
      // (empty the container first)
      while (this.dropboxLinkContainer.firstChild) {
        this.dropboxLinkContainer.removeChild(this.dropboxLinkContainer.firstChild);
      }

      blobDelivery.makeLink({
        link: this.dropboxLinkContainer
      , filename: filename
      , blob: options.blob
      , dropboxLink: true
      , onready: function (err) {
          if (err) {
            // Fine. make sure link is not visible though.
            this.dropboxLinkContainer.style.display = "none";
          } else {
            this.dropboxLinkContainer.style.display = "block";
          }
          BasePage.prototype.showReady.call(this);
          return callback(null);
        }.bind(this)
      });

    }.bind(this)
  });

};

EncryptPage.prototype.handleFormSubmit = function () {
  this.doSubmitForm({
    force: false
  });
  return false;
};

EncryptPage.prototype.doSubmitForm = function (options) {
  if (this.submitCallback) {
    var password = this.passwordInput.value
      , selectedFile = this.fileInput.files[0] || null
      ;
    this.submitCallback(password, selectedFile, options.force);
  }
};

EncryptPage.prototype.getDecryptTemplate = function () {
  return document.getElementById("decrypt-template").textContent;
};

EncryptPage.prototype.handleFileChange = function () {
  // Clear out the password if we're showing a ready.
  if (this.readyShowing) {
    this.clearPassword();
  }
  this.focusPassword();
};

EncryptPage.prototype.handleLearnMore = function () {
  this.slideView.rotateLeft();
  return false;
};

EncryptPage.prototype.handleLeaveFaq = function () {
  // If we are on /faq, after we are done rotating, go to /
  if (window.location.pathname.match(/faq$/)) {
    this.slideView.onrotate = function () {
      window.location = "/";
    };
  }
  this.slideView.rotateRight();
  return false;
};

EncryptPage.prototype.focusFileBrowse = function () {
  this.fileBrowseButton.focus();
};

EncryptPage.prototype.handleWhatNowClick = function () {
  this.whatNowBox.style.display = "block";
};

EncryptPage.prototype.handleEncryptAnywayClick = function () {
  this.hideTooBigWarning();
  this.doSubmitForm({
    force: true
  });
  return false;
};

EncryptPage.prototype.showTooBigWarning = function (bytes) {
  var megabytes = Math.floor(100 * bytes / (1000 * 1000)) / 100;
  this.tooBigSize.innerHTML = megabytes;
  this.tooBigWarning.style.display = "block";
};

EncryptPage.prototype.hideTooBigWarning = function () {
  this.tooBigWarning.style.display = "none";
};
