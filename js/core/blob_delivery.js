"use strict";

/* Code to deliver blobs to download and preview links
   wraps browser compatibility issues
*/

var blobs = require("./blobs");

module.exports.canReadBlob = function () {
  // checks that FileReader interface exists and everythign
  // will be used for browser back checkign
  return !!window.FileReader;
};

module.exports.canDeliverBlobDownloads = function () {
  // checks if we are able to deliver the blob
  // will be used for browser back checking
  // basically, do we have window.URL
  var ok = !!window.URL;
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
    , onready = options.onready || function () {}
    , onreadyAsync = function (e) { setTimeout(function () { onready(e); }, 0); }
    ;

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
