#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

// Resistores do divisor
const float R1 = 20000.0;  // entre Vbat e ADC
const float R2 = 26000.0;  // entre ADC e GND

// Limites de bateria
const float V_BATT_MIN = 3.0;
const float V_BATT_MIN_REENABLE = 3.05;
const float V_BATT_MAX = 4.2;
const float V_BATT_MAX_REENABLE = 4.15;

const int PIN_CHARGE_CTRL = 25;     
const int PIN_DISCHARGE_CTRL = 26;  

// Fator de calibração
float calib_factor = 1.0;  

const float ADS_VFSR = 4.096f;
const float ADC_COUNTS = 32767.0f;

enum Mode { AUTO, MANUAL };
Mode mode = AUTO;

bool forceCharge = true;
bool forceDischarge = true;

const int NUM_SAMPLES = 10;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!ads.begin(0x49)) {
    Serial.println("Erro: ADS1115 nao inicializou!");
    while (1);
  }
  ads.setGain(GAIN_ONE);

  pinMode(PIN_CHARGE_CTRL, OUTPUT);
  pinMode(PIN_DISCHARGE_CTRL, OUTPUT);

  // Inicializa desligado (LOW = relé desligado)
  digitalWrite(PIN_CHARGE_CTRL, LOW);
  digitalWrite(PIN_DISCHARGE_CTRL, LOW);

  Serial.println("Sistema iniciado.");
  Serial.println("Comandos: AUTO | CHARGE ON | CHARGE OFF | DISCH ON | DISCH OFF");
}

// Lê tensão no canal do ADS e retorna a tensão real da bateria
float readBatteryVoltage(uint8_t ch) {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += ads.readADC_SingleEnded(ch);
    delay(5);
  }
  float adc_avg = sum / (float)NUM_SAMPLES;
  float v_adc = adc_avg * (ADS_VFSR / ADC_COUNTS); // tensão no pino do ADC
  float v_batt = v_adc * (R1 + R2) / R2;           // tensão real da bateria
  v_batt *= calib_factor;                           // aplica calibração
  return v_batt;
}

void handleSerialCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "AUTO") {
    mode = AUTO;
    Serial.println("Modo AUTOMATICO ativado.");
  } 
  else if (cmd == "CHARGE ON") {
    mode = MANUAL; forceCharge = true;
    digitalWrite(PIN_CHARGE_CTRL, HIGH); // ativa imediatamente
    Serial.println("Modo MANUAL: carga FORCADA ON.");
  } 
  else if (cmd == "CHARGE OFF") {
    mode = MANUAL; forceCharge = false;
    digitalWrite(PIN_CHARGE_CTRL, LOW); // desativa imediatamente
    Serial.println("Modo MANUAL: carga FORCADA OFF.");
  } 
  else if (cmd == "DISCH ON") {
    mode = MANUAL; forceDischarge = true;
    digitalWrite(PIN_DISCHARGE_CTRL, HIGH); // ativa imediatamente
    Serial.println("Modo MANUAL: descarga FORCADA ON.");
  } 
  else if (cmd == "DISCH OFF") {
    mode = MANUAL; forceDischarge = false;
    digitalWrite(PIN_DISCHARGE_CTRL, LOW); // desativa imediatamente
    Serial.println("Modo MANUAL: descarga FORCADA OFF.");
  } 
  else {
    Serial.println("Comando invalido.");
  }
}

void loop() {
  float v_batt = readBatteryVoltage(0);

  // Lê comandos da Serial
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
    // Controle manual (força estado do relé conforme comandos)
    digitalWrite(PIN_CHARGE_CTRL, forceCharge ? HIGH : LOW);
    digitalWrite(PIN_DISCHARGE_CTRL, forceDischarge ? HIGH : LOW);
  }

  // Debug
  Serial.print("Vbat: "); Serial.print(v_batt, 3);
  Serial.print(" V | Mode: "); Serial.print((mode == AUTO) ? "AUTO" : "MANUAL");
  Serial.print(" | Charge: "); Serial.print(digitalRead(PIN_CHARGE_CTRL) ? "ON" : "OFF");
  Serial.print(" | Disch: "); Serial.println(digitalRead(PIN_DISCHARGE_CTRL) ? "ON" : "OFF");

  delay(500);
}