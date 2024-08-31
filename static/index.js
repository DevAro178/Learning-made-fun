$("form.fileUploadForm").on("change", ".file-upload-field", function(){ 
  $(this).parent(".file-upload-wrapper").attr("data-text",$(this).val().replace(/.*(\/|\\)/, ''));
  setTimeout(() => {
      $("form.fileUploadForm").submit();
  },2000);
});