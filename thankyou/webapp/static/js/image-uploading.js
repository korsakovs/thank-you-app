let progressBarArea = document.getElementById('progress-area');
let progressBar = document.getElementById('progress-bar');

let alertMessage = document.getElementById('alert-message');
let successMessage = document.getElementById('success-message');

let form = document.getElementById('my-form');

let dropArea = document.getElementById('drop-area');
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, unhighlight, false);
});

function showError(msg) {
}

function hideError() {
}

function highlight(e) {
  dropArea.classList.add('highlight');
}

function unhighlight(e) {
  dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
  if (e.dataTransfer.files.length > 1) {
  }
  handleFiles(e.dataTransfer.files);
}

function handleFiles(files) {
  hideMessages()
  initializeProgress()
  uploadFile(files[0])
}

function uploadFile(file) {
  var url = '/app/image-uploading/file'
  var xhr = new XMLHttpRequest()
  var formData = new FormData()
  xhr.open('POST', url, true)

  // Add following event listener
  xhr.upload.addEventListener("progress", function(e) {
    updateProgress((e.loaded * 100.0 / e.total) || 100)
  })

  xhr.addEventListener('readystatechange', function(e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // Done. Inform the user
      resetForm();
      setTimeout(() => {
        showSuccessMessage();
        hideProgress();
      }, 500);
    }
    else if (xhr.readyState == 4 && xhr.status != 200) {
      // Error. Inform the user
      resetForm();
      setTimeout(() => {
        showAlertMessage();
        hideProgress();
      }, 500);
    }
  });

  formData.append('file', file)
  setTimeout(() => {
    xhr.send(formData);
  }, 500);
}

function initializeProgress() {
  progressBarArea.setAttribute("style","display:flex");
  progressBar.setAttribute("style","width:0%");
}

function updateProgress(percent) {
  progressBar.setAttribute("style","width:" + percent + "%");
}

function hideProgress() {
  progressBarArea.setAttribute("style","display:none");
}

function hideMessages() {
  alertMessage.setAttribute("style","display:none");
  successMessage.setAttribute("style","display:none");
}

function showSuccessMessage() {
  successMessage.setAttribute("style","display:block");
}

function showAlertMessage() {
  alertMessage.setAttribute("style","display:block");
}

function resetForm() {
  form.reset();
}
