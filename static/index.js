let text_container = document.querySelector('div.default-text');

$("form.fileUploadForm").on("change", ".file-upload-field", function(){ 
  $(this).parent(".file-upload-wrapper").attr("data-text",$(this).val().replace(/.*(\/|\\)/, ''));
  setTimeout(() => {
    let html = `
        <span class="loader"></span>
        <p>File is uploading this may take a while.....</p>`;
        $("form.fileUploadForm").submit();
        text_container.innerHTML = html;
  },1000);
});