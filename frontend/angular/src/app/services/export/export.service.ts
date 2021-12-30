import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ExportService {

  constructor() { }

  public getCsvExport(studies) {
    let csvContent = "data:text/csv;charset=utf-8,";

    let rows = [];
    console.log(studies);

    let headers = [
      '"SpineAI UUID"',
      '"Study Instance UID"',
      '"Accession Number"',
      '"Patient Name"',
      '"Creation Datetime"',
      '"Num Narrow Canal Slices"',
      '"Surgery Recommended"',
      '"Canal Areas (mm^2)"'
    ];
    rows.push(headers);

    studies.forEach((study) => {
      let row = [];
      row.push(study.uuid);
      row.push(study.study_instance_uid);
      row.push(study.accession_number);
      row.push(study.patient_name);
      row.push(study.creation_datetime);

      let report = study.Reports[0];
      row.push(report.num_narrow_slices);
      row.push(report.surgery_recommended);

      let canalSegmentation = study.CanalSegmentations[0];
      row.push(...canalSegmentation.canal_areas);

      rows.push(row);
    });

    rows.forEach(function(rowArray) {
      let rowTxt = rowArray.join(',');
      csvContent += rowTxt + '\r\n';
    });

    return csvContent;
  }
}
