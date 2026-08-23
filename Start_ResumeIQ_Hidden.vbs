Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)

Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = currentDir

' Run Backend silently (0 means hide window)
WshShell.Run "cmd /c cd backend && .\venv\Scripts\activate && python run.py", 0, False

' Run Frontend silently
WshShell.Run "cmd /c cd frontend && npm run dev", 0, False

' Let the user know it worked
MsgBox "ResumeIQ is starting silently in the background!" & vbCrLf & vbCrLf & "Give it about 5 seconds, and your browser will automatically open.", 64, "ResumeIQ"
