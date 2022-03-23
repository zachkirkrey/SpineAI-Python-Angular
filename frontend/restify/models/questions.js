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
    },
    left_leg: {
      type: DataTypes.INTEGER,
    },
    right_leg: {
      type: DataTypes.INTEGER,
    },
    percent_lower_back: {
      type: DataTypes.INTEGER,
    },
    percent_leg: {
      type: DataTypes.INTEGER,
    },
    previous_spine_surgery: {
      type: DataTypes.BOOLEAN
    },
    current_smoker: {
      type: DataTypes.BOOLEAN
    },
    mri_status: {
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
    }
  });
};
