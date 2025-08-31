import os
from win32com.client import Dispatch

# Path to your Python script
script_path = r"D:\credit\main.py"

# Path to your Python interpreter (adjust if different)
python_exe = r"C:\Users\ADMIN\AppData\Local\Programs\Python\Python313\python.exe"

# Path where you want the shortcut created
shortcut_path = os.path.join(os.environ["USERPROFILE"], "OneDrive\Desktop", "Soldes.lnk")

icon_path = r"D:\credit\images\images\app_icon.ico"
# Create the shortcut
shell = Dispatch('WScript.Shell')
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = python_exe
shortcut.Arguments = f'"{script_path}"'
shortcut.WorkingDirectory = os.path.dirname(script_path)
shortcut.IconLocation = icon_path  # or point to a custom .ico file
shortcut.save()

print(f"Shortcut created at {shortcut_path}")