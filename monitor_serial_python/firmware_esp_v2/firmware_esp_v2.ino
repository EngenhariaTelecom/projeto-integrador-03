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
const int PIN_CHARGE_CTRL = 26;
const int PIN_DISCHARGE_CTRL = 25;

// Calibração da leitura de tensão
float calib_factor = 1.0;

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
Mode mode = AUTO;

bool forceCharge = true;
bool forceDischarge = true;

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

// Lê tensão da bateria (sem divisor de tensão)
float readBatteryVoltage(uint8_t ch) {
  float adc_avg = lerMediaADC(ch);
  float v_adc = adc_avg * (ADS_VFSR / ADC_COUNTS);
  v_adc *= calib_factor; // ajuste fino se necessário
  return v_adc;
}

// Lê corrente do sensor ACS712
float readCurrent() {
  float leitura = lerMediaADC(CANAL_CORRENTE);
  float tensao_mV = (leitura - offset_corrente) * (ADS_VFSR / ADC_COUNTS) * 1000.0;
  float corrente = tensao_mV / (SENSIBILIDADE * 1000.0); // A
  return corrente;
}

// Trata comandos recebidos pela Serial
void handleSerialCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "AUTO") {
    mode = AUTO;
    Serial.println("Modo AUTOMATICO ativado.");
  } 
  else if (cmd == "CHARGE ON") {
    mode = MANUAL; forceCharge = true;
    digitalWrite(PIN_CHARGE_CTRL, LOW);
    Serial.println("Modo MANUAL: carga FORCADA ON.");
  } 
  else if (cmd == "CHARGE OFF") {
    mode = MANUAL; forceCharge = false;
    digitalWrite(PIN_CHARGE_CTRL, HIGH);
    Serial.println("Modo MANUAL: carga FORCADA OFF.");
  } 
  else if (cmd == "DISCH ON") {
    mode = MANUAL; forceDischarge = true;
    digitalWrite(PIN_DISCHARGE_CTRL, LOW);
    Serial.println("Modo MANUAL: descarga FORCADA ON.");
  } 
  else if (cmd == "DISCH OFF") {
    mode = MANUAL; forceDischarge = false;
    digitalWrite(PIN_DISCHARGE_CTRL, HIGH);
    Serial.println("Modo MANUAL: descarga FORCADA OFF.");
  } 
  else {
    Serial.println("Comando invalido.");
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // I2C da ESP32

  if (!ads.begin(0x49)) {
    Serial.println("Erro: ADS1115 nao inicializou!");
    while (1);
  }

  ads.setGain(GAIN_ONE); // ±4.096 V

  pinMode(PIN_CHARGE_CTRL, OUTPUT);
  pinMode(PIN_DISCHARGE_CTRL, OUTPUT);

  digitalWrite(PIN_CHARGE_CTRL, HIGH);     // relé desligado
  digitalWrite(PIN_DISCHARGE_CTRL, HIGH);  // relé desligado

  Serial.println("Sistema iniciado.");
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
    if (v_batt < V_BATT_MIN) digitalWrite(PIN_DISCHARGE_CTRL, HIGH);
    else if (v_batt > V_BATT_MIN_REENABLE) digitalWrite(PIN_DISCHARGE_CTRL, LOW);

    if (v_batt > V_BATT_MAX) digitalWrite(PIN_CHARGE_CTRL, HIGH);
    else if (v_batt < V_BATT_MAX_REENABLE) digitalWrite(PIN_CHARGE_CTRL, LOW);
  } 
  else {
    // Controle manual
    digitalWrite(PIN_CHARGE_CTRL, forceCharge ? LOW : HIGH);
    digitalWrite(PIN_DISCHARGE_CTRL, forceDischarge ? LOW : HIGH);
  }

  // Saída de status no monitor serial
  Serial.print("Vbat: ");
  Serial.print(v_batt, 3);
  Serial.print(" V | Corrente: ");
  Serial.print(corrente, 3);
  Serial.print(" A | Mode: ");
  Serial.print((mode == AUTO) ? "AUTO" : "MANUAL");
  Serial.print(" | Charge: ");
  Serial.print(forceCharge ? "ON" : "OFF");
  Serial.print(" | Disch: ");
  Serial.println(forceDischarge ? "ON" : "OFF");

  delay(500);
}
