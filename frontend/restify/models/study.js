const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Study', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    creation_datetime: {
      type: DataTypes.DATE,
      allowNull: false
    },
    file_dir_path: {
      type: DataTypes.STRING,
      allowNull: false
    },
    file_dir_checksum: {
      type: DataTypes.STRING,
      allowNull: false
    },
    accession_number: {
      type: DataTypes.STRING,
      allowNull: false
    },
    patient_age: {
      type: DataTypes.STRING,
      allowNull: false
    },
    patient_name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    patient_size: {
      type: DataTypes.STRING,
      allowNull: false
    },
    patient_sex: {
      type: DataTypes.STRING,
      allowNull: false
    },
    study_instance_uid: {
      type: DataTypes.STRING,
      allowNull: false
    }
  });
};
