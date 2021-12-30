const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Classification', {
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
        model: 'Study',
        key: 'id'
      }
    },
    state: {
      type: DataTypes.STRING,
      allowNull: false
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    type: {
      type: DataTypes.STRING,
      allowNull: false
    },
    input_series: {
      type: DataTypes.INTEGER,
      allowNull: false,
      references: {
        model: 'ImageSeries',
        key: 'id'
      }
    },
    started_datetime: {
      type: DataTypes.DATE
    },
    completed_datetime: {
      type: DataTypes.DATE
    },
    error_str: {
      type: DataTypes.TEXT,
      allowNull: false
    }
  });
};
