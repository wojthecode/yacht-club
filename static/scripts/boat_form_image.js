document.addEventListener("DOMContentLoaded", function() {

  const file = document.getElementById("id_image")
  const filename = document.getElementById("id_filename")


  function updateFilename() {
    if (file.files[0]) {
      filename.textContent = file.files[0].name
    }
    else {
      filename.textContent = "Choose file"
    }
  }


  file.addEventListener("change", updateFilename);
});
