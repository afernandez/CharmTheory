copy _mysql.pyd ..\..\..\..\Lib\site-packages\_mysql.pyd
copy _mysql_exceptions.py ..\..\..\..\Lib\site-packages\_mysql_exceptions.py
xcopy /E /Q /I MySQLdb ..\..\..\..\Lib\site-packages\MySQLdb
xcopy /E /Q /I MySQL_python-1.2.3-py2.7.egg-info ..\..\..\..\Lib\site-packages\MySQL_python-1.2.3-py2.7.egg-info

pip install django-annoying