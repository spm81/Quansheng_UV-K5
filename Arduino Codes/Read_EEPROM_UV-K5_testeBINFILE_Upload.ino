//@2024 - Matoz ESP8266 / ESP32 UV-K5 Reader/Writer EEPROM

#include "FS.h"
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char *ssid = "UV-K5 EEPROM";
const char *password = "MTel";

#define SDA_PIN D2 // GPIO pin for SDA (Data)
#define SCL_PIN D1 // GPIO pin for SCL (Clock)
#define EEPROM_ADDRESS 0x50 // I2C address of the BL24C64 EEPROM
#define EEPROM_SIZE 0x2000 // Total size of the EEPROM (8192 bytes)

ESP8266WebServer server(80);
bool buttonPressed = false;
File fsUploadFile; // Temporary file to store uploaded data

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP8266 Control Interface</title></head><body><h1>ESP8266 Control Interface</h1><br><form method='POST' action='/upload' enctype='multipart/form-data'><input type='file' name='file'><input type='submit' value='Upload'></form><button onclick=\"startDownload()\">Start Download</button><br><button onclick=\"pressButton()\">Read EEPROM from radio and save it!!</button><br><button onclick=\"deleteFile()\">Delete File</button><br><button onclick=\"readEEPROM()\">Read EEPROM from Radio</button><br><button onclick=\"readEEPROMFile()\">Read EEPROM from File</button><br><script>function startDownload(){fetch('/download').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function pressButton(){fetch('/button').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function deleteFile(){fetch('/deletefile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROM(){fetch('/readeeprom').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROMFile(){fetch('/readeepromfile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}</script></body></html>";
  server.send(200, "text/html", html);
}

