# Digital Twins in Action

## Appendix B - Building a custom IoT Sensor - code samples

In this repository you will find the code sample from Appendix B of Digital Twins in Action where you learn how to build a custom IoT sensor using off the shelf hardware. The required hardware and software are described in the Appendix, and the following file can be updated with your configuration before uploading it to the ESP32.

[appendixb_code01_biegel.ino](appendixb_code01_biegel.ino)

- WIFI_SSID - your WiFi SSID
- WIFI_PASSWORD - your WiFi password
- AWS_IOT_ENDPOINT[] - your AWS IoT core endpoint
- AWS_CERT_CA - the CA cert you got when you created your Thing in AWS
- AWS_CERT_CRT - the cert you got when you created your Thing in AWS
- AWS_CERT_PRIVATE - the private key you got when you created your Thing in AWS