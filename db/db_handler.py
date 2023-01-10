import pandas as pd
import pymysql
from db import db_credentials


class DB:
    def __init__(self):
        self.creds = db_credentials.creds
        self.connect_db_mysql()

    def connect_db_mysql(self):
        """
        :param creds: dict, creds for mysql connection
        :return: connection, cursor for mysql database
        """

        try:
            # Create connection to database
            connection = pymysql.connect(host=self.creds['db_host'],
                                         user=self.creds['db_username'],
                                         passwd=self.creds['db_password'],
                                         database=self.creds['db_name'],
                                         port=self.creds['db_port'])

            cursor = connection.cursor()
        except Exception as e:
            raise ConnectionError('Connection to mysql database went wrong') from e

        self.connection = connection
        self.cursor = cursor

    def get_from_db(self, query):
        """
        :param connection: connection to db
        :param query: str with select query
        :return: pandas Series or DataFrame
        """
        try:
            return pd.read_sql(query, self.connection)
        except Exception as e:
            self.connection.rollback()
            raise Exception('Getting data went wrong') from e

    def execute_query(self, query):
        """
        :param query: str with query or queries separated with ";"
        :param connection: connection to db
        :param cursor: cursor of connection to db
        :return: None
        """
        try:
            for i in query.split(';'):
                if i != '':
                    self.cursor.execute(i)
                    self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception(f'Execution query went wrong ({query})') from e

    def write_to_db(self, to_db_list, table_name, id_tag=None, update_string=None, on_conflict=False):
        """
        :param to_db_list: list of lists
        :param table_name: str name
        :param connection: connection to db
        :param cursor: cursor of connection to db
        :param id_tag: primary key
        :param update_string: list ogf columns
        :param on_conflict: False by default
        :return: None
        """
        # If list is empty do nothing
        if len(to_db_list) == 0:
            return

        signs = '(' + ('%s,' * len(to_db_list[0]))[:-1] + ')'
        try:
            # Generate inserting query
            args_str = ','.join(self.cursor.mogrify(signs, x) for x in to_db_list)
            # args_str = args_str.decode()
            insert_statement = """INSERT INTO %s VALUES """ % table_name
            conflict_statement = """ ON CONFLICT DO NOTHING"""
            if on_conflict:
                conflict_statement = """ ON CONFLICT {0} DO UPDATE SET {1};""".format(id_tag, update_string)
            # Execute inserting query
            self.cursor.execute(insert_statement + args_str + ';')
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception('Inserting data went wrong') from e
