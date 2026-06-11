 #define USER_SETUP_INFO "User_Setup"
 #define ST7735_DRIVER
 #define ST7735_GREENTAB160x80
 #define TFT_RGB_ORDER TFT_BGR
 #define TFT_WIDTH 80
 #define TFT_HEIGHT 160
 #define TFT_MISO 5
 #define TFT_MOSI 1
 #define TFT_SCLK 0
 #define TFT_CS 4 // Chip select control pin
 #define TFT_DC 3 // Data Command control pin
 #define TFT_RST 2 // Reset pin (could connect to RST pin)
 #define TOUCH_CS -1 // Chip select pin (T_CS) of touch screen
 #define LOAD_GLCD // Font 1. Original Adafruit 8 pixel font needs ~1820 bytes in FLASH
 #define LOAD_FONT2 // Font 2. Small 16 pixel high font, needs ~3534 bytes in FLASH, 96 characters
 #define LOAD_FONT4 // Font 4. Medium 26 pixel high font, needs ~5848 bytes in FLASH, 96 characters
 #define LOAD_FONT6 // Font 6. Large 48 pixel font, needs ~2666 bytes in FLASH, only characters 1234567890:-.apm
 #define LOAD_FONT7 // Font 7. 7 segment 48 pixel font, needs ~2438 bytes in FLASH, only characters 1234567890:-.
 #define LOAD_FONT8 // Font 8. Large 75 pixel font needs ~3256 bytes in FLASH, only characters 1234567890:-.
 #define LOAD_GFXFF // FreeFonts. Include access to the 48 Adafruit_GFX free fonts FF1 to FF48 and custom fonts
#define SPI_FREQUENCY 20000000