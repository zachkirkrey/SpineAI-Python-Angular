const fs = require('fs');
const path = require('path');

const glob = require('glob');

var cache = require('memory-cache');


/**
 * Creates a search index object based on given study metadata JSON objects.
 */
generate_index = (metadatas) => {
  return metadatas;
}

error_obj = (err) => {
  return err.toString();
}

/**
 * Reflect returns a promise that always succeeds, but with a status of the
 * inner promise.
 */
reflect = (promise) => {
  return promise.then(function(v) { return { value:v, status: 'resolved' } },
                      function(e) { return { error:e, status: 'rejected' } });
}

class Indexer {

  constructor(uploadDir) {
    if (!fs.existsSync(uploadDir)) {
      throw new Error(`${uploadDir} is not a valid directory.`);
    }
    this.uploadDir = uploadDir;
  }

  getIndex(req, res) {
    console.log('Generating search index...');

    let index = cache.get('index');
    if (index) {
      res.json(index);
      return;
    }

    glob(path.join(this.uploadDir, '*/metadata.json'), (err, files) => {
      if (err) {
        res.json(error_obj(err));
        return;
      }

      let promises = [];

      files.forEach(file_path => {
        promises.push(new Promise((resolve, reject) => {
          fs.readFile(file_path, 'utf8', (err, data) => {
            if (err) {
              reject(err);
              return;
            }

            let metadata = {};
            try {
              metadata = JSON.parse(data);
            } catch (e) {
              console.log(`Invalid JSON: ${data}`);
              reject(e);
              return;
            }
            let uploadId = path.basename(path.dirname(file_path));
            metadata['upload_id'] = uploadId;
            resolve(metadata);
          });
        }));
      });

      Promise.all(promises.map(reflect)).then((data) => {
        // Because of our reflection method, we filter for successful promises.
        var metadatas = data.filter(x => x.status == 'resolved')
          .map(x => x.value);

        let index = generate_index(metadatas);

        cache.put('index', index, 30 * 1000);
        res.json(index);
      }).catch((err) => {
        res.json(error_obj(err));
      });
    });
  }
}
exports.Indexer = Indexer;
