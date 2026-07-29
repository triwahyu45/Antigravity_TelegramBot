Set WshShell = CreateObject("WScript.Shell")
' Jalankan bot
WshShell.Run """C:\Users\Triwahyu45\AppData\Local\Programs\Python\Python313\python.exe"" ""G:\Antigravity_Server\Bot_Scripts\antigravity_telegram_bot.py""", 0, False
WScript.Sleep 2000
' Jalankan mirror
WshShell.Run """C:\Users\Triwahyu45\AppData\Local\Programs\Python\Python313\python.exe"" ""G:\Antigravity_Server\Bot_Scripts\antigravity_mirror.py""", 0, False
