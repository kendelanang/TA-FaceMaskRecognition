#include <NewPing.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
#include <Adafruit_MLX90614.h>
#include <Servo.h>

#define TRIGGER_PIN  9
#define ECHO_PIN     10
#define MAX_DISTANCE 99

LiquidCrystal_I2C lcd(0x27,16,2);
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
Servo myservo;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

boolean simpan = false;
int pos = 90;

void setup() {
  Serial.begin(9600);
  myservo.attach(11);
  mlx.begin();
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print(" SELAMAT DATANG ");
  lcd.setCursor(0,1);
  lcd.print("________________");
  delay(5000);
  lcd.clear();
}

void loop() {
  delay(500);
  int distance = sonar.ping_cm();

  if (distance == 0 || distance>=30){ diam(); }

  if (distance >= 1 && distance <= 20){ ceksuhu(); }
}

void diam(){
  lcd.setCursor(0,0);
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
  lcd.setCursor(0,0);
  lcd.print(" TUNGGU SEBENTAR");
  lcd.setCursor(0,1);
  lcd.print(" SEDANG CEK SUHU");
  delay(3000);
  
  if (suhucek <= 37){
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("SUHU : "); lcd.print(suhucek); lcd.print(" "); lcd.print((char)223); lcd.print("C");
    lcd.setCursor(0,1);
    lcd.print("SUHU ANDA NORMAL");
    delay(3000);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("SILAHKAN MUNDUR");
    lcd.setCursor(0,1);
    lcd.print("UNTUK SCAN WAJAH");
    delay(3000);
    scanwajah();
  }
  else {
    lcd.clear();
    lcd.setCursor(0,0); // Setting the cursor to the beginning of the second line
    lcd.print("SUHU : "); lcd.print(suhucek); lcd.print(" C");
    lcd.setCursor(0,1);
    lcd.print("SUHU TIDAK NORMAL");
    delay(3000);
  }

}

void scanwajah(){
  Serial.write("cekwajah");
  delay(1000);
  if (Serial.available()>0 && simpan == false){
    String x = Serial.readStringUntil('>');
    if (x != "No Mask"){
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("SILAHKAN MASUK"); 
      lcd.setCursor(0,1); 
      lcd.print(x);
      simpan = true;
      Serial.flush();
      bukapintu();
      delay(5000);
    }
    else{
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print(" TOLONG GUNAKAN"); 
      lcd.setCursor(0,1); 
      lcd.print("MASKER DGN BENAR");
      simpan = false;
      Serial.flush();
      delay(5000);
      diam();
    }
  }
}

void bukapintu(){
  delay(1000);
  myservo.write(0);
  delay(5000);
  myservo.write(90);
}
