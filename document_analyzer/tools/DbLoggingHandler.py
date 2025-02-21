import pyodbc
import logging

class DbLoggingHandler(logging.Handler):
    def __init__(self, conn_str):
        logging.Handler.__init__(self)
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='logs' AND xtype='U')
                               CREATE TABLE logs (
                                   id INT IDENTITY(1,1) PRIMARY KEY,
                                   asctime NVARCHAR(50),
                                   levelname NVARCHAR(50),
                                   message NVARCHAR(MAX)
                               )''')
        self.conn.commit()

    def emit(self, record):
        if self.formatter:
            record.message = self.format(record)
        self.cursor.execute("INSERT INTO logs (asctime, levelname, message) VALUES (?, ?, ?)",
                            (record.asctime, record.levelname, record.message))
        self.conn.commit()

    def close(self):
        self.conn.close()
        logging.Handler.close(self)