document.addEventListener("DOMContentLoaded", function() {
  const checkbox = document.getElementById("id_club_owner");
  const owner = document.getElementById("id_owner");
  const keeper = document.getElementById("id_keeper");
  const user_id = document.getElementById("boat_form").dataset.user_id;

  function updateFields() {
    if (checkbox.checked) {
      owner.disabled = true;
      keeper.disabled = false;
      owner.value = "";
    }
    else {
      owner.disabled = false;
      keeper.disabled = true;
      keeper.value = "";
      owner.value = user_id;
    }
  }
  checkbox.addEventListener("change", updateFields);
  updateFields();
});