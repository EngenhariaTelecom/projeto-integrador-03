#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

// ======== CONFIGURAÇÃO GERAL ========

// Limites de tensão da bateria 3,7 V (Li-Ion / LiPo)
const float V_BATT_MIN = 3.0;
const float V_BATT_MIN_REENABLE = 3.05;
const float V_BATT_MAX = 4.2;
const float V_BATT_MAX_REENABLE = 4.15;

// Pinos dos relés
const int PIN_CHARGE_CTRL_1 = 25;
const int PIN_CHARGE_CTRL_2 = 26;
const int PIN_DISCHARGE_CTRL = 27;

// ======== SENSOR DE TENSAO ========
const float DIVISOR = 5.0;
const float OFFSET_ADC = 0.50;   // volts medidos SEM carga

// ADS1115
const float ADS_VFSR = 4.096f;     // ±4.096 V (GAIN_ONE)
const float ADC_COUNTS = 32767.0f;

// ======== SENSOR DE CORRENTE (ACS712) ========
const float SENSIBILIDADE = 0.066;  // V/A (para ACS712-30A)
const int CANAL_CORRENTE = 1;       // A1 do ADS1115
const int NUM_AMOSTRAS = 20;
float offset_corrente = 0.0;

// ======== CANAL DE LEITURA DA TENSÃO ========
const int CANAL_TENSAO = 0; // A0 do ADS1115

// ======== MODO DE OPERAÇÃO ========
enum Mode { AUTO, MANUAL };
Mode mode = MANUAL;  // inicia no modo MANUAL

bool forceCharge = false;    // carga OFF
bool forceDischarge = false; // descarga OFF

// ======== FUNÇÕES AUXILIARES ========

// Faz média de várias amostras do ADC
float lerMediaADC(uint8_t canal) {
  long soma = 0;
  for (int i = 0; i < NUM_AMOSTRAS; i++) {
    soma += ads.readADC_SingleEnded(canal);
    delay(5);
  }
  return soma / (float)NUM_AMOSTRAS;
}

// Lê tensão da bateria
float readBatteryVoltage(uint8_t ch) {

  int16_t adc_raw = lerMediaADC(ch);

  float v_adc = adc_raw * (ADS_VFSR / ADC_COUNTS);

  // --- DETECTAR DESCONEXÃO ---
  // Se a leitura for muito baixa (< 0.20 V na entrada do ADS),
  // significa provavelmente que não existe bateria.
  if (v_adc < 0.20) {
    return 0.0;
  }

  // Caso contrário, bateria conectada → apenas converter normalmente
  float v_real = v_adc * DIVISOR;
  return v_real;
}

// Lê corrente do sensor ACS712
float readCurrent() {
  float leitura = lerMediaADC(CANAL_CORRENTE);
  float tensao_mV = (leitura - offset_corrente) * (ADS_VFSR / ADC_COUNTS) * 1000.0;
  float corrente = tensao_mV / (SENSIBILIDADE * 1000.0); // A
  return corrente;
}

// ======== CONTROLE DOS RELÉS ========
void setCharge(bool on) {
  digitalWrite(PIN_CHARGE_CTRL_1, on ? LOW : HIGH);
  digitalWrite(PIN_CHARGE_CTRL_2, on ? LOW : HIGH);
}

void setDischarge(bool on) {
  digitalWrite(PIN_DISCHARGE_CTRL, on ? LOW : HIGH);
}

// ======== COMANDOS VIA SERIAL ========
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
  else {
    Serial.println("Comando invalido.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Wire.begin(21, 22); // I2C da ESP32

  if (!ads.begin(0x49)) {
    Serial.println("Erro: ADS1115 nao inicializou!");
    while (1);
  }

  ads.setGain(GAIN_ONE); // ±4.096 V

  pinMode(PIN_CHARGE_CTRL_1, OUTPUT);
  pinMode(PIN_CHARGE_CTRL_2, OUTPUT);
  pinMode(PIN_DISCHARGE_CTRL, OUTPUT);

  // Todos os relés desligados (HIGH)
  setCharge(false);
  setDischarge(false);

  Serial.println("Sistema iniciado.");
  Serial.println("Iniciando em modo MANUAL (CHARGE OFF / DISCH OFF).");
  Serial.println("Comandos: AUTO | CHARGE ON | CHARGE OFF | DISCH ON | DISCH OFF");

  // Calibra offset de corrente
  Serial.println("Calibrando offset de corrente (sem carga)...");
  offset_corrente = lerMediaADC(CANAL_CORRENTE);
  Serial.print("Offset corrente: ");
  Serial.println(offset_corrente, 4);
}

void loop() {
  float v_batt = readBatteryVoltage(CANAL_TENSAO);
  float corrente = readCurrent();

  // Leitura de comandos pela Serial
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    handleSerialCommand(cmd);
  }

  if (mode == AUTO) {
    // Controle automático com histerese
    if (v_batt <= V_BATT_MIN) {
      setDischarge(false);
      setCharge(true);
    } 
    else if (v_batt >= V_BATT_MAX) {
      setCharge(false);
      setDischarge(true);
    } 
    else if (v_batt > V_BATT_MIN_REENABLE && v_batt < V_BATT_MAX_REENABLE) {
      // dentro da faixa segura
      setCharge(false);
      setDischarge(false);
    }
  } 
  else {
    // Controle manual
    setCharge(forceCharge);
    setDischarge(forceDischarge);
  }

  // Saída de status no monitor serial
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

  delay(500);
}
