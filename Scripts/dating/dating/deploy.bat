REM Copy __init__.py, settings.py, and web.config to root.
REM Create a "dating" folder in the destination, that will contain all of the files in the source root.
REM Copy the templates folder inside the destination's "dating" folder.
REM Copy the static folder inside the destination's root.
REM Don't delete the "venv" folder in the destination

echo Starting
SET @SOURCE=D:\software\Python\django\Scripts\dating\dating
SET @DEST=C:\Users\Alejandro\Documents\My Web Sites\ZooPythonProject

copy "%@SOURCE%\__init__.py" "%@DEST%\__init__.py"
copy "%@SOURCE%\settings.py" "%@DEST%\settings.py"
copy "%@SOURCE%\web.config"  "%@DEST%\web.config"

mkdir "%@DEST%\dating"

copy "%@SOURCE%\__init__.py" "%@DEST%\dating\__init__.py"
copy "%@SOURCE%\admin.py"    "%@DEST%\dating\admin.py"
copy "%@SOURCE%\models.py"   "%@DEST%\dating\models.py"
copy "%@SOURCE%\settings.py" "%@DEST%\dating\settings.py"
copy "%@SOURCE%\urls.py"     "%@DEST%\dating\urls.py"
copy "%@SOURCE%\views.py"    "%@DEST%\dating\views.py"
copy "%@SOURCE%\web.config"  "%@DEST%\dating\web.config"
copy "%@SOURCE%\wsgi.py"     "%@DEST%\dating\wsgi.py"

xcopy /E /Q /I /Y "%@SOURCE%\templates" "%@DEST%\dating\templates"
xcopy /E /Q /I /Y "%@SOURCE%\static"    "%@DEST%\dating\static"