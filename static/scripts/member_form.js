document.addEventListener("DOMContentLoaded", function() {
  const checkbox = document.getElementById("id_phone_visibility")
  const label = document.getElementById("id_label_phone_visibility")

  const file = document.getElementById("id_avatar")
  const filename = document.getElementById("id_filename")

  function updateLabel() {
    if (checkbox.checked) {
      label.textContent = "Visible for all members"
    }
    else {
      label.textContent = "Visible for board only"
    }
  }

  function updateFilename() {
    if (file.files[0]) {
      filename.textContent = file.files[0].name
    }
    else {
      filename.textContent = "Choose file"
    }
  }

  checkbox.addEventListener("change", updateLabel);
  updateLabel();

  file.addEventListener("change", updateFilename);
});
