#!/usr/bin/env python3

"""This script cleans up Luke's Spine Questionnaire CSV."""

import argparse
import csv
import datetime
from enum import IntEnum, auto
import logging
import os
import sqlite3

import bcrypt
import yaml


class ColumnType(IntEnum):
    DATETIME = auto()
    TEXT = auto()
    INTEGER = auto()
    FLOAT = auto()


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
            'input_file',
            metavar='questionnaire.csv',
            type=str)
    parser.add_argument(
            '--overwrite',
            default=False,
            action='store_true')
    parser.add_argument(
            '--output_db',
            metavar='questionnaire.db',
            type=str,
            default='./questionnaire.db')

    args = parser.parse_args()

    settings = None
    with open('csv_cleaner.yml', 'r', encoding='utf8') as settings_file:
        settings = yaml.load(settings_file)

        for column in settings['columns']:
            if 'type' in column:
                try:
                    column['type'] = ColumnType[column['type']]
                except KeyError:
                    logging.error('Unknown column type for column "{}". Got "{}"'.format(
                        column['input'], column['type']))

    if os.path.exists(args.output_db):
        if args.overwrite:
            os.remove(args.output_db)
        else:
            raise FileExistsError('File "{}" already exists and --overwrite is not set. Exiting...')

    db = sqlite3.connect(args.output_db)
    c = db.cursor()
    c.execute('DROP TABLE IF EXISTS data')
    db.commit()

    # Create the SQL table schema.
    create_table_columns = [('id', 'INTEGER', 'PRIMARY KEY')]
    for col in settings['columns']:
        if 'output' in col:

            if 'hash' in col and col['hash']:
                column_name = '"{}"'.format(col['output'] + ' Hash')
                create_table_columns.append((column_name, 'TEXT'))

            if 'store_original' in col and not col['store_original']:
                continue

            column_name = '"{}"'.format(col['output'])
            data_type = "TEXT"
            if 'type' in col:
                if col['type'] == ColumnType.INTEGER:
                    data_type = "INTEGER"
                elif col['type'] == ColumnType.FLOAT:
                    data_type = "REAL"

            create_table_columns.append((column_name, data_type))

    num_columns = len(create_table_columns)
    create_table_column_expressions = [
            ' '.join(c) for c in create_table_columns]
    c.execute('CREATE TABLE data ({})'.format(
        ','.join(create_table_column_expressions)))
    db.commit()


    logging.info('Reading {}...'.format(args.input_file))

    with open(args.input_file, 'r') as csvfile:
        reader = csv.reader(csvfile)

        headers = next(reader)
        logging.info('# of columns in first row: {}'.format(len(headers)))

        for i, cell in enumerate(headers):
            column = settings['columns'][i]
            if column['input'] not in cell:
                logging.error('Expected "{}" for column {}. Got "{}".'.format(
                    column['input'], i, cell))

        num_data_rows = 0
        num_valid_rows = 0
        sql_rows = []

        for row in reader:
            is_valid_row = True
            num_data_rows += 1
            row_data = [num_data_rows]

            if num_data_rows % 10 == 1:
                logging.info('Processed {} rows.'.format(num_data_rows - 1))

            for i, cell in enumerate(row):
                column = settings['columns'][i]

                if i == 6 and cell != 'English':
                    is_valid_row = False
                    break

                if 'output' in column:
                    if 'hash' in column and column['hash']:
                        salt = bcrypt.gensalt(settings['bcrypt-hash-work-factor'])
                        secret = bytes(cell, 'utf-8')
                        hashed = bcrypt.hashpw(secret, salt).decode('utf-8', 'strict')
                        if not bcrypt.checkpw(secret, bytes(hashed, 'utf-8')):
                            raise ValueError(
                                    'bcrypt hash for row {} could not be '
                                    'verified. This should never '
                                    'happen.'.format(
                                        num_data_rows))
                        row_data.append(hashed)

                    if 'store_original' in column and not column['store_original']:
                        continue

                    column_type = ColumnType.TEXT
                    if 'type' in column:
                        column_type = column['type']

                    if column_type == ColumnType.DATETIME:
                        time = datetime.datetime.strptime(cell, column['datetime_format'])
                        cell_value = time.isoformat()
                    elif column_type == ColumnType.INTEGER:
                        cell_value = int(cell)
                    elif column_type == ColumnType.FLOAT:
                        cell_value = float(cell)
                    else:
                        cell_value = cell

                    row_data.append(cell_value)

            if is_valid_row:
                sql_rows.append(row_data)
                num_valid_rows += 1

        logging.info('# of stored columns: {}'.format(num_columns))
        logging.info('# of data rows: {}'.format(num_data_rows))
        logging.info('# of valid rows: {}'.format(num_valid_rows))

        logging.info('Writing values to database...')
        c.executemany(
                'INSERT INTO data VALUES ({})'.format(
                    ','.join(['?']*num_columns)),
                sql_rows)
        db.commit()

    db.close()


if __name__ == "__main__":
    main()
