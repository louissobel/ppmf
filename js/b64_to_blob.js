"use strict";

var b64ToBlob = module.exports = function (b64Data, contentType) {

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