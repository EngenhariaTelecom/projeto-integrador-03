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
    #    Copia os arquivos do PyInstaller         #
    ##############################################

    # Atenção: File /r NÃO aceita aspas!
    File /r ${SRC_DIR}\*.*

    ##############################################
    #       Copia JSON, CSV, ícones, assets       #
    ##############################################

    # Cria pasta baterias
    CreateDirectory "$INSTDIR\baterias"
    File /r bateria_app\baterias\*.*

    # Cria pasta assets
    CreateDirectory "$INSTDIR\assets"
    File /r bateria_app\assets\*.*


    ##############################################
    #                  ATALHOS                    #
    ##############################################

    # Atalho na Área de Trabalho
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_NAME}.exe" "" "$INSTDIR\${APP_NAME}.exe" 0

    # Pasta no Menu Iniciar
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"

    # Atalho no Menu Iniciar
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_NAME}.exe" "" "$INSTDIR\${APP_NAME}.exe" 0


    ##############################################
    #     REGISTRO PARA DESINSTALAÇÃO            #
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

    # Atalhos
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"

    # Remove instalação
    RMDir /r "$INSTDIR"

    # Remove registro
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd