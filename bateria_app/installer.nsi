!define APP_NAME "MonitorBateria"
!define VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"
!define SRC_DIR "MonitorBateriaApp"
!define ICON_FILE "assets\icon.ico"

OutFile "MonitorBateriaInstaller.exe"
Icon "${ICON_FILE}"

InstallDir "${INSTALL_DIR}"

RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles


##############################################
#                 INSTALL                    #
##############################################

Section "Install Application"

    SetOutPath "$INSTDIR"

    # Copia tudo que o PyInstaller gerou
    File /r "${SRC_DIR}\*.*"

    # Garante criação da pasta com JSONs
    CreateDirectory "$INSTDIR\baterias"

    # Copia os JSONs original do repositório
    File /r "baterias\*.*"

    ##############################################
    #               ATALHOS
    ##############################################

    # Atalho no Desktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\MonitorBateria.exe" 0

    # Pasta no Menu Iniciar
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    # Atalho no Menu Iniciar
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\MonitorBateria.exe" 0

    ##############################################
    #     REGISTRO PARA DESINSTALAÇÃO
    ##############################################

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
        "UninstallString" "$INSTDIR\Uninstall.exe"

    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


##############################################
#                 UNINSTALL                  #
##############################################

Section "Uninstall"

    # Remove atalhos
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"

    # Remove arquivos da aplicação
    RMDir /r "$INSTDIR"

    # Remove chave do registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd