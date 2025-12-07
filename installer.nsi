!define APP_NAME "MonitorBateria"
!define VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"

!define SRC_DIR "InstallerFiles"
!define ICON_FILE "bateria_app\assets\icons\icon.ico"

OutFile "MonitorBateriaInstaller.exe"
Icon "${ICON_FILE}"

InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

SetCompressor /SOLID lzma

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles


##############################################
#                 INSTALL                    
##############################################

Section "Install Application"

    SetOverwrite on
    SetOutPath "$INSTDIR"

    DetailPrint "Copying files..."
    File /r ${SRC_DIR}\*.*

    ##############################################
    #               SHORTCUTS FIXED              #
    ##############################################

    DetailPrint "Creating shortcuts..."

    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\assets\icons\icon.ico" 0

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\assets\icons\icon.ico" 0

    ##############################################
    #                UNINSTALL ENTRY             #
    ##############################################

    DetailPrint "Registering uninstall..."
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "Monitor Bateria"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"

    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


##############################################
#                 UNINSTALL                  
##############################################

Section "Uninstall"

    DetailPrint "Removing shortcuts..."
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"

    DetailPrint "Removing files..."
    RMDir /r "$INSTDIR"

    DetailPrint "Cleaning registry..."
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd