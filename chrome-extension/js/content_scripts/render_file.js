window.requestFileSystem = window.requestFileSystem || window.webkitRequestFileSystem;
fs = null;

var filesystem = {

  _errorHandler: function(e) {
    var msg = '';
    switch (e.code) {
      case FileError.QUOTA_EXCEEDED_ERR:
        msg = 'QUOTA_EXCEEDED_ERR';
        break;
      case FileError.NOT_FOUND_ERR:
        msg = 'NOT_FOUND_ERR';
        break;
      case FileError.SECURITY_ERR:
        msg = 'SECURITY_ERR';
        break;
      case FileError.INVALID_MODIFICATION_ERR:
        msg = 'INVALID_MODIFICATION_ERR';
        break;
      case FileError.INVALID_STATE_ERR:
        msg = 'INVALID_STATE_ERR';
        break;
      default:
        msg = 'Unknown Error';
        break;
    };
    document.body.innerHTML = 'Error: ' + msg;
  },

  initFS: function() {
    if (fs !== null) {
      return;
    }

    window.requestFileSystem(window.TEMPORARY, 1024*1024, function(filesystem) {
      fs = filesystem;
    }, filesystem._errorHandler);
  },

  writeToTmpFile: function(pathname, fileContents) {
    //should different files be called different things or just overwrite with tmp?
    pathname = pathname ? pathname : "tmp";
    fs.root.getFile(pathname, {create: true}, function(fileEntry) {
      fileEntry.createWriter(function(fileWriter) {
          
        fileWriter.onwriteend = function(e) {

          //delete this file later?? right now will get overwritten by next one
          var fileUrl = fileEntry.toURL();
          var fileViewerObj = $('#fileViewer');
          $('#fileViewer').attr({
              'data': fileUrl,
              'type': 'application/pdf'
            })
            .css('visibility', 'visible');
        };

        fileWriter.onerror = function(e) {
          console.log('Write failed: ' + e.toString());
        };

        var blob = new Blob([filesystem._base64ToBytes(fileContents)]);

        fileWriter.write(blob);

      }, filesystem._errorHandler);

    }, filesystem._errorHandler);

  },

  _base64ToBytes: function(text) {
    //converts base64 encoded text into blobbbb
    text = atob(text);
    var byteNums = new Array(text.length);
    for (var i in text) {
      byteNums[i] = text.charCodeAt(i);
    }
    return new Uint8Array(byteNums);
  }
}

$(function() {
  filesystem.initFS();

  $('#decryptForm').css('visibility', 'visible').submit(function(evt) {
    evt.preventDefault();

    var ciphertext = $('#ciphertext').text().trim()
        , password = $("#password").val();
    console.log(password);

    var decrypted = decrypt(ciphertext, password) 
    if (decrypted.success) {
      $('#decryptForm').remove();
      $('#ciphertext').remove();
      filesystem.writeToTmpFile("tmp", decrypted.plaintext);
    }

  });

  function decrypt(ciphertext, password) {
      //decrypt ciphertext with password here...right now this just returns the base64-encoded text
      return {
        plaintext: ciphertext,
        success: true
      }
  }

})

