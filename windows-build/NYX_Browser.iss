#define AppName "NYX Browser"
#define AppVersion "1.0.0-dev.3.2"
#define AppPublisher "NYX"
#define AppExeName "NYX Browser.exe"

[Setup]
AppId={{7B6F1A43-7B61-4D63-9F75-7A9C0E9A10F1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\NYX Browser
DefaultGroupName=NYX Browser
DisableProgramGroupPage=yes
DisableDirPage=yes
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
UninstallDisplayVersion={#AppVersion}
WizardStyle=modern
SetupIconFile=..\nyx\assets\nyx.ico
OutputDir=..\installer
OutputBaseFilename=NYX_Browser_{#AppVersion}_Setup_x64
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на рабочем столе"; GroupDescription: "Дополнительные ярлыки:"; Flags: unchecked

[Files]
Source: "..\dist\NYX Browser\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NYX Browser"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\NYX Browser"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Запустить NYX Browser"; Flags: nowait postinstall skipifsilent

; User data in %LOCALAPPDATA%\NYX Browser is outside the install directory and is retained on uninstall.
