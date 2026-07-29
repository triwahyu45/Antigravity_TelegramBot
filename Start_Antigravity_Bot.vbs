' Google Antigravity Telegram Bot - Double-Click System Tray & Local GPU Launcher
' Author: TriWahyu45 (https://github.com/triwahyu45)

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\Triwahyu45\AppData\Local\Programs\Ollama\ollama.exe"" serve", 0, False
WshShell.Run "pythonw G:\Antigravity_Server\Bot_Scripts\tray_launcher.py", 0, False
