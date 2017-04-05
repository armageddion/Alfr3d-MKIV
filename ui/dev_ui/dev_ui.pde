import processing.opengl.*;

import controlP5.*;

ControlP5 cp5;

int alfr3d_blue = color(26, 157, 255);

int slider = 0;

void setup()
{
   size(800, 480, OPENGL);
   smooth();

   cp5 = new ControlP5(this);

  Button BT1 = cp5.addButton("BT1")
     .setPosition(700,430)
     .setSize(40,40)
     ;   

   BT1.addCallback(new CallbackListener() {
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

   bt_exit.addCallback(new CallbackListener() {
      public void controlEvent(CallbackEvent theEvent) {
         switch(theEvent.getAction()) {
           case(ControlP5.ACTION_PRESSED): println("start"); exit();
           case(ControlP5.ACTION_RELEASED): println("stop"); break;
         }
      }
   });     

  // cp5.addSlider("slider")
  //    .setPosition(20,50)
  //    .setSize(20,200)
  //    .setRange(0,255)
  //    .setLabelVisible(false)
  //    ;     

  // cp5.addSlider("slider2")
  //    .setPosition(50,50)
  //    .setSize(20,200)
  //    .setRange(0,255)
  //    ;          
}

void draw()
{
   background(20);

   //cp5.getController("slider2").setValue(slider);

}

public void controlEvent(ControlEvent theEvent) {
   println(theEvent.getController().getName());
}

public void BT1(){
   String [] response = loadStrings("http://10.0.0.69:8080/morningAlarm");
}

// called every time a keyboard key is pressed
void keyPressed() {
  if (key == ESC) {
    exit();
  }
}