# Projeto Integrador 3
## Proposta
### Título: Sistema de Medição Automatizada de Carga e Descarga de Baterias
2. Prazo: 23/12/2025
3. Equipe: Beatriz P. Faria, Igor B. de Oliveira, Júlia E. Steinbach, Lucas C. Fontes
4. Resumo da proposta: O projeto visa desenvolver um sistema para medição da curva
de carga e descarga de baterias, monitorando a tensão ao longo do tempo. A aplicação
permitirá analisar o comportamento de baterias, facilitando a previsão de desempenho e a
elaboração de relatórios automáticos com gráficos de tensão versus tempo.

atual estrutura de pastas do protótipo:
```
bateria_app/
│
├── main.py                     # Ponto de entrada da aplicação
│
├── bateria/
│   ├── bateriaA.json           # exemplo 1
│   ├── bateriaB.json           # exemplo 2
│   ├── bateriaC.json           # exemplo 3
│   .
│   .
│   .
│    └── bateriaN.json          # idealmente aceitando n baterias
│
├── core/
│   ├── bateria.py              # Classe Battery com atributos e métodos
│   ├── historico.py            # Salvamento e leitura dos CSVs
│   └── monitor.py              # Lógica de leitura/simulação de sensores
│
├── ui/
│   ├── autocomplete.py         # Caixa de texto que permite a escolha através de dados já cadastrados
│   ├── base_app.py             # Arquivo de programa que intersecciona cada outro ao programa
│   ├── tela_ciclos.py          # Interface de testes de carga/descarga
│   ├── tela_configuracao.py    # Interface de configuração de teste
│   ├── tela_historico.py       # Histórico de medições e exportação
│   ├── tela_inicial.py         # Menu inicial
│   ├── tela_monitoramento.py   # Interface de monitoramento em tempo real
│   └── tela_selecao.py         # Interface de seleção de bateria
│
└── assets/
    ├── icons/                  # Ícones e imagens de interface
    ├── dados/                  # CSVs e logs de testes
    ├── lib/                    # Bibliotecas usadas no python
    └── mqtt/                   # Local do Broker Mosquitto
```