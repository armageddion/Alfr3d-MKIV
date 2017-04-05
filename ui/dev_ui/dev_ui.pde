import processing.opengl.*;

import controlP5.*;

ControlP5 cp5;

int alfr3d_blue = color(26, 157, 255);

int slider = 0;

Textarea online_users;

void setup()
{
    size(800, 480, OPENGL);
    smooth();

    cp5 = new ControlP5(this);

   Button bt_who = cp5.addButton("WHO")
     .setPosition(700,430)
     .setSize(40,40)
     ;   

   bt_who.addCallback(new CallbackListener() {
      public void controlEvent(CallbackEvent theEvent) {
         switch(theEvent.getAction()) {
           case(ControlP5.ACTION_PRESSED): println("start"); break;
           case(ControlP5.ACTION_RELEASED): println("stop"); break;
         }
      }
   });


   Button bt_exit = cp5.addButton("Exit")
     .setPosition(750,430)
     .setSize(40,40)
     ;        

   //button callbacks
   bt_exit.addCallback(new CallbackListener() {
      public void controlEvent(CallbackEvent theEvent) {
         switch(theEvent.getAction()) {
           case(ControlP5.ACTION_PRESSED): exit();
           case(ControlP5.ACTION_RELEASED): break;
         }
      }
   });     

   cp5.addSlider("slider")
     .setPosition(20,50)
     .setSize(20,200)
     .setRange(0,255)
     .setLabelVisible(false)
     ;     

   cp5.addSlider("slider2")
     .setPosition(50,50)
     .setSize(20,200)
     .setRange(0,255)
     ;

   online_users = cp5.addTextarea("txt")
                  .setPosition(750,20)
                  .setSize(45,50)
                  .setFont(createFont("Courier 10 Pitch",48))
                  .setColor(alfr3d_blue)
                  .setLineHeight(10)
                  .setColorBackground(color(255,100))
                  .setColorForeground(color(255,100));
                  ;    

   online_users.setText("0");
}

void draw()
{
   background(20);

   cp5.getController("slider2").setValue(slider);

}

public void controlEvent(ControlEvent theEvent) {
   //println(theEvent.getController().getName());
}

public void WHO(){
   String [] response = loadStrings("http://10.0.0.69:8080/whosthere");
   println (response);
   println (response[0].substring(13,15));      //number of users 
   online_users.setText(response[0].substring(13,15));
   for (int i = 1; i < response.length; i++) {
      println(response[i]);                     // names of online users
   }
}

// called every time a keyboard key is pressed
void keyPressed() {
   if (key == ESC) {
      exit();
   }
}