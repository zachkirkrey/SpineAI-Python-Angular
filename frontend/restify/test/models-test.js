/**
 * Unit tests for the model definitions in /models.
 *
 * Mostly checking that foreign key relationships are defined correctly.
 */

const assert = require('assert');
const config = require('config');
const yaml = require('node-yaml');
const Sequelize = require('sequelize');

const sequelize = new Sequelize(config.get('sequelize.init'));
const {
  Classification,
  ImageSeries,
  Report,
  Segmentation,
  Study
} = require('../models')(sequelize);

describe('Classification', function() {
  describe('#findOne()', function() {
    it('should return 1', function() {
      return Classification.findOne().then(classification => {
        assert(classification);
      });
    });
  });
  describe('#getStudy()', function() {
    it('should return 1', function() {
      return Classification.findOne().then(classification => {
        return classification.getStudy().then(study => {
          assert(study);
        });
      });
    });
  });
  describe('#getReports()', function() {
    it('should return at least 1', function() {
      return Classification.findOne().then(classification => {
        return classification.getReports().then(reports => {
          assert(reports.length > 0);
        });
      });
    });
  });
});

describe('ImageSeries', function() {
  describe('#findOne()', function() {
    it('should return 1', function() {
      return ImageSeries.findOne().then(series => {
        assert(series);
      });
    });
  });
  context('RAW', function() {
    beforeEach(function() {
      this.find = {
        where: {
          type: 'RAW'
        }
      };
    });
    describe('#findOne()', function() {
      it('should return 1', function() {
        return ImageSeries.findOne(this.find).then(series => {
          assert(series);
        });
      });
    });
  });
  context('PREPROCESSED', function() {
    beforeEach(function() {
      this.find = {
        where: {
          type: 'PREPROCESSED'
        }
      };
    });
    describe('#findOne()', function() {
      it('should return 1', function() {
        return ImageSeries.findOne(this.find).then(series => {
          assert(series);
        });
      });
    });
  });
});

describe('Report', function() {
  describe('#findAll()', function() {
    it('should return at least 1', function() {
      return Report.findAll().then(reports => {
        assert(reports.length > 0);
      });
    });
  });
  describe('#getStudies()', function() {
    it('should return at least 1', function() {
      return Report.findOne().then(report => {
        return report.getStudies().then(studies => {
          assert(studies.length > 0);
        });
      });
    });
  });
});

describe('Segmentation', function() {
  describe('#findOne()', function() {
    it('should return 1', function() {
      return Segmentation.findOne().then(seg => {
        assert(seg);
      });
    });
  });
  describe('#getRawSeries()', function() {
    it('should return 1', function() {
      return Segmentation.findOne().then(seg => {
        return seg.getRawSeries().then(series => {
          assert(series);
        });
      });
    });
  });
  describe('#getPreprocessedSeries()', function() {
    it('should return 1', function() {
      return Segmentation.findOne().then(seg => {
        return seg.getPreprocessedSeries().then(series => {
          assert(series);
        });
      });
    });
  });
});

describe('Study', function() {
  describe('#findOne()', function() {
    it('should return 1', function() {
      return Study.findOne().then(study => {
        assert(study);
      });
    });
  });
  describe('#getClassifications()', function() {
    it('should return at least 1', function() {
      return Study.findOne().then(study => {
        return study.getClassifications().then(classifications => {
          assert(classifications.length > 0);
        });
      });
    });
  });
  describe('#getReports()', function() {
    it('should return at least 1', function() {
      return Study.findOne().then(study => {
        return study.getReports().then(reports => {
          assert(reports.length > 0);
        });
      });
    });
  });
});
