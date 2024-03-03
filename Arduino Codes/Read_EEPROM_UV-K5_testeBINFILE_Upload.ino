//@2024 - Matoz ESP8266 / ESP32 UV-K5 Reader/Writer EEPROM

//#define ENABLE_AP //Remove "//" if you want ESP8266 to act as an Acess Point

#include "FS.h"
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <EEPROM.h> // Include the EEPROM library

const char *ssid = "ENFERMEIRAANACOSTA.PT";
const char *password = "Matos@Costa";

#define SDA_PIN D2 // GPIO pin for SDA (Data)
#define SCL_PIN D1 // GPIO pin for SCL (Clock)
#define EEPROM_ADDRESS 0x50 // I2C address of the BL24C64 EEPROM
#define EEPROM_SIZE 0x2000 // Total size of the EEPROM (8192 bytes)

ESP8266WebServer server(80);
bool buttonPressed = false;
File fsUploadFile; // Temporary file to store uploaded data

/*void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP8266 Control Interface</title></head><body><h1>ESP8266 Control Interface</h1><br><br><br><form method='POST' action='/writeeeprom'><label for='offset'>Offset:</label><input type='text' id='offset' name='offset'><br><br><label for='data'>Data (16 bytes, separated by spaces):</label><input type='text' id='data' name='data'><br><br><input type='submit' value='Write EEPROM'></form><br><br><button onclick=\"startDownload()\">Start Download</button><br><br><button onclick=\"pressButton()\">Read EEPROM from radio and save it!!</button><br><br><button onclick=\"deleteFile()\">Delete File</button><br><br><button onclick=\"readEEPROM()\">Read EEPROM from Radio</button><br><br><button onclick=\"readEEPROMFile()\">Read EEPROM from File</button><br><br><script>function startDownload(){fetch('/download').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function pressButton(){fetch('/button').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function deleteFile(){fetch('/deletefile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROM(){fetch('/readeeprom').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROMFile(){fetch('/readeepromfile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}</script></body></html>";
  server.send(200, "text/html", html);

  }

  void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>ESP8266 Control Interface</title></head><body><h1>ESP8266 Control Interface</h1><br><br><br><form method='GET' action='/readeepromoffset'><label for='offsetSelect'>Offset Select:</label><input type='text' id='offsetSelect' name='offsetSelect'><p><input type='submit' value='Read EEPROM From Radio at Offset'></form><br><br><button onclick=\"startDownload()\">Start Download</button><br><br><button onclick=\"pressButton()\">Read EEPROM from radio and save it!!</button><br><br><button onclick=\"deleteFile()\">Delete File</button><br><br><button onclick=\"readEEPROM()\">Read EEPROM from Radio</button><br><br><button onclick=\"readEEPROMFile()\">Read EEPROM from File</button><br><br><script>function startDownload(){fetch('/download').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function pressButton(){fetch('/button').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function deleteFile(){fetch('/deletefile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROM(){fetch('/readeeprom').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}function readEEPROMFile(){fetch('/readeepromfile').then(response => response.text()).then(data => alert(data)).catch(error => console.error('Error:', error));}</script></body></html>";
  server.send(200, "text/html", html);
  }

  void handleRoot() {
  String html =
  "<!DOCTYPE html>\
  <html>\
  <head>\
    <title>ESP8266 Control Interface</title>\
  </head>\
  <body>\
    <h1>ESP8266 Control Interface</h1>\
    <br><br><br>\
    <form method='GET' action='/readeepromoffset'>\
      <label for='offsetSelect'>Offset Select:</label>\
      <input type='text' id='offsetSelect' name='offsetSelect'>\
      <p><input type='submit' value='Read EEPROM From Radio at Offset'>\
    </form>\
    <br>\
    <button onclick=\"startDownload()\">Start Download</button>\
    <br><br>\
    <button onclick=\"pressButton()\">Read EEPROM from radio and save it!!</button>\
    <br><br>\
    <button onclick=\"deleteFile()\">Delete File</button>\
    <br><br>\
    <button onclick=\"readEEPROM()\">Read EEPROM from Radio</button>\
    <br><br>\
    <button onclick=\"readEEPROMFile()\">Read EEPROM from File</button>\
    <br><br>\
    <button onclick=\"uploadToEEPROM()\">Upload eeprom_data.bin file to radio EEPROM</button><br><br>\
    <script>\
      function startDownload(){\
        fetch('/download')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
      function pressButton(){\
        fetch('/button')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
      function deleteFile(){\
        fetch('/deletefile')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
      function readEEPROM(){\
        fetch('/readeeprom')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
      function readEEPROMFile(){\
        fetch('/readeepromfile')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
      function uploadToEEPROM(){\
        fetch('/uploadToEEPROM')\
          .then(response => response.text())\
          .then(data => alert(data))\
          .catch(error => console.error('Error:', error));\
      }\
    </script>\
  </body>\
  </html>";

  server.send(200, "text/html", html);
  }

  void handleRoot() {
  String html = "<html>\
  <head>\
  <title>ESP8266 Control Interface</title>\
  </head>\
  <body style=\"color: rgb(51, 255, 51); background-color: rgb(1, 1, 1);\" alink=\"#000099\" link=\"#000099\" vlink=\"#990099\">\
  <h1>ESP8266 Control Interface</h1>\
  <br><br><br>\
  <form method=\"get\" action=\"/readeepromoffset\">\
    <label for=\"offsetSelect\">Offset Select:</label>\
    <input id=\"offsetSelect\" name=\"offsetSelect\" type=\"text\">\
    <input value=\"Read EEPROM From Radio at Offset\" type=\"submit\"><br><br>\
  </form>\
  <button onclick='startDownload()'>Start Download</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='pressButton()'>Read EEPROM from radio and save it!!</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='deleteFile()'>Delete File</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='readEEPROM()'>Read EEPROM from Radio</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='readEEPROMFile()'>Read EEPROM from File</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='uploadToEEPROM()'>Upload eeprom_data.bin file to radio EEPROM</button><br><br>\
  <script>\
    function startDownload(){\
      fetch('/download')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function pressButton(){\
      fetch('/button')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function deleteFile(){\
      fetch('/deletefile')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function readEEPROM(){\
      fetch('/readeeprom')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function readEEPROMFile(){\
      fetch('/readeepromfile')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function uploadToEEPROM(){\
      fetch('/uploadToEEPROM')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
  </script>\
  </body>\
  </html>";

  server.send(200, "text/html", html);
  }

void handleRoot() {
  String html = "<html>\
<head>\
  <title>ESP8266 Control Interface</title>\
</head>\
<body style=\"color: rgb(51, 255, 51); background-color: rgb(1, 1, 1);\" alink=\"#000099\" link=\"#000099\" vlink=\"#990099\">\
  <h1>ESP8266 Control Interface</h1>\
  <br><br><br>\
  <form method=\"get\" action=\"/readeepromoffset\">\
    <label for=\"offsetSelect\">Offset Select:</label>\
    <input id=\"offsetSelect\" name=\"offsetSelect\" type=\"text\">\
    <input value=\"Read EEPROM From Radio at Offset\" type=\"submit\"><br><br>\
  </form>\
  <button onclick='startDownload()'>Start Download</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='pressButton()'>Read EEPROM from radio and save it!!</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='deleteFile()'>Delete File</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='readEEPROM()'>Read EEPROM from Radio</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='readEEPROMFile()'>Read EEPROM from File</button>\
  &nbsp;&nbsp;&nbsp; \
  <button onclick='uploadToEEPROM()'>Upload eeprom_data.bin file to radio EEPROM</button><br><br>\
  <button onclick='uploadFromWWW()'>Upload From WWW</button>\
  <input id=\"fileURL\" type=\"text\" placeholder=\"Enter file URL\"><br><br>\
  <script>\
    function startDownload(){\
      fetch('/download')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function pressButton(){\
      fetch('/button')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function deleteFile(){\
      fetch('/deletefile')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function readEEPROM(){\
      fetch('/readeeprom')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function readEEPROMFile(){\
      fetch('/readeepromfile')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function uploadToEEPROM(){\
      fetch('/uploadToEEPROM')\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
    function uploadFromWWW(){\
      var fileURL = document.getElementById('fileURL').value;\
      fetch('/uploadFromWWW?fileURL=' + fileURL)\
        .then(response => response.text())\
        .then(data => alert(data))\
        .catch(error => console.error('Error:', error));\
    }\
  </script>\
</body>\
</html>";

  server.send(200, "text/html", html);
}
*/

