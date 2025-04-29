## Voraussetzungen
- Active Directory läuft bereits auf einer VM
    - wenn nicht dann dem Tutorial folgen: "https://activedirectorypro.com/create-active-directory-test-environment/"
- Auf dem System ist entweder WSL mit Python oder Python an sich installiert.

## WSL mit Python
- Ist im Docs unter Notes LDAP aufsetzen.
- Später kommt noch eine ausführliche Version.
- sollte mit der aktuellen testuser.py funktionieren, wenn Active Directory läuft.
    - Wenn Ihr keinen habt, dann nehmt die EARLY ldapTest.py

## Python unter Windows
- Um das testuser.py Script zu starten, müssen einige Vorkehrungen getroffen werden.
1. Python 3.12 (oder eine Version euer Wahl) muss installiert sein.
    - wenn die Version abweicht, muss sich später eine andere .whl (wheel) heruntergeladen werden. Erklärung weiter unten.
    - meine Version: "python-3.12.0-amd64"
2. Visual Studio Build Tools runterladen von "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
3. Sachen auswählen wie im Bild "Visual Studio Build Tools.png"
    - WICHTIG! Wenn ihr eine andere Windows Version als Windows 10 habt, dann eine andere SDK auswählen!
4. installieren lassen
5. .whl Datei für gewählte Python Version installieren von "https://github.com/cgohlke/python-ldap-build/releases"
    - in diesem Beispiel mit Python 3.12, also "python_ldap-3.4.4-cp312-cp312-win_amd64.whl"
6. Diese Datei in das Verzeichnis legen, wodrin ihr Python in eurer Konsole ausführt
    - bei mir "C:\Users\mylab\Documents\ldap" in Windows PowerShell (als Admin)
7. Python LDAP installieren über "pip install python_ldap‑3.4.4‑cp312‑cp312‑win_amd64.whl"
8. testuser.py ausführen mit "py testuser.py"
    - Vorrausgesetzung: Die Datei befindet sich in eurem aktuellen Verzeichnis.
9. Hoffen, dass alles geklappt hat. Ansonsten mich gerne Anschreiben.