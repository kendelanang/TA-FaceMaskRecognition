#include <NewPing.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <Adafruit_MLX90614.h>
#include <Servo.h>

#define TRIGGER_PIN  9
#define ECHO_PIN     10
#define MAX_DISTANCE 99 // Maximum distance we want to measure (in centimeters).

LiquidCrystal_I2C lcd(0x27,16,2);
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo myservo;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

boolean simpan = false;
int pos = 0;

void setup() {
  Serial.begin(9600);
  myservo.attach(11);
  mlx.begin();
  lcd.begin(); // Initialize display  
  lcd.backlight(); // connecting backlight
  lcd.setCursor(0,0); // Set the cursor to the beginning of the first line
  lcd.print(" SELAMAT DATANG ");
  lcd.setCursor(0,1); // Setting the cursor to the beginning of the second line
  lcd.print("DI SALTY SPITON."); // Typing on the second line
  delay(5000);
  lcd.clear();
}

void loop() {
  delay(500); // Wait 50ms between pings (about 20 pings/sec). 29ms should be the shortest delay between pings.
  int distance = sonar.ping_cm(); // Send ping, get distance in cm and print result (0 = outside set distance range)

  if (distance == 0 || distance>=30){
    diam();
  }

  if (distance >= 1 && distance <= 20){
    ceksuhu();
  }
  
//  Serial.print("Jarak: ");
//  lcd.setCursor(0,0); // Set the cursor to the beginning of the first line
//  lcd.print("Jarak : "); lcd.print(distance); lcd.print(" cm");// Typing text on the first line
//  lcd.setCursor(0,1); // Setting the cursor to the beginning of the second line
//  lcd.print("Suhu : "); lcd.print(mlx.readObjectTempC()); lcd.print(" C");
//  Serial.print(distance); Serial.println("cm");

  //Serial.println(x);

}

void diam(){
  lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
  lcd.print("_______________________________________");
  lcd.setCursor(0,1);
  lcd.print("DEKATKAN WAJAH ANDA UNTUK CEK SUHU.....");
  lcd.scrollDisplayLeft();
  delay(100);
  simpan = false;
}

void ceksuhu(){
  float suhucek = mlx.readObjectTempC()+1;
  lcd.clear();
  lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
  lcd.print(" TUNGGU SEBENTAR");
  lcd.setCursor(0,1);
  lcd.print(" SEDANG CEK SUHU");
  delay(3000);
  
  if (suhucek <= 37){
    lcd.clear();
    lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
    lcd.print("SUHU ANDA : "); lcd.print(suhucek); lcd.print(" C");
    lcd.setCursor(0,1);
    lcd.print("SUHU NORMAL");
    delay(3000);
    scanwajah();
    bukapintu();
  }
  else {
    lcd.clear();
    lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
    lcd.print("SUHU ANDA : "); lcd.print(suhucek); lcd.print(" C");
    lcd.setCursor(0,1);
    lcd.print("SUHU TIDAK NORMAL");
    delay(3000);
  }

}

void scanwajah(){
  if (Serial.available()>0 && simpan == false){
    String x = Serial.readStringUntil('.');
    lcd.clear();
    lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
    lcd.print("SILAHKAN MASUK"); 
    lcd.setCursor(0,1); 
    lcd.print(x);
    simpan = true;
    
    delay(5000);
  }
}

void bukapintu(){
  delay(1000);
  myservo.write(90);
  delay(5000);
  myservo.write(0);
  
}