void handleRoot() {
  String html = "<html>\
<head>\
<title>ESP8266 Control Interface</title>\
</head>\
<body style=\"color: rgb(51, 255, 51); background-color: rgb(1, 1, 1);\" alink=\"#000099\" link=\"#000099\" vlink=\"#990099\">\
<h1 style=\"text-align: center;\">ESP8266 EEPROM Reader/Writer by Matoz</h1>\
<br>\
<br>\
<table style=\"text-align: left; width: 1427px; height: 154px; margin-left: auto; margin-right: auto;\" border=\"1\" cellpadding=\"2\" cellspacing=\"2\">\
<tbody>\
<tr>\
<td style=\"vertical-align: top; text-align: center;\"><span style=\"font-weight: bold;\">READING</span><br>\
</td>\
<td style=\"vertical-align: top; text-align: center;\"><span style=\"font-weight: bold;\">UPLOAD</span><br>\
</td>\
<td style=\"vertical-align: top; text-align: center;\"><span style=\"font-weight: bold;\">DOWNLOAD</span><br>\
</td>\
<td style=\"vertical-align: top; text-align: center;\"><span style=\"font-weight: bold;\">DELETE</span><br>\
</td>\
</tr>\
<tr>\
<td style=\"vertical-align: top;\"><label for=\"offsetSelect\">Offset Select: (From 0000 to 1FF0)</label> <input id=\"offsetSelect\" name=\"offsetSelect\" type=\"text\"> <input value=\"Read EEPROM From Radio at Offset\" type=\"submit\"></td>\
<td style=\"vertical-align: top;\"><button onclick=\"uploadToEEPROM()\">Upload eeprom_data.bin file to radio EEPROM</button></td>\
<td style=\"vertical-align: top;\"><button onclick=\"startDownload()\">Download eeprom_data.bin file</button></td>\
<td style=\"vertical-align: top; text-align: left;\"><button onclick=\"deleteFile()\">Delete eeprom_data.bin File</button></td>\
</tr>\
<tr>\
<td style=\"vertical-align: top;\"><button onclick=\"readEEPROM()\">Read EEPROM from Radio</button></td>\
<td style=\"vertical-align: top;\"><button onclick=\"uploadFromWWW()\">Upload From WWW</button> <input id=\"fileURL\" placeholder=\"Enter file URL\" type=\"text\"></td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
</tr>\
<tr>\
<td style=\"vertical-align: top;\"><button onclick=\"pressButton()\">Read EEPROM from radio and save it!!</button></td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
</tr>\
<tr>\
<td style=\"vertical-align: top; text-align: left;\"><button onclick=\"readEEPROMFile()\">Read EEPROM from eeprom_data.bin File</button></td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
<td style=\"vertical-align: top;\"><br>\
</td>\
</tr>\
</tbody>\
</table>\
<br>\
<br>\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp; <br>\
<br>\
<br>\
<br>\
<script>\
function startDownload(){\
fetch('/download')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function pressButton(){\
fetch('/button')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function deleteFile(){\
fetch('/deletefile')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function readEEPROM(){\
fetch('/readeeprom')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function readEEPROMFile(){\
fetch('/readeepromfile')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function uploadToEEPROM(){\
fetch('/uploadToEEPROM')\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
function uploadFromWWW(){\
var fileURL = document.getElementById('fileURL').value;\
fetch('/uploadFromWWW?fileURL=' + fileURL)\
.then(response => response.text())\
.then(data => alert(data))\
.catch(error => console.error('Error:', error));\
}\
</script>\
</body>\
</html>";\
  server.send(200, "text/html", html);
}




