
var fileViewer = {

  renderFile: function(fileContents) {

    var fileUrl = fileViewer.writeToFile(fileContents);

    var fileViewerObj = $('#fileViewer');
    $('#fileViewer').attr({
        'data': fileUrl,
        'type': 'application/pdf'
      })
      .css('visibility', 'visible');
  },

  writeToFile: function(fileContents) {
    return 'hello-test.pdf';
  },
};

$(function() {
    $('#decryptForm').css('visibility', 'visible').submit(function() {

      var ciphertext = $('#ciphertext').text().trim()
          , password = $("#password").val();
      console.log(password);

      var decrypted = decrypt(ciphertext, password) 
      if (decrypted.success) {
        $('#decryptForm').remove();
        $('#ciphertext').remove();
        fileViewer.renderFile(decrypted.plaintext);
      }

      return false;

    });

    function decrypt(ciphertext, password) {
        //decrypt ciphertext with password here...right now this just returns the base64-decoded text
        return {
          plaintext: atob(ciphertext),
          success: true
        }
    }

})

