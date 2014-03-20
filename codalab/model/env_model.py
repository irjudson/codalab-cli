'''
EnvModel is a lightweight model for storing variables that are persisted
across multiple command-line client invocations in the same shell. In
particular, we do NOT import sqlalchemy in this module, because that library
is quite expensive to import.
'''
# TODO(skishore): If we want to support work contexts that are indexed by
# keys other than the shell ppid, this model's get / set methods will just have
# to take additional parameters for the key.
import os
import sqlite3

"""
Monkey patch OS module so we have a getppid on windows.
"""

if not hasattr(os, 'getppid'):
    import ctypes

    TH32CS_SNAPPROCESS = 0x02L
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    GetCurrentProcessId = ctypes.windll.kernel32.GetCurrentProcessId

    MAX_PATH = 260

    _kernel32dll = ctypes.windll.Kernel32
    CloseHandle = _kernel32dll.CloseHandle

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong),
            ("cntUsage", ctypes.c_ulong),
            ("th32ProcessID", ctypes.c_ulong),
            ("th32DefaultHeapID", ctypes.c_int),
            ("th32ModuleID", ctypes.c_ulong),
            ("cntThreads", ctypes.c_ulong),
            ("th32ParentProcessID", ctypes.c_ulong),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.c_ulong),

            ("szExeFile", ctypes.c_wchar * MAX_PATH)
        ]

    Process32First = _kernel32dll.Process32FirstW
    Process32Next = _kernel32dll.Process32NextW

    def getppid():
        '''
        :return: The pid of the parent of this process.
        '''
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        mypid = GetCurrentProcessId()
        snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

        result = 0
        try:
            have_record = Process32First(snapshot, ctypes.byref(pe))

            while have_record:
                if mypid == pe.th32ProcessID:
                    result = pe.th32ParentProcessID
                    break

                have_record = Process32Next(snapshot, ctypes.byref(pe))

        finally:
            CloseHandle(snapshot)

        return result

    os.getppid = getppid

class EnvModel(object):
    SQLITE_DB_FILE_NAME = 'env.db'

    def __init__(self, home):
        sqlite_db_path = os.path.join(home, self.SQLITE_DB_FILE_NAME)
        self.connection = sqlite3.connect(sqlite_db_path)
        self.create_tables()

    def create_tables(self):
        # Create a table mapping shell process ids to worksheets.
        self.connection.execute('''
          CREATE TABLE IF NOT EXISTS worksheets (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            ppid INTEGER NOT NULL,
            worksheet_uuid VARCHAR(63) NOT NULL,
            CONSTRAINT uix_1 UNIQUE(ppid)
          );
        ''')

    def get_current_worksheet(self):
        '''
        Return a worksheet_uuid for the current worksheet, or None if there is none.

        This method uses the current parent-process id to return the same result
        across multiple invocations in the same shell.
        '''
        ppid = os.getppid()
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM worksheets WHERE ppid = ?;', (ppid,))
        row = cursor.fetchone()
        return row[2] if row else None

    def set_current_worksheet(self, worksheet_uuid):
        '''
        Set the current worksheet for this ppid.
        '''
        ppid = os.getppid()
        with self.connection:
            self.connection.execute('''
              INSERT OR REPLACE INTO worksheets (ppid, worksheet_uuid) VALUES (?, ?);
            ''', (ppid, worksheet_uuid))

    def clear_current_worksheet(self):
        '''
        Clear the current worksheet setting for this ppid.
        '''
        ppid = os.getppid()
        with self.connection:
            self.connection.execute('DELETE FROM worksheets WHERE ppid = ?;', (ppid,))
