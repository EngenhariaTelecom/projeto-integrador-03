#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

// ======== CONFIGURAÇÃO GERAL ========

const float V_BATT_MIN = 3.0;
const float V_BATT_MIN_REENABLE = 3.05;
const float V_BATT_MAX = 4.2;
const float V_BATT_MAX_REENABLE = 4.15;

const int PIN_CHARGE_CTRL_1 = 25;
const int PIN_CHARGE_CTRL_2 = 26;
const int PIN_DISCHARGE_CTRL = 27;

float calib_factor = 1.0;

const float ADS_VFSR = 4.096f;
const float ADC_COUNTS = 32767.0f;

const float SENSIBILIDADE = 0.066;  // V/A (para ACS712-30A)
const int CANAL_CORRENTE = 1;       // A1
const int CANAL_TENSAO = 0;         // A0
const int NUM_AMOSTRAS = 20;

float offset_corrente = 0.0;

// ======== MODO DE OPERAÇÃO ========
enum Mode { AUTO, MANUAL };
Mode mode = MANUAL;

bool forceCharge = false;
bool forceDischarge = false;

// ======== FREE RTOS ========
unsigned long lastSerialTime = 0;  // último tempo em que recebeu algo
const unsigned long TIMEOUT_USB = 10000; // 10 segundos

TaskHandle_t TaskCore0;
TaskHandle_t TaskCore1;

// ======== FUNÇÕES ========

float lerMediaADC(uint8_t canal) {
  long soma = 0;
  for (int i = 0; i < NUM_AMOSTRAS; i++) {
    soma += ads.readADC_SingleEnded(canal);
    delay(5);
  }
  return soma / (float)NUM_AMOSTRAS;
}

float readBatteryVoltage(uint8_t ch) {
  float adc_avg = lerMediaADC(ch);
  float v_adc = adc_avg * (ADS_VFSR / ADC_COUNTS);
  v_adc *= calib_factor;
  return v_adc;
}

float readCurrent() {
  float leitura = lerMediaADC(CANAL_CORRENTE);
  float tensao_mV = (leitura - offset_corrente) * (ADS_VFSR / ADC_COUNTS) * 1000.0;
  float corrente = tensao_mV / (SENSIBILIDADE * 1000.0);
  return corrente;
}

void setCharge(bool on) {
  digitalWrite(PIN_CHARGE_CTRL_1, on ? LOW : HIGH);
  digitalWrite(PIN_CHARGE_CTRL_2, on ? LOW : HIGH);
}

void setDischarge(bool on) {
  digitalWrite(PIN_DISCHARGE_CTRL, on ? LOW : HIGH);
}

// ======== COMANDOS SERIAL ========
void handleSerialCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "AUTO") {
    mode = AUTO;
    Serial.println("Modo AUTOMATICO ativado.");
  } 
  else if (cmd == "CHARGE ON") {
    mode = MANUAL; forceCharge = true;
    setCharge(true);
    Serial.println("Modo MANUAL: carga FORCADA ON.");
  } 
  else if (cmd == "CHARGE OFF") {
    mode = MANUAL; forceCharge = false;
    setCharge(false);
    Serial.println("Modo MANUAL: carga FORCADA OFF.");
  } 
  else if (cmd == "DISCH ON") {
    mode = MANUAL; forceDischarge = true;
    setDischarge(true);
    Serial.println("Modo MANUAL: descarga FORCADA ON.");
  } 
  else if (cmd == "DISCH OFF") {
    mode = MANUAL; forceDischarge = false;
    setDischarge(false);
    Serial.println("Modo MANUAL: descarga FORCADA OFF.");
  } 
  else if (cmd == "USB ON") {
    // sinal recebido da serial indicando que o PC está conectado
    lastSerialTime = millis();
  }
  else {
    Serial.println("Comando invalido.");
  }
}

// ======== TAREFA DO CORE 0 (lógica principal) ========
void taskCore0(void *pvParameters) {
  for (;;) {
    float v_batt = readBatteryVoltage(CANAL_TENSAO);
    float corrente = readCurrent();

    if (mode == AUTO) {
      if (v_batt <= V_BATT_MIN) {
        setDischarge(false);
        setCharge(true);
      } 
      else if (v_batt >= V_BATT_MAX) {
        setCharge(false);
        setDischarge(true);
      } 
      else if (v_batt > V_BATT_MIN_REENABLE && v_batt < V_BATT_MAX_REENABLE) {
        setCharge(false);
        setDischarge(false);
      }
    } 
    else {
      setCharge(forceCharge);
      setDischarge(forceDischarge);
    }

    Serial.print("Vbat: ");
    Serial.print(v_batt, 3);
    Serial.print(" V | Mode: ");
    Serial.print((mode == AUTO) ? "AUTO" : "MANUAL");
    Serial.print(" | Charge: ");
    Serial.print(forceCharge ? "ON" : "OFF");
    Serial.print(" | Disch: ");
    Serial.print(forceDischarge ? "ON" : "OFF");
    Serial.print(" | Corrente: ");
    Serial.print(corrente, 3);
    Serial.println(" A");
    
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

// ======== TAREFA DO CORE 1 (monitor USB) ========
void taskCore1(void *pvParameters) {
  for (;;) {
    if (Serial.available()) {
      String cmd = Serial.readStringUntil('\n');
      handleSerialCommand(cmd);
      lastSerialTime = millis(); // atualiza tempo da última comunicação
    }

    // verifica timeout
    if (millis() - lastSerialTime > TIMEOUT_USB) {
      // tempo limite sem comunicação USB
      setCharge(false);
      setDischarge(false);
      Serial.println("Sem comunicação USB há 10s — desligando relés.");
    }

    vTaskDelay(pdMS_TO_TICKS(100)); // checa a cada 100ms
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!ads.begin(0x49)) {
    Serial.println("Erro: ADS1115 nao inicializou!");
    while (1);
  }

  ads.setGain(GAIN_ONE);

  pinMode(PIN_CHARGE_CTRL_1, OUTPUT);
  pinMode(PIN_CHARGE_CTRL_2, OUTPUT);
  pinMode(PIN_DISCHARGE_CTRL, OUTPUT);

  setCharge(false);
  setDischarge(false);

  Serial.println("Sistema iniciado (modo MANUAL, CHARGE OFF / DISCH OFF).");
  Serial.println("Comandos: AUTO | CHARGE ON | CHARGE OFF | DISCH ON | DISCH OFF | USB ON");

  offset_corrente = lerMediaADC(CANAL_CORRENTE);
  Serial.print("Offset corrente: ");
  Serial.println(offset_corrente, 4);

  lastSerialTime = millis(); // inicia com tempo atual

  // Cria as tarefas nos dois núcleos
  xTaskCreatePinnedToCore(taskCore0, "TaskCore0", 8192, NULL, 1, &TaskCore0, 0);
  xTaskCreatePinnedToCore(taskCore1, "TaskCore1", 8192, NULL, 1, &TaskCore1, 1);
}

void loop() {
  // Nada — o FreeRTOS controla as tasks
}
