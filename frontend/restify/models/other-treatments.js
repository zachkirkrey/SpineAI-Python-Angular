const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('OtherTreatments', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    treatment: {
      type: DataTypes.STRING,
      allowNull: false
    },
  });
};
