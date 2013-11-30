/*
Code for Chrome extension. Eventually this should detect a dropbox preview window and add the link to open the html file in a new tab.
For now, copy and paste this code while a preview window for a file is open on dropbox site.
JS to decrypt the html is already in html file, executes when opened in the non-sandboxed tab.
*/

$(function() {
	$('#file-viewer-container').on('DOMNodeInserted', function(e) {
		var fileSrc = $('.preview').find('iframe').attr('src');
		var linkToDecrypt = $('<a href="' + fileSrc + '" target="_blank" class="cryptbox-decrypt-link">Decrypt meee</a>');
		$('.filename').children('.cryptbox-decrypt-link').remove();
		$('.filename').append(linkToDecrypt);
	});
});