/*
  void handleReadEEPROMOffsetFromRadio() {
  // Verifica se foi enviado o argumento (offsetSelect)
  if (server.args() == 1) {
    uint16_t offset = (uint16_t) strtol(server.arg("offsetSelect").c_str(), NULL, 16); // Obtém o offset selecionado

    // Verifica se o offset está dentro dos limites da EEPROM
    if (offset >= EEPROM_SIZE) {
      server.send(400, "text/plain", "Erro: Offset fora dos limites da EEPROM");
      return;
    }

    // Lê os 16 bytes a partir do offset selecionado
    byte readData[16];
    EEPROM_ReadBuffer(offset, readData, sizeof(readData));

    // Constrói uma string com os dados lidos
    String responseData = "Decoded text: ";
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x20 || readData[i] > 0x7E) { // Fora do intervalo ASCII imprimível
        responseData += ".";
      } else {
        responseData += (char)readData[i];
      }
    }
    responseData += "\nRaw data: ";
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x10) {
        responseData += "0";
      }
      responseData += String(readData[i], HEX);
      responseData += " ";
    }

    server.send(200, "text/plain", responseData);
  } else {
    server.send(400, "text/plain", "Erro: Deve enviar um argumento (offsetSelect)");
  }
  }
*/
void handleReadEEPROMOffsetFromRadio() {
  // Verifica se foi enviado o argumento (offsetSelect)
  if (server.args() == 1) {
    uint16_t offset = (uint16_t) strtol(server.arg("offsetSelect").c_str(), NULL, 16); // Obtém o offset selecionado

    // Verifica se o offset está dentro dos limites da EEPROM
    if (offset >= EEPROM_SIZE) {
      server.send(400, "text/plain", "Erro: Offset fora dos limites da EEPROM");
      return;
    }

    // Lê os 16 bytes a partir do offset selecionado
    byte readData[16];
    EEPROM_ReadBuffer(offset, readData, sizeof(readData));

    // Constrói uma string com os dados lidos
    String responseData = "Raw data: ";
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x10) {
        responseData += "0";
      }
      responseData += String(readData[i], HEX);
      responseData += " ";
    }
    responseData += "     Decoded text: ";
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x20 || readData[i] > 0x7E) { // Fora do intervalo ASCII imprimível
        responseData += ".";
      } else {
        responseData += (char)readData[i];
      }
    }

    server.send(200, "text/plain", responseData);
  } else {
    server.send(400, "text/plain", "Erro: Deve enviar um argumento (offsetSelect)");
  }
}





