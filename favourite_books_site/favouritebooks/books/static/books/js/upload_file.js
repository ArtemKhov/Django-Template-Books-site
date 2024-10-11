document.getElementById('file-upload').onchange = function(e) {
  document.querySelector('.custom-file-upload span').innerText = e.target.files[0].name;
};