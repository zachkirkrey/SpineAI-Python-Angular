const config = require('config');
const createCsvWriter = require('csv-writer').createObjectCsvStringifier;

const csvConfig = config.get('api.json_to_csv');

/**
 * Returns a CSV string for the given reports.
 *
 * @param {Array} reports - JSON reports to process.
 * @param {string} csvcol - Optional multi column to output. Currently supports
 *   'canal_areas', 'canal_heights', or 'canal_widths'. If omitted, assumes
 *   'canal_areas'.
 * @returns {string}
 */
function sendCsv(reports, csvcol = 'canal_areas') {
  // Prepare headers.
  headers = [];
  for (let key in csvConfig) {
    let keyId = key.toLowerCase().replace('/\s/g', '_');
    headers.push({
      id: keyId,
      title: key
    });
  }
  if (csvcol == 'canal_heights') {
    headers.push({
      id: 'canal_height_unit',
      title: 'Canal Vertical Diameter Unit'
    })
    for (let i = 0; i < 80; i++) {
      let keyId = `canal_height_${i}`;
      headers.push({
        id: keyId,
        title: `Slice ${i} - Canal Vertical Diamenter`
      });
    }
  } else if (csvcol == 'canal_widths') {
    headers.push({
      id: 'canal_width_unit',
      title: 'Canal Horizontal Diameter Unit'
    })
    for (let i = 0; i < 80; i++) {
      let keyId = `canal_width_${i}`;
      headers.push({
        id: keyId,
        title: `Slice ${i} - Canal Horizontal Diamenter`
      });
    }
  } else {
    for (let i = 0; i < 80; i++) {
      let keyId = `canal_area_${i}`;
      headers.push({
        id: keyId,
        title: `Slice ${i} - Canal Area (mm^2)`
      });
    }
  }

  csvWriter = createCsvWriter({
    header: headers
  });

  // Process reports.
  let records = [];
  reports.forEach(report => {
    if (report.type.toLowerCase() != 'json') return;

    let study = report.Studies[0];
    let reportJson = JSON.parse(report.report_bytes);
    if (!reportJson) {
      return;
    }

    record = {};
    for (let key in csvConfig) {
      let keyId = key.toLowerCase().replace('/\s/g', '_');
      record[keyId] = eval(csvConfig[key]);
    }

    // Write CSV columns for multi columns.
    if (csvcol == 'canal_heights') {
      let allCanalHeights = reportJson.measurements.geisinger.canal_heights;
      record['canal_height_unit'] = allCanalHeights[0]['unit'];
      for (let i = 0; i < 80; i++) {
        let keyId = `canal_height_${i}`;
        if (allCanalHeights.length > i) {
          record[keyId] = allCanalHeights[i]['display_height'];
        }
      }
    } else if (csvcol == 'canal_widths') {
      let allCanalWidths = reportJson.measurements.geisinger.canal_widths;
      record['canal_width_unit'] = allCanalWidths[0]['unit'];
      for (let i = 0; i < 80; i++) {
        let keyId = `canal_width_${i}`;
        if (allCanalWidths.length > i) {
          record[keyId] = allCanalWidths[i]['display_width'];
        }
      }
    } else {
      let allCanalAreas = reportJson.canal_segmentation.all_canal_areas;
      for (let i = 0; i < 80; i++) {
        let keyId = `canal_area_${i}`;
        if (allCanalAreas.length > i) {
          let area = parseFloat(allCanalAreas[i]);
          record[keyId] = area.toFixed(2);
        }
      }
    }

    records.push(record);
  });

  return(csvWriter.getHeaderString() +
         csvWriter.stringifyRecords(records));
}

exports.sendCsv = sendCsv;
