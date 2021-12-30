const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Segmentation', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    study: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.Study,
        key: 'id'
      }
    },
    classification: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'Classification',
        key: 'id'
      }
    },
    preprocessed_patient_series: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.ImageSeries,
        key: 'id'
      }
    },
    raw_segmentation_series: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.ImageSeries,
        key: 'id'
      }
    },
    postprocessed_segmentation_series: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: sequelize.models.ImageSeries,
        key: 'id'
      }
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    type: {
      type: DataTypes.STRING,
      allowNull: false
    }
  });
};