/*
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
*/
void handleReadEEPROM() {
  String responseData = "Reading EEPROM:\n";
  for (uint16_t offset = 0; offset < EEPROM_SIZE; offset += 16) {
    byte readData[16];
    EEPROM_ReadBuffer(offset, readData, sizeof(readData));

    responseData += "Offset: 0x";
    if (offset < 0x1000) {
      Serial.print("0");
      responseData += "0";
    }
    if (offset < 0x100) {
      Serial.print("0");
      responseData += "0";
    }
    if (offset < 0x10) {
      Serial.print("0");
      responseData += "0";
    }
    Serial.print(offset, HEX);
    Serial.print(" : ");
    responseData += String(offset, HEX);
    responseData += " : ";


    // Add raw data to response
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x10) {
        Serial.print("0");
        responseData += "0";
      }
      Serial.print(readData[i], HEX);
      Serial.print(" ");
      responseData += String(readData[i], HEX);
      responseData += " ";
    }

    responseData += "     Decoded text: ";
    // Add decoded text to response
    for (int i = 0; i < sizeof(readData); i++) {
      if (readData[i] < 0x20 || readData[i] > 0x7E) { // Outside printable ASCII range
        responseData += ".";
        Serial.print(".");
      } else {
        Serial.print((char)readData[i]);
        responseData += (char)readData[i];
      }
    }
    Serial.println();
    responseData += "\n";
    delay(50);
  }
  server.send(200, "text/plain", responseData);
}


