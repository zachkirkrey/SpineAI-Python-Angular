function showQuestionSpec() {
  if ($('#question_spec').is(':visible')) {
    $('#question_spec').slideUp();
    $('#toggle_question_spec').html('Show Spec');
  } else {
    $('#question_spec').slideDown();
    $('#toggle_question_spec').html('Hide Spec');
  }
}

function readCSV($input) {
  return new Promise((resolve, reject) => {
    files = $input.prop('files');
    if (files && files[0]) {
      let reader = new FileReader();
      reader.onload = (e) => {
        try {
          resolve($.csv.toObjects(e.target.result));
        } catch(err) {
          showError(err.message);
          reject(err);
        }
      }
      reader.readAsText(files[0]);
    } else {
      showError('Questions CSV file not provided.');
      reject('Questions CSV file not provided.');
    }
  });
}

function readImageData(file) {
  return new Promise((resolve, reject) => {
    if (file) {
      let reader = new FileReader();
      reader.onload = (e) => {
        resolve(e.target.result);
      }
      reader.readAsDataURL(file)
    } else {
      reject()
    }
  });
}

function getQuestionsHTML(imageNum, imageFile, questions) {
  requiredFields = [
    "Multiselect",
    "Question Text"
  ];
  numResponses = 10;
  for (var i = 1; i <= numResponses; i++ ) {
    requiredFields.push(`Response ${i}`);
  }

  questionHTML = '';
  for (var i = 0; i < questions.length; i++) {
    question = questions[i];
    for (field of requiredFields) {
      if (!question.hasOwnProperty(field)) {
        err = `Question #${i + 1} is missing field "${field}"`;
        showError(err);
        throw err;
      }
    }

    imageName = imageFile['name'];

    questionText = question['Question Text'];
    questionHTML += `<p>${questionText}</p>`;

    multiselect = question['Multiselect'];
    if (multiselect == 'Y' || multiselect == 'N') {
      inputType = 'radio';
      if (multiselect == 'Y') inputType = 'checkbox';

      for (var r = 1; r < numResponses; r++) {
        response = question['Response ' + r];
        if (response) {
          questionHTML += `
            <div class="response">
              <input type="${inputType}" id="q${i}_${response}" name="${imageName}|${questionText}" value="${response}" />
              <label for="q${i}_${response}">${response}</label>
            </div>
          `;
        }
      }
    } else if (multiselect == '') {
      questionHTML += `
        <div class="response">
          <input type="textarea" name="${imageName}|${questionText}" rows="3" cols="30"/>
        </div>
      `;
    } else {
      err = `Invalid "Multiselect" value: ${multiselect}`;
      showError(err);
      throw err;
    }
  }
  return questionHTML;
}

function getSurveyImageHTML(i, numImages, imageData, questions, imageFile) {
  questionsHTML = getQuestionsHTML(i, imageFile, questions);

  return `
    <span class="survey_question">
      <div class="row">
        <p>Currently tagging image ${i + 1}/${numImages} - ${imageFile['name']}</p>
      </div>
      <div class="row flex-grow-container">
        <div>
          <img src="${imageData}"/>
        </div>
        <div class="questions-container">
          ${questionsHTML}
        </div>
      </div>
    </span>
  `;
}

async function loadSurvey($imageInput, questions) {
  let imageFiles = $imageInput.prop('files');
  if (!imageFiles || imageFiles.length == 0) {
    showError('No image files provided.');
    throw 'No image files proivded.';
  }

  let numImages= imageFiles.length;
  let nextImageModifier = '';
  if (numImages == 1) nextImageModifier = 'disabled';
  surveyHTML = `
    <div class="row">
      <button id="submitSurvey">Export Responses as CSV</button>
    </div>
  `;

  let questionsHTML = '';
  for (let i = 0; i < imageFiles.length; i++) {
    let file = imageFiles[i];
    let imageData = await readImageData(file);
    questionsHTML += getSurveyImageHTML(i, imageFiles.length, imageData, questions, file);
  }
  surveyHTML += `
    <form id="survey_form">
    <div id="survey_questions">${questionsHTML}</div>
    </form>
    <div class="nav-buttons-container left-container clearfix">
      <span id="surveyMetadata" data-activeimage="1" data-numimages="${numImages}"></span>
      <button id="prevImage" disabled>&lt; Prev Image</button>
      <button id="nextImage" ${nextImageModifier}>Next Image &gt;</button>
    </div>
  `;

  $('#survey').append(surveyHTML);
}

function activateQuestion(i) {
  $('.survey_question').hide();
  $(`.survey_question:nth-child(${i})`).show();
}

function nextImage() {
  let activeImage = parseInt($('#surveyMetadata').data('activeimage'));
  let numImages = parseInt($('#surveyMetadata').data('numimages'));

  if (activeImage >= numImages) return;

  let newImage = activeImage + 1;
  activateQuestion(newImage);
  $('#surveyMetadata').data('activeimage', newImage.toString());

  $('#prevImage').prop('disabled', false);
  if (newImage >= numImages) $('#nextImage').prop('disabled', true);
}

function prevImage() {
  let activeImage = parseInt($('#surveyMetadata').data('activeimage'));
  let numImages = parseInt($('#surveyMetadata').data('numimages'));

  if (activeImage <= 1) return;

  let newImage = activeImage - 1;
  activateQuestion(newImage);
  $('#surveyMetadata').data('activeimage', newImage.toString());

  $('#nextImage').prop('disabled', false);
  if (newImage <= 1) $('#prevImage').prop('disabled', true);
}

function loadSurveyHandlers() {
  $('#prevImage').click(prevImage);
  $('#nextImage').click(nextImage);

  $('#submitSurvey').click((e) => {
    let csvRows = [];

    csvRows.push(["Image File Name", "Responder Name", "Question", "Response"].join(','));

    responses = $('form#survey_form').serializeArray();
    console.log(responses);

    responderName = $('#name').val();
    for (response of responses) {
      responseName = response['name'].split('|');
      imageName = responseName[0];
      questionText = responseName[1];
      responseText = response['value'];
      csvRows.push(
        [imageName, responderName, questionText, responseText].join(','));

    }

    var csvString = csvRows.join("\r\n");
    var a = document.createElement('a');
    a.href = 'data:attachment/csv,' + encodeURIComponent(csvString);
    a.target = '_blank';
    a.download = 'xtagger.csv';
    document.body.appendChild(a);
    a.click();
  });
}

function clearStatus() {
  $('#status').html('');
}

function showStatus(txt) {
  $('#status').html(`<p>${txt}</p>`);
}

function showError(txt) {
  $('#status').html(`<p class="error">${txt}</p>`);
}

$(function() {
  $('form#setup_tagging').submit(async (event) => {
    event.preventDefault();

    showStatus('Loading survey...');

    let data = $('form#setup_tagging :input').serializeArray();

    // Read questions CSV.
    questions = await readCSV($('input#questions'));

    await loadSurvey($('input#images'), questions);
    loadSurveyHandlers();

    clearStatus();
    $('#setup_tagging').slideUp();
  });
});
