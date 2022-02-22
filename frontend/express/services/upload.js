const { execSync } = require('child_process');
const archiver = require('archiver');
const config = require('config');
const fs = require('fs');
const path = require('path');
const streamBuffers = require('stream-buffers');

const IncomingForm = require('formidable').IncomingForm;
const uuidv4 = require('uuid/v4');

const uploadDoneFileName = 'upload_done'
const metadataFileName = 'metadata.json'

class Uploader {

  constructor(uploadDir, client) {
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
      if (!fs.existsSync(uploadDir)) {
        throw new Error(
          `${uploadDir} is not a valid directory and could not be created.`);
      }
    }
    this.uploadDir = uploadDir;
    this.client = client;
  }

  upload(req, res) {
    console.log('Processing new upload...');
    var form = new IncomingForm({
      maxFileSize: config.get('uploadService.maxFileSize')
    });

    // Create a unique identifier for this upload.
    let uploadID = uuidv4();
    console.log(`Upload ID: ${uploadID}...`);

    let basePath = path.join(this.uploadDir, uploadID);
    fs.mkdirSync(basePath);
    let uploadPath = path.join(basePath, 'upload');
    fs.mkdirSync(uploadPath);

    form.on('file', (field, file) => {
      let fileName = file.name;

      // TODO(billy): Perform file safety checks.
      // TODO(billy): Render/return errors as HTTP response.
      console.log(
        `Moving file from ${file.path} to ${uploadPath}/${fileName}...`);
      // TODO(billy): Perform asynchronously.
      try {
        fs.renameSync(file.path, path.join(uploadPath, fileName));
      } catch (err) {
        fs.copyFileSync(file.path, path.join(uploadPath, fileName));
      }
    });

    let metadata = {
      name: '',
      patient_age: null,
      patient_height: null,
      patient_sex: null,
    }
    // TODO(billy): Return errors to frontend on invalid inputs instead of
    // silently using default.
    form.on('field', (name, value) => {
      console.log('value',value)
      if (name == 'projectName') {
        metadata.name = value;
      } else if (name == 'age' && !isNaN(Number(value))) {
        metadata.patient_age = Number(value);
      } else if (name == 'height' && !isNaN(Number(value))) {
        metadata.patient_height = Number(value);
      } else if (name == 'sex' && (value == 'MALE' || value == 'FEMALE')) {
        metadata.patient_sex = value;
      }
    })

    // TODO(billy): Return errors to frontend here.
    form.on('end', () => {
      let metadata_json = JSON.stringify(metadata);
      console.log(`Writing metadata file: ${metadata_json}`);
      fs.writeFile(path.join(uploadPath, metadataFileName), metadata_json, function(err) {
        if (err) {
          return console.log(err);
        }
      });
      fs.writeFile(path.join(basePath, uploadDoneFileName), '', function(err) {
        if (err) {
          return console.log(err);
        }
      });

      // Archive as .zip and create Ingestion.
      let absUploadPath = path.resolve(uploadPath);
      let buffer = new streamBuffers.WritableStreamBuffer({
        initialSize: (10 * 1024 * 1024),  // start at 10MB
        incrementAmount: (10 * 1024 * 1024)
      });
      let archive = archiver('zip');

      archive.on('error', (err) => {
        console.log(err);
        res.json({
          'error': err,
        });
      });
      archive.pipe(buffer);
      archive.directory(absUploadPath, false);

      buffer.on('finish', () => {
        this.client.post('/ingestions', {
          uuid: uploadID,
          creation_datetime: new Date().toISOString(),
          state: 'NEW',
          error_str: '',
          name: metadata.name,
          file_archive_bytes: buffer.getContentsAsString('base64')
        }, function(err, postReq, postRes, obj) {
          if (err) {
            console.log('Error during post to /ingestions:');
            console.log('%d -> %j', postRes.statusCode, postRes.headers);
            console.log('%j', obj);
            res.json(obj);
          } else {
            res.json({
              'id': uploadID,
            });
          }
        });
      });
      archive.finalize();

      console.log(`Finished processing upload ${uploadID}`);

    });
    form.parse(req);
  }
}
exports.Uploader = Uploader;