////Escreve em DECODED TEXT
/*
  void handleWriteEEPROM() {
  if (server.method() == HTTP_POST) {
    uint16_t address = server.arg("address").toInt();
    String data = server.arg("data");

    Wire.beginTransmission(EEPROM_ADDRESS);
    Wire.write((byte)(address >> 8)); // Most significant byte
    Wire.write((byte)(address & 0xFF)); // Least significant byte

    for (size_t i = 0; i < data.length(); i++) {
      Wire.write(data[i]);
    }

    Wire.endTransmission();

    server.send(200, "text/plain", "Write successful");
  } else {
    server.send(405, "text/plain", "Method Not Allowed");
  }
  }
*/
void handleWriteEEPROM() {
  if (server.method() == HTTP_POST) {
    String addressStr = server.arg("address");
    uint16_t address = strtoul(addressStr.c_str(), NULL, 16); // Parse address as hexadecimal

    String hexData = server.arg("data");

    Wire.beginTransmission(EEPROM_ADDRESS);
    Wire.write((byte)(address >> 8)); // Byte mais significativo
    Wire.write((byte)(address & 0xFF)); // Byte menos significativo

    // Escreve os dados hexadecimais diretamente na EEPROM
    for (size_t i = 0; i < hexData.length(); i += 2) {
      String hexByte = hexData.substring(i, i + 2);
      byte byteValue = (byte) strtol(hexByte.c_str(), NULL, 16);
      Wire.write(byteValue);
    }

    Wire.endTransmission();

    server.send(200, "text/plain", "Escrita bem sucedida");
  } else {
    server.send(405, "text/plain", "Método não permitido");
  }
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
    fsUploadFile = SPIFFS.open("/eeprom_data.bin", "w"); // Open the EEPROM data file for writing
    if (!fsUploadFile) {
      Serial.println("Failed to open file for writing");
      return;
    }
  } else if (upload.status == UPLOAD_FILE_WRITE) {
    if (fsUploadFile) {
      int bytesWritten = fsUploadFile.write(upload.buf, upload.currentSize);
      if (bytesWritten != upload.currentSize) {
        Serial.println("Error writing to file");
      }
    } else {
      Serial.println("File is not open");
    }
  } else if (upload.status == UPLOAD_FILE_END) {
    if (fsUploadFile) {
      fsUploadFile.close();
    } else {
      Serial.println("File is not open");
      return;
    }

    server.send(200, "text/plain", "File uploaded successfully");
  }
}

void handleUploadToEEPROM() {
  File dataFile = SPIFFS.open("/eeprom_data.bin", "r");
  if (!dataFile) {
    server.send(500, "text/plain", "Failed to open file for reading");
    Serial.println("Failed to open file for reading");
    return;
  }

  // Write EEPROM data
  for (uint16_t offset = 0; offset < EEPROM_SIZE; offset++) {
    byte readData;
    size_t bytesRead = dataFile.read(&readData, sizeof(readData));
    if (bytesRead == 0) {
      // End of file reached, break the loop
      break;
    }
    EEPROM_WriteBuffer(offset, &readData, sizeof(readData));
  }

  // Close file
  dataFile.close();

  server.send(200, "text/plain", "EEPROM Data Uploaded Successfully");
}

/*
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

*/
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

/*
  void handleUploadFromWWW() {
  String fileURL = server.arg("fileURL");

  // Verifica se o URL do arquivo foi fornecido
  if (fileURL.isEmpty()) {
    server.send(400, "text/plain", "Erro: URL do arquivo não fornecido");
    return;
  }

  // Faz a solicitação HTTP para obter o arquivo binário
  HTTPClient http;
  http.begin(fileURL);
  int httpCode = http.GET();

  // Verifica se a solicitação HTTP foi bem-sucedida
  if (httpCode != HTTP_CODE_OK) {
    server.send(500, "text/plain", "Erro ao obter o arquivo do URL fornecido");
    http.end();
    return;
  }

  // Cria um buffer para armazenar os dados do arquivo
  const size_t bufferSize = 2048;
  uint8_t buffer[bufferSize];
  size_t readSize = 0;

  // Abre a EEPROM para escrita
  EEPROM.begin(EEPROM_SIZE);

  // Lê os dados do arquivo e escreve na EEPROM
  size_t offset = 0;
  WiFiClient *stream = http.getStreamPtr();
  while (http.connected() && (readSize = stream->readBytes(buffer, bufferSize)) > 0) {
    for (size_t i = 0; i < readSize; i++) {
      EEPROM.write(offset + i, buffer[i]);
    }
    offset += readSize;
    Serial.printf("Bytes lidos: %d, Offset: %d\n", readSize, offset);
  }

  // Finaliza a escrita na EEPROM e fecha a conexão HTTP
  EEPROM.commit();
  http.end();

  server.send(200, "text/plain", "Upload do arquivo a partir de URL bem-sucedido");
  }

*/



