const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('Symptoms', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    symptom: {
      type: DataTypes.STRING,
      allowNull: false
    },
  });
};
