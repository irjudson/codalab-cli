@echo off
REM
REM TODO: replace this with an nicer unified Python interface that unifies the
REM server and client.
REM Once you install your virtual environment, activate it and 'pip install .'
REM 

REM Twisted way of getting the directory two levels above us in windows command prompt
pushd %~dp0
   pushd .. 
      pushd .. 
         set CODALAB=%cd%
      popd 
    popd 
popd

set PYTHONPATH="%PYTHONPATH%;%CODALAB%"

python %CODALAB%\codalab\bin\codalab_client.py %CODALAB%\codalab\config\sqlite_client_config.json "%*"
