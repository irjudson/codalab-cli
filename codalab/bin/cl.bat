@echo off
REM
REM TODO: replace this with an nicer unified Python interface that unifies the
REM server and client.
REM Once you install your virtual environment, activate it and 'pip install .'
REM 
set CODALAB="C:\dev\codalab-cli"

python %CODALAB%\codalab\bin\codalab_client.py %CODALAB%\codalab\config\sqlite_client_config.json "%*"
