const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Report', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    state: {
      type: DataTypes.STRING,
      allowNull: false
    },
    type: {
      type: DataTypes.STRING,
      allowNull: false
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    started_datetime: {
      type: DataTypes.DATE
    },
    completed_datetime: {
      type: DataTypes.DATE
    },
    error_str: {
      type: DataTypes.STRING,
      allowNull: false
    },
    report_bytes: {
      type: DataTypes.BLOB
    },
    num_narrow_slices: {
      type: DataTypes.INTEGER
    },
    surgery_recommended: {
      type: DataTypes.BOOLEAN
    }
  }, {
    defaultScope: {
      attributes: {
        exclude: ['report_bytes']
      }
    }
  });
};
