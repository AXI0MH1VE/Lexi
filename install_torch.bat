@echo off
call d:\lex7\env\Scripts\activate.bat
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
echo Torch installed.
