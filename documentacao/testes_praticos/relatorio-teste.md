# Teste prático 

## Objetivo

Após desenvolvermos um software e hardware que se comunicam via Serial para monitoramento de ciclos de carga e descarga de uma bateira de 3,7v, iniciamos uma bateria de testes práticos para validar o funcionamento do software/hardware e garantir robustez no protótipo proposto. 


### Especificações da Bateria Testada

- Modelo: Ubetter
- Química: Lítio
- Capacidade nominal: 500mAh
- Tensão nominal: 3,7V
- Tensão de carga máxima: 4,2V

### Metodologia

Utilizando a versão de firmware 4.0 e a versão 1.0 do software foi iniciada a bateria de testes.

Inicialmente foi efetuado teste no modo MANUAL, onde o software permite o operador decidir se faz uma carga ou descarga da bateria. Tal teste se demonstrou efetido, sendo possível manualmente gerar uma carga ou descarga e depois ter os resultados em csv para consulta futura. 

Depois iniciamos testes no modo AUTO, onde o operador pode decidir quantos ciclos automaticamente de carga/descarga deve ocorrer assim como o tempo de descanso entre cada ciclo. Neste modo, tanto o hardware quanto o software foram efetivos, conseguindo efetuar os ciclos conforme o desejado pelo o operador e armazenando em csv o resultado.

_OBS.:_
- _Ciclo: entendemos como ciclo o processo de carga ou de descarga, ou seja, para ocorrer uma carga e descarga é interpretado como 2 ciclos._
- _Amostragem: a ESP32 envia os dados de tensão a cada ≈ 1 s._


## Resultados

A seguir apresento gráfico feito a paritr dos dados do CSV obtido do teste de 100 ciclos no modo AUTO. 

A bateria apresenta tensão máxima próxima de 4,2 V, valor típico de Li-ion / Li-Po, indicando carga completa adequada.

Durante a carga, observa-se que a tensao sobe rapidamente no início e depois entra em regime quase estacionário, caracterizando a fase CV (tensão constante).


<p align="center">
  <img src="ciclo-carga.png" alt="Ciclo carga - Tensão vs Tempo" width="500"><br>
  <em>Figura 1 – Ciclo de carga: Tensão vs Tempo</em>
</p>

A descarga é contínua, sem quedas abruptas o que indica boa estabilidade elétrica e ausência de falhas de contato ou sobrecorrente.

A tensão decresce de ~3,7 V até ~3,3 V no ciclo analisado, típico de região útil da descarga. Contudo, vale lembrar que os teste são realizados considerando a descarga competa quando a tensao abaixa de 3v.

<p align="center">
  <img src="ciclo-descarga.png" alt="Ciclo carga - Tensão vs Tempo" width="500"><br>
  <em>Figura 2 – Ciclo de descarga: Tensão vs Tempo</em>
</p>


## Conclusão

O sistema de teste funcionou conforme o esperado durante os ensaios realizados. A análise dos dados mostrou que os ciclos de carga e descarga da bateria ocorreram de forma estável, sem falhas, apresentando um comportamento compatível com o esperado para baterias do tipo Li-ion.

O intervalo de 60 segundos entre cada ciclo foi suficiente para evitar o aquecimento da bateria utilizada no teste, contribuindo para a segurança do experimento e para a repetição adequada dos ciclos ao longo do tempo.

O equipamento mostrou-se confiável para testes futuros, pois os resultados obtidos foram consistentes e bem definidos. Além disso, conforme apresentado no repositório do projeto, diferentes arquivos CSV comprovam o funcionamento correto do protótipo, variando a quantidade de ciclos testados e demonstrando sua eficácia para a finalidade proposta.

Dessa forma, conclui-se que o protótipo atende ao objetivo do trabalho, podendo ser utilizado como uma ferramenta adequada para testes de carga e descarga de baterias de lítio de 3,7V.