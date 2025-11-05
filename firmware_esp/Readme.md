# Changelog Firmware - ESP 32

### Versão 2.0

- Está versão incia a ESP no modo MANUAL com os reles de carga e descarga desligados.
- Além disso, essa versão tem um melhor controle do modo AUTO para ser mais assertivo na verificação.


### Versão 3.0

- Essa versão trabalha usando os dois núcleos da ESP usando tarefas no sistem freeRTOS.
- Cria duas tasks, cada uma em um núcleo diferente.
    - Core 0: executa a sua lógica original de medição e controle.
    - Core 1: fica monitorando o timeout da comunicação USB.
- Se passar 10 segundos sem receber “USB ON”, desliga automaticamente os relés como segurança.