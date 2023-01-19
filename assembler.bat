@echo off
SETLOCAL
cls

set curr=%cd%

cd %cd%\Assembly Files\

for %%a in (*.asm) do (
	%curr%\dist\Assembler.py "%cd%\%%a"
)


 

@echo Exection finished!
pause> nul | set /p "=Click any key to exit the program...." 

