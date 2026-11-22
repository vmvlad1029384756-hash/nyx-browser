#define AppName "NYX Browser"
#define AppVersion "1.0.0-dev.3.9"
#define AppPublisher "NYX"
#define AppExeName "NYX Browser.exe"

[Setup]
AppId={{7B6F1A43-7B61-4D63-9F75-7A9C0E9A10F1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\NYX Browser
AppendDefaultDirName=no
UsePreviousAppDir=yes
DefaultGroupName=NYX Browser
DisableProgramGroupPage=yes
DisableDirPage=no
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
WizardStyle=modern
SetupIconFile=..\nyx\assets\nyx.ico
OutputDir=..\installer
OutputBaseFilename=NYX_Browser_{#AppVersion}_Setup_x64
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
PrivilegesRequired=admin
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[CustomMessages]
english.DesktopIconTask=Create a desktop shortcut
english.AdditionalTasks=Additional icons:
english.LaunchApp=Launch NYX Browser
english.UserDataNote=Browser profile, cookies, history and cache will be stored on the selected drive.
russian.DesktopIconTask=Создать ярлык на рабочем столе
russian.AdditionalTasks=Дополнительные ярлыки:
russian.LaunchApp=Запустить NYX Browser
russian.UserDataNote=Профиль браузера, cookies, история и кеш будут храниться на выбранном диске.

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopIconTask}"; GroupDescription: "{cm:AdditionalTasks}"; Flags: unchecked

[Dirs]
Name: "{app}"
Name: "{app}\UserData"; Permissions: users-modify
Name: "{app}\UserData\NYX Browser"; Permissions: users-modify

[Files]
Source: "..\dist\NYX Browser\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NYX Browser"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\NYX Browser"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Registered browser capabilities are exposed to Windows. The user still chooses the actual default app in Windows Settings.
Root: HKCU; Subkey: "Software\Classes\NYXBrowserHTML"; ValueType: string; ValueName: ""; ValueData: "NYX Browser HTML Document"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\NYXBrowserHTML\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"",0"
Root: HKCU; Subkey: "Software\Classes\NYXBrowserHTML\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""
Root: HKCU; Subkey: "Software\Classes\NYXBrowserURL"; ValueType: string; ValueName: ""; ValueData: "NYX Browser URL"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\NYXBrowserURL"; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\NYXBrowserURL\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"",0"
Root: HKCU; Subkey: "Software\Classes\NYXBrowserURL\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"" ""%1"""
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser"; ValueType: string; ValueName: ""; ValueData: "NYX Browser"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"",0"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#AppExeName}"""
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "NYX Browser"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "NYX Browser — dark browser for Windows"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities"; ValueType: string; ValueName: "ApplicationIcon"; ValueData: """{app}\{#AppExeName}"",0"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities\URLAssociations"; ValueType: string; ValueName: "http"; ValueData: "NYXBrowserURL"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities\URLAssociations"; ValueType: string; ValueName: "https"; ValueData: "NYXBrowserURL"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities\FileAssociations"; ValueType: string; ValueName: ".htm"; ValueData: "NYXBrowserHTML"
Root: HKCU; Subkey: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities\FileAssociations"; ValueType: string; ValueName: ".html"; ValueData: "NYXBrowserHTML"
Root: HKCU; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "NYX Browser"; ValueData: "Software\Clients\StartMenuInternet\NYX Browser\Capabilities"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  UserDataDir: string;
begin
  if CurStep = ssPostInstall then
  begin
    UserDataDir := ExpandConstant('{app}\UserData\NYX Browser');
    if not ForceDirectories(UserDataDir) then
      RaiseException('Could not create the NYX Browser data folder.');
    if not SaveStringToFile(ExpandConstant('{app}\nyx-user-data-path.txt'), UserDataDir, False) then
      RaiseException('Could not save the NYX Browser data folder setting.');
  end;
end;

// User data is stored inside {app}\UserData\NYX Browser on the same drive and is intentionally retained on uninstall.
