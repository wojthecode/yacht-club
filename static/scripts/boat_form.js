document.addEventListener("DOMContentLoaded", function() {
  const checkbox = document.getElementById("id_club_owner");
  const owner = document.getElementById("id_owner");
  const keeper = document.getElementById("id_keeper");
  const user_id = document.getElementById("boat_form").dataset.user_id;
  const club_owner = document.getElementById("boat_form").dataset.club_owner;

  var keepers;
  if (club_owner) {
    keepers = Array.from(keeper.selectedOptions).map(option => option.value);
  }

  function updateFields() {
    if (checkbox.checked) {
      owner.disabled = true;
      keeper.disabled = false;
      owner.value = "";
      if (club_owner) {
        Array.from(keeper.options).forEach(option => {
          option.selected = keepers.includes(option.value);
        });
      }
    }
    else {
      owner.disabled = false;
      keeper.disabled = true;
      owner.value = user_id;
      keeper.value = "";
    }
  }

  checkbox.addEventListener("change", updateFields);
  updateFields();
});