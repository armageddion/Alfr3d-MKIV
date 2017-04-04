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

  // create a new button with name 'buttonA'
  cp5.addButton("Exit")
     .setValue(0)
     .setPosition(750,430)
     .setSize(40,40)
     ;   

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
}

void draw()
{
   background(20);

   cp5.getController("slider2").setValue(slider);

}

public void controlEvent(ControlEvent theEvent) {
  println(theEvent.getController().getName());
}

public void Exit(){
   String [] response = loadStrings("http://10.0.0.69:8080/morningAlarm");
}