void handleReadEEPROM() {
  Serial.println("Reading EEPROM:");
 for (uint16_t offset = 0; offset < EEPROM_SIZE; offset += 16) {
    byte readData[16];
    EEPROM_ReadBuffer(offset, readData, sizeof(readData));

    Serial.print("Offset: 0x");
    if (offset < 0x1000) {
      Serial.print("0");
    }
    if (offset < 0x100) {
      Serial.print("0");
    }
    if (offset < 0x10) {
      Serial.print("0");
    }
    Serial.print(offset, HEX);
    Serial.print(" : ");

    // Mostrar os dados lidos no monitor serial
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x10) {
        Serial.print("0");
      }
      Serial.print(readData[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
      delay(5);
  }
  server.send(200, "text/plain", "EEPROM data printed in Serial");
}

void handleReadEEPROMFromFile() {
  File dataFile = SPIFFS.open("/eeprom_data.bin", "r");
  if (!dataFile) {
    Serial.println("Failed to open file for reading");
    return;
  }

  Serial.println("Reading EEPROM from file:");
  uint16_t offset = 0;
  while (offset < EEPROM_SIZE && dataFile.available()) {
    char readData[17]; // Buffer for data plus null terminator
    size_t bytesRead = dataFile.readBytes(readData, sizeof(readData) - 1); // Read one byte less to leave space for null terminator
    readData[bytesRead] = '\0'; // Null terminate the string

    Serial.print("Offset: 0x");
    if (offset < 0x1000) {
      Serial.print("0");
    }
    if (offset < 0x100) {
      Serial.print("0");
    }
    if (offset < 0x10) {
      Serial.print("0");
    }
    Serial.print(offset, HEX);
    Serial.print(" : ");

    // Show the read data on the serial monitor
    for (size_t i = 0; i < bytesRead; i++) {
      if (readData[i] < 0x10) {
        Serial.print("0");
      }
      Serial.print(readData[i], HEX);
      Serial.print(" ");
    }
    Serial.println();

    offset += bytesRead;
  }

  dataFile.close();
}




void handleUpload() {
  HTTPUpload& upload = server.upload();
  if (upload.status == UPLOAD_FILE_START) {
    Serial.printf("UploadStart: %s, total size: %u\n", upload.filename.c_str(), upload.totalSize);
    if (!SPIFFS.exists("/eeprom_data.bin")) {
      Serial.println("File does not exist. Creating new file.");
      File dataFile = SPIFFS.open("/eeprom_data.bin", "w+");
      if (!dataFile) {
        Serial.println("Failed to open file for writing");
        return;
      }
      dataFile.close();
    }
    fsUploadFile = SPIFFS.open("/temp.bin", "w+"); // Open temporary file for writing
    if (!fsUploadFile) {
      Serial.println("Failed to open temporary file for writing");
      return;
    }
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    Serial.printf("UploadWrite: %d Bytes\n", upload.currentSize);
    if (fsUploadFile) {
      int bytesWritten = fsUploadFile.write(upload.buf, upload.currentSize);
      if (bytesWritten != upload.currentSize) {
        Serial.println("Error writing to temporary file");
      }
    } else {
      Serial.println("Temporary file is not open");
    }
  } else if (upload.status == UPLOAD_FILE_END) {
    Serial.println("UploadEnd");

    // Close temporary file
    if (fsUploadFile) {
      fsUploadFile.close();
    } else {
      Serial.println("Temporary file is not open");
      return;
    }

    // Move temporary file to target file
    if (!SPIFFS.rename("/temp.bin", "/eeprom_data.bin")) {
      Serial.println("Failed to move temporary file to target file");
      return;
    }

    // Respond to the client
    server.send(200, "text/plain", "File uploaded successfully");

    // Print file contents for debugging
    File dataFile = SPIFFS.open("/eeprom_data.bin", "r");
    if (!dataFile) {
      Serial.println("Failed to open file for reading");
      return;
    }
    Serial.println("File contents:");
    while (dataFile.available()) {
      Serial.write(dataFile.read());
    }
    dataFile.close();
  }
}


void handleDownload() {
  File dataFile = SPIFFS.open("/eeprom_data.bin", "r");
  if (!dataFile) {
    server.send(500, "text/plain", "Failed to open file for reading");
    Serial.println("Failed to open file for reading");
    return;
  }
  server.streamFile(dataFile, "application/octet-stream");
  dataFile.close();
}

void handleButton() {
  buttonPressed = true;
  server.send(200, "text/plain", "Button pressed");
}

void handleDeleteFile() {
  if (SPIFFS.remove("/eeprom_data.bin")) {
    server.send(200, "text/plain", "File deleted successfully");
  } else {
    server.send(500, "text/plain", "Failed to delete file");
  }
}

void setup() {
  Serial.begin(38400);
  delay(100);

  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount file system");
    return;
  }

  Wire.begin(SDA_PIN, SCL_PIN);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  Serial.println("Access Point (AP) started");
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());

  pinMode(D3, INPUT_PULLUP);

  server.on("/", handleRoot);
  server.on("/upload", HTTP_POST, handleUpload); // Added upload handling
  server.on("/download", HTTP_GET, handleDownload);
  server.on("/button", handleButton);
  server.on("/deletefile", HTTP_GET, handleDeleteFile);
  server.on("/readeeprom", HTTP_GET, handleReadEEPROM); // Nova rota para ler eeprom
  server.on("/readeepromfile", HTTP_GET, handleReadEEPROMFromFile); // Add new route

  server.begin();
  Serial.println("HTTP server started");

  Serial.println("Setup complete");
}

void loop() {
  server.handleClient();

  if (buttonPressed) {
    // Open file for writing
    File dataFile = SPIFFS.open("/eeprom_data.bin", "w");
    if (!dataFile) {
      server.send(500, "text/plain", "Failed to open file for writing");
      return;
    }

    // Read EEPROM and write to file
    for (uint16_t offset = 0; offset < EEPROM_SIZE; offset++) {
      byte readData;
      EEPROM_ReadBuffer(offset, &readData, 1);
      dataFile.write(&readData, 1);
    }

    // Close file
    dataFile.close();

    // Reset buttonPressed flag
    buttonPressed = false;
  }
}

void EEPROM_ReadBuffer(uint16_t Address, void *pBuffer, uint16_t Size) {
  Wire.beginTransmission(EEPROM_ADDRESS);
  Wire.write((byte)(Address >> 8)); // most significant byte
  Wire.write((byte)(Address & 0xFF)); // least significant byte
  Wire.endTransmission();
  Wire.requestFrom(EEPROM_ADDRESS, Size);
  byte *ptr = (byte *)pBuffer;
  for (uint16_t i = 0; i < Size; i++) {
    if (Wire.available()) {
      *ptr = Wire.read();
      ptr++;
    }
  }
}
