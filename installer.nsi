!define APP_NAME "MonitorBateria"
!define VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"

# Diretório onde o PyInstaller gera os arquivos
!define SRC_DIR "dist\MonitorBateria"

# Ícone do instalador
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
#                 INSTALL                    #
##############################################

Section "Install Application"

    SetOutPath "$INSTDIR"

    ##############################################
    #   Copia tudo que o PyInstaller gerou        #
    ##############################################

    # IMPORTANTE: File /r NÃO aceita aspas e não aceita variáveis com aspas
    File /r ${SRC_DIR}\*.*

    ##############################################
    #    Copia JSON, CSV, ícones e recursos       #
    ##############################################

    # Baterias
    CreateDirectory "$INSTDIR\baterias"
    File /r bateria_app\baterias\*.*

    # Assets
    CreateDirectory "$INSTDIR\assets"
    File /r bateria_app\assets\*.*


    ##############################################
    #                  ATALHOS                    #
    ##############################################

    # Desktop
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\MonitorBateria.exe" "" "$INSTDIR\MonitorBateria.exe" 0

    # Menu Iniciar
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
#                 UNINSTALL                  #
##############################################

Section "Uninstall"

    # Remove atalhos
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    RMDir  "$SMPROGRAMS\${APP_NAME}"

    # Remove pasta de instalação
    RMDir /r "$INSTDIR"

    # Remove chave do registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd