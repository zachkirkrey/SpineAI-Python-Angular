/**
 * Unit tests for the REST API defined in /api.
 */
const http = require('http');
const path = require('path');

const assert = require('assert');
const supertest = require('supertest');

const app = require('../app');


describe('API', function() {
  before(function() {
    agent = supertest.agent(app);

    isValidJson = function(test, f) {
      f = f || function() {};
      return test.expect('Content-Type', /json/)
          .expect(200)
          .then((response) => {
            f(response.body);
          });
    };

    isErrorJson = function(test, f) {
      f = f || function() {};
      return test.expect('Content-Type', /json/)
          .expect(500)
          .then((response) => {
            data = response.body;
            assert(data.message.includes('error'));
            assert(data.errors);
            f(response.body);
          });
    }
  });
  context('CanalSegmentation', function() {
    describe('/canalsegmentations', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/canalsegmentations'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
  context('Classification', function() {
    describe('/classifications', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/classifications'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
  context('DiskSegmentation', function() {
    describe('/disksegmentations', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/disksegmentations'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
  context('ImageSeries', function() {
    describe('/imageseries', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/imageseries'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
  context('Ingestion', function() {
    describe('/ingestions', function() {
      it('should return valid JSON', function() {
        return isValidJson(agent.get('/ingestions'));
      });
    });
  });
  context('Report', function() {
    describe('/reports', function() {
      // TODO(billy): Add test for fetching by uuid.
      it('should return at least 1', function() {
        return isValidJson(agent.get('/reports'));
      });
      it('should return reports for Study ID == 0', function() {
        return isValidJson(agent.get('/reports?Studies.id=1'), (data) => {
          assert(data.length > 0);
        });
      });
      it('should not return reports for Study ID == gibberish', function() {
        return isValidJson(agent.get('/reports?Studies.id=gibberish'), (data) => {
          assert(data.length == 0);
        });
      });
      it('should return PDF when ?as=PDF', function(done) {
        agent.get('/reports?type=PDF_SIMPLE&as=PDF')
          .expect(200)
          .expect('Content-Type', /pdf/)
          .end(done)
      });
      it('should return HTML when ?as=HTML', function(done) {
        agent.get('/reports?type=HTML_VIEWER&as=HTML')
          .expect(200)
          .expect('Content-Type', /html/)
          .end(done)
      });
      it('should return JSON when ?as=JSON', function(done) {
        agent.get('/reports?type=JSON&as=JSON')
          .expect(200)
          .expect('Content-Type', /json/)
          .end(done)
      });
      it('should return CSV when ?as=CSV', function(done) {
        agent.get('/reports?type=JSON&as=CSV')
          .expect(200)
          .expect('Content-Type', /csv/)
          .end(done)
      });
      it('should return CSV when ?as=SUMMARYCSV', function(done) {
        agent.get('/reports?type=JSON&as=SUMMARYCSV')
          .expect(200)
          .expect('Content-Type', /csv/)
          .end(done)
      });

      it('should return error when ?as=PDF but no reports found.', function() {
        return isErrorJson(agent.get('/reports?id=nonexistent&as=PDF'));
      });
      it('should return error when ?as=invalid', function() {
        return isErrorJson(agent.get('/reports?as=invalid'));
      });
    });
  });
  context('Segmentation', function() {
    describe('/segmentations', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/segmentations'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
  context('Study', function() {
    describe('/studies', function() {
      it('should return at least 1', function() {
        return isValidJson(agent.get('/studies'), (data) => {
          assert(data.length > 0);
        });
      });
    });
  });
});
