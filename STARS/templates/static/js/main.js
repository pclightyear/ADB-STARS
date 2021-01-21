function show_spinner() {
  document.getElementById("schedule_form").style.visibility = "hidden";
  document.getElementById("spinner-border").style.visibility = "visible";
}

function check_password () {
  var password = document.getElementById("password").value;
  var password2 = document.getElementById("password2").value;
  var submit_form = document.getElementById("submit_form");
  if (password != password2) {
    alert("Passwords not consist.");    
    // submit_form.addEventListener("submit", function(event){
    //   event.preventDefault()
    // });
}}

function repeat_password () {        
  var password = document.getElementById("password").value;
  document.getElementById("password2").value = password;        
}

function delete_equipment(eid) {
  var input_value = document.getElementById("input_value").value = eid;
  document.getElementById("submit_button").click();  
}

function project_action (action) {
  var input_value = document.getElementById("input_value").value = action;
  document.getElementById("submit_button").click();
}

function delete_project (pid) {
  var input_value = document.getElementById("input_value").value = pid;
  document.getElementById("submit_button").click();
}

function change_progress_bar () {
  var progress = document.getElementById("progress").value;
  var progress_bar = document.getElementById("progress_bar");
  var percentage = progress.concat("%");
  progress_bar.style.width = percentage;
  progress_bar.innerHTML = percentage;
}

function add_target_table () {
  var table = document.getElementById('target_table');
  var row = table.insertRow(-1);
  var cell0 = row.insertCell(0);
  var cell1 = row.insertCell(1);
  var cell2 = row.insertCell(1);
  cell0.innerHTML = '<input type="text"  class="form-control" id="target_name">';
  cell1.innerHTML = '<input type="number" step="0.01"  class="form-control" id="ra">';
  cell2.innerHTML = '<input type="number" step="0.01"  class="form-control" id="dec">';
}

function add_participant_table () {
  var table = document.getElementById('participant_table');
  var row = table.insertRow(-1);
  var cell0 = row.insertCell(0);
  var cell1 = row.insertCell(1);
  var cell2 = row.insertCell(1);
  cell0.innerHTML = '<input type="text"  class="form-control" id="participant_uid">';
  cell1.innerHTML = '<input type="text"   class="form-control" id="participant_name">';
  cell2.innerHTML = '<input type="email"   class="form-control" id="participant_email">';
}