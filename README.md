# Projeto Integrador 3
## Proposta
### Título: Sistema de Medição Automatizada de Carga e Descarga de Baterias

1. Prazo: 23/12/2025
2. Equipe: Beatriz P. Faria, Igor B. de Oliveira, Júlia E. Steinbach, Lucas C. Fontes
3. Resumo da proposta: O projeto visa desenvolver um sistema para medição da curva
de carga e descarga de baterias, monitorando a tensão ao longo do tempo. A aplicação
permitirá analisar o comportamento de baterias, facilitando a previsão de desempenho e a
elaboração de relatórios automáticos com gráficos de tensão versus tempo.


## Organização do projeto
O projeto está organizado de modo que cada repositório separa funções específicas do hardware e do software aplicativo do projeto:

- [bateria_app](bateria_app/): É o diretório do software aplicativo que se comunica com o hardware diretamente e mostra ao usuário os resultados dos ciclos de carga e descarga para o usuário final.
- [documentacao](documentacao/): Diretório que contém o guia do usuário do software e datasheet do hardware.
- [ensaios_de_teste](ensaios_de_teste/): Pasta dedicada para apresentar os testes práticos realizados.
- [firmware_esp](firmware_esp/): Esse é o diretório que contém os códigos com as versões de firmware da ESP 32 que controla o hardware em termos de como os dados serão enviados para o software. E também processa os comandos vindo do software para iniciar os processos de carga/descarga de forma manual (forçada) ou automática (em modo auto).
- [outros](outros/): É uma pasta com ferramentas de testes que foram úteis ao longo do desenvolvimneto do projeto, como um programa que cria seriais virtuais para utilizar no software e um programa monitor serial em python para avaliar como a ESP processa os dados recebidos do software.

## Funcionamento básico da integração software - hardware

O software aplicativo utiliza a interface gráfica, onde o usuário poderá escolher a quantidade e a maneira que os ciclos ocorrerão. Com base na escolha do usuário, o comando de carga/descarga em modo auto/manual é enviado para a ESP32 presente no hardware. Com base no comando recebido, a ESP32 controla o circuito através da ativação/desativação de relés que ditam o modo do ciclo atual do circuito.

## Executável do projeto
O desenvolvimento do projeto ao longo de todo o semestre resultou no [executável final do projeto para sistemas WIndows](Executavel_Projeto_WIndows.zip)
