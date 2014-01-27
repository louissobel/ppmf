"use strict";

module.exports.b64ToBlob = function (b64Data, contentType) {

  // http://stackoverflow.com/questions/16245767/creating-a-blob-from-a-base64-string-in-javascript
  var sliceSize = 512
    , byteCharacters = atob(b64Data)
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

module.exports.blobToB64 = function (blob, callback) {
  // http://jsperf.com/blob-base64-conversion

  // TODO: handle error?

  var reader = new FileReader();

  reader.onload = function() {
    var dataUrl = reader.result
      , base64 = dataUrl.split(",")[1]
      ;

    callback(null, base64);
  };

  reader.readAsDataURL(blob);
};
