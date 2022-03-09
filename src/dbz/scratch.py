'''
Created on Mar 7, 2022

@author: immanueltrummer
'''
import sqlite3

con = sqlite3.connect(":memory:")
result = con.execute("""
    explain query plan select * from pragma_compile_options
    where compile_options like 'THREADSAFE=%'
""").fetchall()
print(result)