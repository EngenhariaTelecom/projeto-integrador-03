!define APP_NAME "Monitor de Bateria"
!define COMPANY_NAME "SeuNome"
!define VERSION "1.0"
!define INSTALL_DIR "$PROGRAMFILES\${APP_NAME}"

OutFile "installer.exe"
InstallDir "${INSTALL_DIR}"

RequestExecutionLevel admin
SetCompress auto
SetCompressor lzma

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Instalar"

    SetOutPath "$INSTDIR"

    ; Copia tudo do dist/MonitorBateria (caminho correto)
    File /r "bateria_app\dist\MonitorBateria\*.*"

    ; Atalho Desktop
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\MonitorBateria.exe"

    ; Atalho Menu Iniciar
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\MonitorBateria.exe"
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\Desinstalar.lnk" "$INSTDIR\Uninstall.exe"

    ; Registrar desinstalador
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


Section "Uninstall"

    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\Desinstalar.lnk"
    RMDir  "$SMPROGRAMS\${APP_NAME}"

    RMDir /r "$INSTDIR"

SectionEnd