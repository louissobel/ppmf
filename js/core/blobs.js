"use strict";

module.exports.binaryStringToBlob = function (byteCharacters, contentType) {

  // http://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript
  var sliceSize = 512
    , byteArrays = []
    ;

  var offset
    , slice
    , byteNumbers
    , i
    ;

  for (offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    slice = byteCharacters.slice(offset, offset + sliceSize);

    byteNumbers = new Array(slice.length);
    for (i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    byteArrays.push(new Uint8Array(byteNumbers));
  }

  return new Blob(byteArrays, {type: contentType});
};

module.exports.blobToBase64 = function (blob, callback) {
  // http://jsperf.com/blob-base64-conversion

  // TODO: handle error?

  var reader = new FileReader();

  reader.onload = function() {
    var base64 = reader.result.substring(reader.result.indexOf(",") + 1);
    callback(null, base64);
  };

  reader.readAsDataURL(blob);
};

module.exports.getBlobUrl = function (blob, callback) {
  // Schedule it for async consistency
  setTimeout(function () {
    callback(null, URL.createObjectURL(blob));
  }, 0);
};
