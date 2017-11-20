# https://stackoverflow.com/questions/5687718/how-can-i-insert-data-into-a-mysql-database
# https://github.com/PyMySQL/PyMySQL
import pymysql
import pymysql.cursors

import re
import pandas as pd

class databaseInterface():

    def __init__(self):
        super(databaseInterface,self).__init__()

        #self.connection = make_connection()
        # instance variables
        self.host     = 'localhost'
        self.user     = 'root'
        self.password = ''
        self.db       = 'politicalNewsSiteText'

        self.make_connection()

    def make_connection(self):
        # Connect to the database
        self.connection = pymysql.connect(host=self.host,
                             user=self.user,
                             password=self.password,
                             db=self.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def insert_into_sources(self,sql_info):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `sources` (`affiliation`, `url`,`name_of_site`,`rss_feed_url`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (sql_info[0],sql_info[1],sql_info[2],sql_info[3]))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def insert_into_source_data(self,sql_info):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "(select source_id from sources where rss_feed_url = '%s')" %sql_info[3]
            cursor.execute(sql)
            result = cursor.fetchone()

            sql = "INSERT INTO `source_data` (`date`, `title`,`summary`,`source_id`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql,
            (sql_info[0],
            sql_info[1],
            sql_info[2],
            result['source_id'])
            )

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()

    def read_columns(self,column_names,table_name):
        if type(column_names) == str:
            print("The column names must be passed in a list or array")
            return False

        dict_results = {}

        with self.connection.cursor() as cursor:
            for column_name in column_names:

                sql = "SELECT %s from %s" %(column_name,table_name)
                cursor.execute(sql)
                results = cursor.fetchall()

                temp = []
                for row in results:
                    temp.append(row[column_name])

                dict_results[column_name] = temp
        return dict_results

    def read_table_given_sql(self,sql_query):
        dict_results = {}
        dict_results['sql_query'] = sql_query

        with self.connection.cursor() as cursor:
            columns = re.search(r'SELECT(.*?)FROM', sql_query).group(1)
            columns = columns.split(',')

            cursor.execute(sql_query)
            results = cursor.fetchall()
            dict_results['results'] = results

            #for column in columns:
            #    name = column.strip()
            #    temp = []
            #    for row in results:
            #        temp.append(row[name])
            #    dict_results[name] = temp

        return dict_results

    def return_source_name_id(self):
        # remind what the mapping is between names and source_id's
        sql_query = "SELECT source_id, name_of_site FROM sources;"
        results = self.read_table_given_sql(sql_query)

        # df for mapping
        site_id_mapping_df = pd.DataFrame(columns=['name_of_site','source_id'])
        site_id_mapping_df['name_of_site'] = [row['name_of_site'] for row in results['results']]
        site_id_mapping_df['source_id'] = [row['source_id'] for row in results['results']]

        return site_id_mapping_df
