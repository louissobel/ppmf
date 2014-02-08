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

module.exports.blobToDataURI = function (blob, callback) {
  var reader = new FileReader();
  reader.onload = function () {
    callback(null, reader.result);
  };
  reader.readAsDataURL(blob);
};

module.exports.blobToBase64 = function (blob, callback) {
  // http://jsperf.com/blob-base64-conversion

  // TODO: handle error?
  module.exports.blobToDataURI(blob, function (err, result) {
    var base64 = result.substring(result.indexOf(",") + 1);
    callback(null, base64);
  });

};
