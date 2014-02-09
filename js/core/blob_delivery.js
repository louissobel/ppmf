"use strict";

/* Code to deliver blobs to download and preview links
   wraps browser compatibility issues
*/

var blobs = require("./blobs");

module.exports.canReadBlob = function () {
  // checks that FileReader interface exists
  // and that we have the blob constructor
  // will be used for browser back checkign
  return !!window.FileReader && !!window.Blob;
};

module.exports.canDeliverBlobDownloads = function () {
  // checks if we are able to deliver the blob
  // will be used for browser back checking
  // basically, do we have window.URL and the blob constructor
  var ok = !!window.URL && !!window.Blob;
  if (dataURLFallback()) {
    // then we need to be able to read blob
    ok = ok && module.exports.canReadBlob();
  }
  return ok;
};

var onIE10Plus = function () {
  return !!window.navigator.msSaveBlob;
};

var dataURLFallback = function () {
  // Do we need to fallback to a data URI for download?
  // basically, if we're safari.
  return (
    navigator.userAgent.match(/safari/i) &&
    !navigator.userAgent.match(/chrome/i)
  );
};

module.exports.makeLink = function (options) {
  // returns true if delivered sucessfully
  var link = options.link
    , blob = options.blob
    , filename = options.filename
    , dropboxLink = options.dropboxLink || false
    , onready = options.onready || function () {}
    , onreadyAsync = function (e) { setTimeout(function () { onready(e); }, 0); }
    ;

  if (dropboxLink) {
    return makeDropboxLink(options);
  }

  if (!module.exports.canDeliverBlobDownloads()) {
    return onreadyAsync(new Error("Unable to deliver download"));
  }

  // OK, check first if we are IE 10+
  if (onIE10Plus()) {
    link.onclick = function () {
      window.navigator.msSaveOrOpenBlob(blob, filename);
      return false;
    };
    return onreadyAsync();
  }

  // We need to check if we can degrade to an object URL
  // SHIT this all needs to be made async again. Or, handle the async on click?
  // no, needs to have the data url ready
  if (dataURLFallback()) {
    // TODO use a data URL
    blobs.blobToDataURI(blob, function (err, uri) {
      link.href = uri;
      link.download = filename;
      onready();
    });
  }

  // Otherwise, just create and set the fucking blob URL
  // Assume we have window.URL available?
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  onreadyAsync();

};

var makeDropboxLink = function (options) {
  var blob = options.blob
    , linkContainer = options.link
    , filename = options.filename
    , onready = options.onready || function () {}
    , onreadyAsync = function (e) { setTimeout(function () { onready(e); }, 0); }
    ;

  if (!window.Dropbox) {
    return onreadyAsync(new Error("Dropbox not available"));
  }

  if (!window.Dropbox.isBrowserSupported()) {
    return onreadyAsync(new Error("Browser not supported for dropbox"));
  }

  // Enforce 10MB size limit.
  if (blob.size / (1024 * 1024) > 10) {
    return onreadyAsync(new Error("File too big for dropbox uplaod"));
  }

  blobs.blobToDataURI(blob, function (err, uri) {
    if (err) {
      return onready(err);
    }
    // JANK JANK JANK
    // work around bug in Saver API (or undocumented limit)
    // Known good length
    if (uri.length > 1048291)  {
      return onready(new Error("File too big for undocumented limit"));
    }

    var link = window.Dropbox.createSaveButton(uri, filename);
    linkContainer.appendChild(link);
    onready();
  });

};