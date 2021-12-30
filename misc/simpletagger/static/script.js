function readCSV($input) {
  return new Promise((resolve, reject) => {
    files = $input.prop('files');
    if (files && files[0]) {
      let reader = new FileReader();
      reader.onload = (e) => {
        try {
          resolve($.csv.toArrays(e.target.result));
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

function loadSurvey(input_csv) {
  // Validate CSV
  if (input_csv.length <= 1) {
    throw `CSV must contain 2 or more rows. Got: ${input_csv.length}.`;
  }
  for (let i = 1; i < input_csv.length; i++) {
    row = input_csv[i];
    if (row.length < 3) {
      throw `CSV row #${i+1} does not contain at least 3 items. Got: ${row.lengoh}.`;
    }
  }

  let numRows = input_csv.length - 1;
  let nextRowModifier = '';
  if (numRows == 1) nextRowModifier = 'disabled';

  surveyHMTL = `
    <span id="surveyMetadata" data-activerow="1" data-numrows="${numRows}"></span>
    <div class="row">
      <button id="submitSurvey">Export Responses as CSV</button>
    </div>
    <div class="left-container clearfix">
      <button id="prevRow" disabled>&lt; Prev Row</button>
      <button id="nextRow" ${nextRowModifier}>Next Row &gt;</button>
    </div>
  `;

  window.data = {
    headers: input_csv[0],
    numRows: numRows
  }

  let questionsHTML = '';
  for (let i = 1; i < input_csv.length; i++) {
    let row = input_csv[i];
    let patient = {
      mrn: row[0],
      report: row[1],
      accession: row[2]
    };
    questionsHTML += `
      <span class="survey_question">
        <div class="row">
          <p>Currently tagging Patient #${i} of ${input_csv.length - 1}</p>
          <p>${window.data.headers[0]}: ${patient.mrn}</p>
          <p>${window.data.headers[2]}: ${patient.accession}</p>
        </div>
        <div class="row questions-container">
          <input type="hidden" name="row${i}_mrn" value="${patient.mrn}" />
          <input type="hidden" name="row${i}_accession" value="${patient.accession}" />
          <p>Spondylothesis Presence?</p>
          <input type="radio" id="row${i}_yes" name="row${i}_spondy" value="1" />
          <label for="row${i}_yes">Yes</label>
          <br /><br />
          <input type="radio" id="row${i}_no" name="row${i}_spondy" value="0" />
          <label for="row${i}_no">No</label>
        </div>
        <div class="row">
          <div style="width: 50%;">
            <textarea rows="50" cols="80">${patient.report}</textarea>
          </div>
        </div>
      </span>
    `;
  }

  surveyHMTL += `
    <form id="survey_form">
    <div id="survey_questions">${questionsHTML}</div>
    </form>`;

  $('#survey').append(surveyHMTL);
}

function activateRow(i) {
  $('.survey_question').hide();
  $(`.survey_question:nth-child(${i})`).show();
}

function nextRow() {
  let activeRow = parseInt($('#surveyMetadata').data('activerow'));
  let numRows = parseInt($('#surveyMetadata').data('numrows'));

  if (activeRow >= numRows) return;

  let newRow = activeRow + 1;
  activateRow(newRow);
  $('#surveyMetadata').data('activerow', newRow.toString());

  $('#prevRow').prop('disabled', false);
  if (newRow >= numRows) $('#nextRow').prop('disabled', true);
}

function prevRow() {
  let activeRow = parseInt($('#surveyMetadata').data('activerow'));
  let numRows = parseInt($('#surveyMetadata').data('numrows'));

  if (activeRow <= 1) return;

  let newRow = activeRow - 1;
  activateRow(newRow);
  $('#surveyMetadata').data('activerow', newRow.toString());

  $('#nextRow').prop('disabled', false);
  if (newRow <= 1) $('#prevRow').prop('disabled', true);
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

function updateHighlight() {
  values = $(this).val().split(',');
  for (let i = 0; i < values.length; i++) {
    values[i] = values[i].trim();
  }
  $('textarea').highlightWithinTextarea({
    highlight: values
  });
}

function loadSurveyHandlers() {
  $('#prevRow').click(prevRow);
  $('#nextRow').click(nextRow);

  $('#submitSurvey').click((e) => {
    let csvRows = [];
    csvRows.push([window.data.headers[0], window.data.headers[2], "Spondylothesis"]);

    for (let i = 1; i <= window.data.numRows; i++) {
      csvRows.push([
        $(`input[name="row${i}_mrn"]`).val(),
        $(`input[name="row${i}_accession"]`).val(),
        $(`input[name="row${i}_spondy"]:checked`).val()
      ]);
    }

    var csvString = csvRows.join("\r\n");
    var a = document.createElement('a');
    a.href = 'data:attachment/csv,' + encodeURIComponent(csvString);
    a.target = '_blank';
    a.download = 'simpletagger.csv';
    document.body.appendChild(a);
    a.click();
  });
}

$(function() {
  $('form#setup_tagging').submit(async (event) => {
    event.preventDefault();

    showStatus('Loading survey...');

    // Read questions CSV.
    input = await readCSV($('input#input'));

    try {
      loadSurvey(input);
    } catch (err) {
      showError(err.message);
    }
    loadSurveyHandlers();

    clearStatus();
    $('#setup_tagging').slideUp();
    $('#survey').show();
    updateHighlight.bind($('input#highlight'))();
  });
  $('input#highlight').keyup(() => {
    updateHighlight.bind($('input#highlight'))()
  });
});
