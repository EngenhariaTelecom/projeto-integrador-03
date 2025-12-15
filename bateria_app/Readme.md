# Diretório do software

Aqui será mostrada a arquitetura geral do software do projeto

## Estrutura do diretório

```
bateria_app/
│
├── main.py                     # Ponto de entrada da aplicação
│
├── bateria/
│   ├── bateriaA.json           # exemplo 1 de bateria
│   ├── bateriaB.json           # exemplo 2 de bateria
│   ├── bateriaC.json           # exemplo 3 de bateria
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

