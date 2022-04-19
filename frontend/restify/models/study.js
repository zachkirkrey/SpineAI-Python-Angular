const {
    DataTypes
} = require('sequelize');

module.exports = function (sequelize) {
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
            type: DataTypes.STRING
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
            type: DataTypes.STRING
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
        },
        image_file_type: {
            type: DataTypes.STRING,
            allowNull: false
        },
        mrn: {
            type: DataTypes.STRING,
            allowNull: false
        },
        email: {
            type: DataTypes.STRING
        },
        date_of_birth: {
            type: DataTypes.DATE,
            allowNull: false
        },
        phone_number: {
            type: DataTypes.INTEGER,
            allowNull: true
        },
        diagnosis: {
            type: DataTypes.STRING,
            allowNull: false
        },
        created_by: {
            type: DataTypes.BOOLEAN
        },
        appointment_date: {
            type: DataTypes.DATE,
        },
        archived_status: {
            type: DataTypes.BOOLEAN,
            allowNull: true
        }
    });
};