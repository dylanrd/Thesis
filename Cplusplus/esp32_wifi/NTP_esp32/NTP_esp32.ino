#include <WiFi.h>
#include <time.h>
#include <sys/time.h>

// Replace with your WiFi credentials
const char* ssid = "durand.rebel@kpnplanet.nl";
const char* password = "RMD687101";

// NTP server
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600; // Adjust for your timezone
const int daylightOffset_sec = 3600; // Adjust for daylight savings

void setup() {
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, -1, 17)
  // Connect to Wi-Fi
  Serial.print("Connecting to Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");

  // Initialize time with NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.println("Waiting for NTP time sync...");

  // Wait until time is set
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Time synchronized!");
}

void loop() {
  // Get time with millisecond precision
  struct timeval tv;
  gettimeofday(&tv, NULL);

  // Extract seconds and milliseconds
  time_t seconds = tv.tv_sec;
  int milliseconds = tv.tv_usec / 1000;

  // Convert to human-readable time
  struct tm* timeinfo = localtime(&seconds);
  char timeString[64];
  strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", timeinfo);

  // Print the full time including milliseconds
  Serial.printf("Current time: %s.%03d\n", timeString, milliseconds);
  Serial1.printf("%s.%03d\n", timeString, milliseconds);
  delay(10); // Update every second
}
