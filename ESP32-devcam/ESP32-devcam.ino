#include "OV2640.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>

#include "OV2640Streamer.h"
#include "CRtspSession.h"
#define USEBOARD_AITHINKER

OV2640 cam;
WebServer server(80);
WiFiServer rtspServer(9001);

#include "wifikeys.h"

void handle_jpg_stream(void)
{
    WiFiClient client = server.client();
    String response = "HTTP/1.1 200 OK\r\n";
    response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
    server.sendContent(response);

    while (1)
    {
        cam.run();
        if (!client.connected())
            break;
        response = "--frame\r\n";
        response += "Content-Type: image/jpeg\r\n\r\n";
        server.sendContent(response);

        client.write((char *)cam.getfb(), cam.getSize());
        server.sendContent("\r\n");
        if (!client.connected())
            break;
    }
}



void setup()
{

    Serial.begin(115200);
    while (!Serial)
    {
        Serial.println('Waiting for Serial');
        delay(1000);
    }
    cam.init(esp32cam_config);

    IPAddress ip;

    WiFi.mode(WIFI_STA);
    WiFi.begin("OnePlus7Pro", "passpass");
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(F("."));
    }
    ip = WiFi.localIP();
    Serial.println(F("WiFi connected"));
    Serial.println("");
    Serial.println(ip);


    server.on("/", HTTP_GET, handle_jpg_stream);
    server.begin();

    rtspServer.begin();
}

CStreamer *streamer;
CRtspSession *session;
WiFiClient client; 

void loop()
{
    server.handleClient();
    uint32_t msecPerFrame = 100;
    static uint32_t lastimage = millis();

    
    
    // Copied this part of code
    if(session) {
        session->handleRequests(0); 

        uint32_t now = millis();
        if(now > lastimage + msecPerFrame || now < lastimage) {
            session->broadcastCurrentFrame(now);
            lastimage = now;

            // check  max frame rate
            now = millis();
            if(now > lastimage + msecPerFrame)
                printf("warning max frame rate of %d ms\n", now - lastimage);
        }

        if(session->m_stopped) {
            delete session;
            delete streamer;
            session = NULL;
            streamer = NULL;
        }
    }
    else {
        client = rtspServer.accept();

        if(client) {
            streamer = new OV2640Streamer(&client, cam);  

            session = new CRtspSession(&client, streamer);
        }
    }
}