void handleUploadFromWWW() {
  String fileURL = server.arg("fileURL");

  // Verifica se o URL do arquivo foi fornecido
  if (fileURL.isEmpty()) {
    server.send(400, "text/plain", "Erro: URL do arquivo não fornecido");
    return;
  }

  // Faz a solicitação HTTP para obter o arquivo binário
  HTTPClient http;
  http.begin(fileURL);
  int httpCode = http.GET();

  // Verifica se a solicitação HTTP foi bem-sucedida
  if (httpCode != HTTP_CODE_OK) {
    server.send(500, "text/plain", "Erro ao obter o arquivo do URL fornecido");
    http.end();
    return;
  }

  // Cria um buffer para armazenar os dados do arquivo
  const size_t bufferSize = 16;
  uint8_t buffer[bufferSize];
  size_t readSize = 0;

  // Abre a EEPROM para escrita
  EEPROM.begin(EEPROM_SIZE);

  // Lê os dados do arquivo e escreve na EEPROM
  size_t offset = 0;
  WiFiClient *stream = http.getStreamPtr();
  unsigned long previousMillis = millis();  // Variable to store the last time the delay was updated
  const unsigned long delayInterval = 100; // Delay interval in milliseconds
  
  while (http.connected() && (readSize = stream->readBytes(buffer, bufferSize)) > 0) {
    EEPROM_WriteBuffer(offset, buffer, readSize); // Escreve os dados do buffer na EEPROM
    offset += readSize;
    Serial.printf("Bytes lidos: %d, Offset: %04X\n", readSize, offset); // Imprime o número de bytes lidos e o offset em hexadecimal
    printHex(buffer, readSize, offset - readSize); // Imprime os bytes em formato hexadecimal e texto legível
    
    // Check if it's time to apply delay
    if (millis() - previousMillis >= delayInterval) {
      delay(delayInterval); // Apply delay
      previousMillis = millis(); // Update the previous time
    }
  }

  // Finaliza a escrita na EEPROM e fecha a conexão HTTP
  EEPROM.commit();
  http.end();

  server.send(200, "text/plain", "Upload do arquivo a partir de URL bem-sucedido");
}








void setup() {
  Serial.begin(38400);
  delay(100);

  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount file system");
    return;
  }

  Wire.begin(SDA_PIN, SCL_PIN);

#ifdef ENABLE_AP
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  Serial.println("Access Point (AP) started");
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
#else
  // Change WiFi mode to Station (client) mode
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); // Connect to the WiFi network

  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
#endif
  pinMode(D3, INPUT_PULLUP);

  server.on("/", handleRoot);
  server.on("/upload", HTTP_POST, handleUpload); // Added upload handling
  server.on("/download", HTTP_GET, handleDownload);
  server.on("/button", handleButton);
  server.on("/deletefile", HTTP_GET, handleDeleteFile);
  server.on("/readeeprom", HTTP_GET, handleReadEEPROM); // Nova rota para ler eeprom
  server.on("/readeepromfile", HTTP_GET, handleReadEEPROMFromFile); // Add new route
  server.on("/writeeeprom", HTTP_POST, handleWriteEEPROM);
  server.on("/readeepromoffset", HTTP_GET, handleReadEEPROMOffsetFromRadio);
  server.on("/uploadToEEPROM", handleUploadToEEPROM);
  server.on("/uploadFromWWW", HTTP_GET, handleUploadFromWWW);

  server.begin();
  Serial.println("HTTP server started & Setup Complete, ready to use!!!");
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

void EEPROM_WriteBuffer(uint16_t Address, const void *pBuffer, uint16_t Size) {
  Wire.beginTransmission(EEPROM_ADDRESS);
  Wire.write((byte)(Address >> 8)); // byte mais significativo
  Wire.write((byte)(Address & 0xFF)); // byte menos significativo
  const byte *ptr = (const byte *)pBuffer;
  for (uint16_t i = 0; i < Size; i++) {
    Wire.write(*ptr);
    ptr++;
  }
  Wire.endTransmission();
#ifdef ENABLE_250ms
  delay(250);
#else    
  delay(10); // delay necessário para garantir que a escrita seja concluída
#endif
}

void printHex(uint8_t *data, size_t len, uint32_t offset) {
  char buf[9];
  for (size_t i = 0; i < len; i += 16) {
    sprintf(buf, "%04X : ", offset + i);
    Serial.print(buf);
    for (size_t j = i; j < min(i + 16, len); j++) {
      sprintf(buf, "%02X ", data[j]);
      Serial.print(buf);
    }
    for (size_t j = 0; j < (16 - (len - i > 16 ? 0 : 16 - len + i)); j++) {
      Serial.print("   ");
    }
    Serial.print(" ");
    for (size_t j = i; j < min(i + 16, len); j++) {
      if (isprint(data[j])) {
        Serial.print((char)data[j]);
      } else {
        Serial.print(".");
      }
    }
    Serial.println();
  }
}
