"use strict";

var NOT_STARTED = 0
  , DOWNLOADING = 1
  , DONE = 2
  ;

var Download = module.exports = function (url, progressCallback) {
  this.url = url;
  this.state = NOT_STARTED;
  this.done = false;
  this.resultBlob = null;

  this.progress = 0;
  this.progressCallback = progressCallback;
  this._start();
};

Download.prototype._start = function () {
  this.xhr = new window.XMLHttpRequest();
  this.xhr.onreadystatechange = this._handleReadyStateChange.bind(this);
  this.xhr.onprogress = function () {
    window.console.log(arguments);
  };
  this.xhr.open("get", this.url, true);
  this.xhr.responseType = "blob";
  this.state = DOWNLOADING;
  this.xhr.send();
};

Download.prototype._handleReadyStateChange = function () {
  if (this.xhr.readyState === 4 && this.xhr.status === 200) {
    var blob = this.xhr.response;
    this.result = blob;
    this.state = DONE;
    this.done = true;
    if (this.progressCallback) {
      this.progressCallback(null, this);
    }
  }
};
