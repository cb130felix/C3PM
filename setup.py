from cx_Freeze import setup, Executable

setup(name='c3pm', version='0.1', description='Construct 3 pack manager', executables=[Executable('main.py')])