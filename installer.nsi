!define APP_NAME "MonitorBateria"
!define VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"

# --- A pasta usada pelo GitHub Actions ---
!define SRC_DIR "InstallerFiles"

# Ícone
!define ICON_FILE "bateria_app\assets\icons\icon.ico"

OutFile "MonitorBateriaInstaller.exe"
Icon "${ICON_FILE}"

InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

##############################################
#                   INSTALL                  #
##############################################

Section "Install Application"

    SetOverwrite on
    SetOutPath "$INSTDIR"

    ##############################################
    #         Copia EXE + assets + baterias       #
    ##############################################

    ; OBS: File /r NÃO aceita aspas
    File /r ${SRC_DIR}\*.*

    ##############################################
    #                  ATALHOS                    #
    ##############################################

    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\MonitorBateria.exe" 0

    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\MonitorBateria.exe" 0

    ##############################################
    #           REGISTRO DE DESINSTALAÇÃO         #
    ##############################################

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayName" "${APP_NAME}"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "InstallLocation" "$INSTDIR"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayVersion" "${VERSION}"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "Publisher" "Monitor Bateria"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "UninstallString" "$INSTDIR\Uninstall.exe"

    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

##############################################
#                  UNINSTALL                 #
##############################################

Section "Uninstall"

    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    RMDir  "$SMPROGRAMS\${APP_NAME}"

    RMDir /r "$INSTDIR"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd