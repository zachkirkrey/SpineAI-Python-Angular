const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Ingestion', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    name: {
      type: DataTypes.STRING,
      allowNull: true
    },
    state: {
      type: DataTypes.STRING,
      allowNull: false
    },
    type: {
      type: DataTypes.STRING,
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
    accession_number: {
      type: DataTypes.STRING,
      allowNull: false
    },
    file_archive_bytes: {
      type: DataTypes.BLOB
    }
  }, {
    defaultScope: {
      attributes: {
        exclude: ['file_archive_bytes']
      }
    }
  });
};
