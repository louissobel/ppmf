"use strict";

/* Whitelist which mimetypes are available to be "Viewed" - in a browser or inline */

module.exports.canViewInWindow = function (mimeType) {
  return _matchAny(mimeType, [
    "image/.+" // All images.
  , "text/.+" // All text.
  , "application/pdf"
  , "application/javascript"
  ]);
};

var _matchAny = function (mimeType, regexStringList) {
  var i;
  for (i=0; i<regexStringList.length; i++) {
    if (mimeType.match(new RegExp(regexStringList[i]))) {
      return true;
    }
  }
  return false;
};
