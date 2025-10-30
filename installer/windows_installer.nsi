; NSIS Installer Script for Agentic Bookkeeper
; Author: Stephen Bogner
; Created: 2025-10-29
;
; Build command:
;   makensis installer\windows_installer.nsi
;
; Requirements:
;   - NSIS 3.0 or higher (https://nsis.sourceforge.io/)
;   - Built executable in dist\AgenticBookkeeper\

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General Configuration

; Application name and version
!define PRODUCT_NAME "Agentic Bookkeeper"
!define PRODUCT_VERSION "0.1.0"
!define PRODUCT_PUBLISHER "Stephen Bogner"
!define PRODUCT_WEB_SITE "https://github.com/yourusername/agentic_bookkeeper"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\AgenticBookkeeper.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Output filename
OutFile "..\dist\AgenticBookkeeper-${PRODUCT_VERSION}-Setup.exe"

; Installation directory
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""

; Request admin privileges
RequestExecutionLevel admin

; Compression
SetCompressor /SOLID lzma
SetCompress auto

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;--------------------------------
; Pages

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Version Information

VIProductVersion "${PRODUCT_VERSION}.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2025 ${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileDescription" "Intelligent bookkeeping automation powered by AI"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"

;--------------------------------
; Installer Sections

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  ; Copy all files from dist directory
  File /r "..\dist\AgenticBookkeeper\*.*"

  ; Create directories
  CreateDirectory "$INSTDIR\config"
  CreateDirectory "$INSTDIR\data"
  CreateDirectory "$INSTDIR\logs"
  CreateDirectory "$INSTDIR\watch"

  ; Create shortcuts in Start Menu
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\AgenticBookkeeper.exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\User Guide.lnk" "$INSTDIR\USER_GUIDE.md"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"

  ; Create desktop shortcut (optional)
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\AgenticBookkeeper.exe"

SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"

  ; Write registry keys for uninstaller
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\AgenticBookkeeper.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\AgenticBookkeeper.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"

  ; Get installation size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

;--------------------------------
; Uninstaller Sections

Section Uninstall
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\User Guide.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"

  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"

  ; Remove files and directories
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\AgenticBookkeeper.exe"
  Delete "$INSTDIR\USER_GUIDE.md"
  Delete "$INSTDIR\README.txt"

  ; Ask user if they want to keep data
  MessageBox MB_YESNO|MB_ICONQUESTION \
    "Do you want to keep your data and configuration files?$\n$\n\
    Choose 'Yes' to keep them for future installations.$\n\
    Choose 'No' to delete everything." \
    IDYES KeepData

  ; Remove all data
  RMDir /r "$INSTDIR\config"
  RMDir /r "$INSTDIR\data"
  RMDir /r "$INSTDIR\logs"
  RMDir /r "$INSTDIR\watch"

  KeepData:

  ; Remove installation directory if empty
  RMDir "$INSTDIR"

  ; Remove registry keys
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

;--------------------------------
; Installer Functions

Function .onInit
  ; Check if already installed
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString"
  StrCmp $R0 "" done

  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
    "${PRODUCT_NAME} is already installed.$\n$\n\
    Click 'OK' to uninstall the previous version$\n\
    or 'Cancel' to cancel this installation." \
    IDOK uninst
  Abort

  uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'

  done:
FunctionEnd
