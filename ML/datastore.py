import psycopg2
from pandas import read_sql
import json
from cStringIO import StringIO
import time

config = { 'dbname': 'newsdb', 
           'user': 'test',
           'pwd': 'test',
           'host': 'localhost',
           'port':'5432'
}


class DataStore ():


    def __init__( self ):
        '''
            Constructor
        '''
        self.conn = self.create_conn(config=config)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()


    def create_conn(*args,**kwargs):
        config = kwargs['config']
        try:
            con=psycopg2.connect(dbname=config['dbname'], host=config['host'], port=config['port'], user=config['user'], password=config['pwd'])
            
            return con
        except Exception as err:
            print(err)


    def createTable( self, term ):
        '''
            create new table
        '''

        query = "CREATE TABLE IF NOT EXISTS "+ term + " ( tweetid bigint NOT NULL PRIMARY KEY, text varchar(500) NOT NULL, timestamp bigint NOT NULL );"

        self.cur.execute(query)

        # Make the changes to the database persistent
        self.conn.commit()

        print "Table :" + term +" is created!!!"


    def removeTable( self, term ):
        '''
            remove new table
        '''
        query = "DROP TABLE "+ term + ";"
        self.cur.execute(query)

        # Make the changes to the database persistent
        self.conn.commit()

        print "Table :" + term +" is deleted!!!"



    def addRowToTable( self, term, tweetid, text, timestamp ):
        '''
            add row to table
        '''
        self.cur.execute("INSERT INTO "+term+" (tweetid, text, timestamp) VALUES (%s,%s,%s)",  ( tweetid, text, timestamp) )

        #print "New row added in the Table :" + term 


    def getEveryRow( self, term ):
        '''
            add row to table
        '''
        output = []
        query="SELECT * from "+ term  + ";"
        self.cur.execute(query)
        row = self.cur.fetchone()
        while row:
            output.append (row)
            row = self.cur.fetchone()

        return output


    def getDF( self, term, start_timestamp, end_timestamp ):
        '''
            get dataframe
        '''
        query = "select text, timestamp from "+ term + " where timestamp between " + str(start_timestamp) + " and " + str(end_timestamp)

        df = read_sql(query, con=self.conn) 
        return df


    def __del__(self):
        # Close communication with the database
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    dsObj = DataStore ()
    #term = "kenneth"
    term = "james"
    dsObj.removeTable( term )
    dsObj.createTable( term )

    dsObj.addRowToTable( term, 177384834569, "Please am coming home", 45332228 )
    dsObj.addRowToTable( term, 177384838297, "Please am seeing him", 45332229916 )
    print dsObj.getEveryRow( term )
    print "======================================="
    print "======================================="
    print "=======================================\n"
    print dsObj.getDF(  term )




