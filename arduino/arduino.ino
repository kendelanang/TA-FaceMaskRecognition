#include <NewPing.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h> // Connection of the library
#include <Adafruit_MLX90614.h>

LiquidCrystal_I2C lcd(0x27,16,2); //Indicate I2C address (the most common value), as well as screen parameters (in case of LCD 1602 - 2 lines of 16 characters each 
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

#define TRIGGER_PIN  9
#define ECHO_PIN     10
#define MAX_DISTANCE 400 // Maximum distance we want to measure (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  Serial.begin(9600);
  mlx.begin();
  lcd.begin(); // Initialize display  
  lcd.backlight(); // connecting backlight
  lcd.setCursor(0,0); // Set the cursor to the beginning of the first line
  lcd.print("Hello"); // Typing text on the first line
  lcd.setCursor(0,1); // Setting the cursor to the beginning of the second line
  lcd.print("Boi"); // Typing on the second line
  delay(500);
  lcd.clear();
}

void loop() {
  delay(500); // Wait 50ms between pings (about 20 pings/sec). 29ms should be the shortest delay between pings.

  int distance = sonar.ping_cm(); // Send ping, get distance in cm and print result (0 = outside set distance range)

  Serial.print("Jarak: ");
  lcd.setCursor(0,0); // Set the cursor to the beginning of the first line
  lcd.print("Jarak : "); lcd.print(distance); lcd.print(" cm");// Typing text on the first line
  lcd.setCursor(0,1); // Setting the cursor to the beginning of the second line
  lcd.print("Suhu : "); lcd.print(mlx.readObjectTempC()+2); lcd.print(" C");
  Serial.print(distance); Serial.println("cm");
  Serial.print(mlx.readObjectTempC()+2); Serial.println(" C");
}
