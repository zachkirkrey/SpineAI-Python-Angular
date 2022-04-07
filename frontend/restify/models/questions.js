const { DataTypes } = require('sequelize');

module.exports = function(sequelize) {
  return sequelize.define('OtherQuestions', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    uuid: {
      type: DataTypes.STRING,
      allowNull: false
    },
    lower_back: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    left_leg: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    right_leg: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    percent_lower_back: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    percent_leg: {
      type: DataTypes.INTEGER,
      allowNull: true
    },
    previous_spine_surgery: {
      type: DataTypes.BOOLEAN,
      allowNull: true
    },
    current_smoker: {
      type: DataTypes.BOOLEAN,
      allowNull: true
    },
    mri_status: {
      type: DataTypes.STRING,
      allowNull: true
    },
    updation_datetime:{
        type: DataTypes.DATE,
    },
    study: {
      type: DataTypes.INTEGER,
      allowNull: true,
      references: {
        model: sequelize.models.Study,
        key: 'id'
    }
    },
    archived_status:{
     type: DataTypes.BOOLEAN,
     allowNull: true
    }
  });
};
