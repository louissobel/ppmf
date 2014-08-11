
var passwordProtect = function (url) {

  var pageUrl = 'b/ppmf.html#' + url;

  // Create a new window to the info page.
  chrome.windows.create({
    url: pageUrl
  , width: 520
  , height: 660
  });

};

var handleLinkSelect = function (info) {
  // The srcUrl property is only available for image elements.
  passwordProtect(info.linkUrl);
};

var handleImgSelect = function (info) {
  passwordProtect(info.srcUrl);
};

chrome.contextMenus.create({
  "title" : "Password Protect Linked File"
, "type" : "normal"
, "contexts" : ["link"]
, "onclick" : handleLinkSelect
});

chrome.contextMenus.create({
  "title" : "Password Protect Image"
, "type" : "normal"
, "contexts" : ["image"]
, "onclick" : handleImgSelect
});