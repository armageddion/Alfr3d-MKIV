import processing.opengl.*;

boolean keyPress1 = false;
boolean keyPress2 = false;
boolean keyPress3 = false;
boolean keyPress4 = false;

void setup()
{
   size(800, 480, OPENGL);
   smooth();
}

void draw()
{
   background(51);
   lights();
   //noStroke();

   translate(width/2, height/2);


   noFill();
   stroke(26, 157, 255);
   strokeWeight(1);

   // SPHERE
   pushMatrix();
   //rotateX(radians(frameCount*2));
   rotateY(radians(frameCount));
   //rotateZ(radians(frameCount*2));
   sphereDetail(20);
   sphere(100);
   popMatrix();

   // ROTATING JUBLE #1
   strokeWeight(15);
   pushMatrix();
   rotateZ(radians(frameCount/2));
   arc(
      0,0,
      225,225,
      PI/4,PI/2-PI/100
   );
   strokeWeight(1);
   arc(
      0,0,
      210,210,
      PI/4-PI/100,PI/2
   );   
   line(0,105,0,120);
   popMatrix();

   // ROTATING JUMBLE #2   
   pushMatrix();
   rotateZ(-radians(frameCount));
   strokeWeight(10);
   arc(
      0,0,
      255,255,
      0+PI/50,PI/2
   );
   strokeWeight(1);
   arc(
      0,0,
      245,245,
      0,PI/2
   );
   strokeWeight(10);
   line(90,90,100,100);
   popMatrix();   

   // ROTATING JUMBLE #3
   pushMatrix();
   rotateZ(-radians(frameCount/3));
   strokeWeight(75);
   stroke(26, 157, 255,60);
   arc(
      0,0,
      200,200,
      0,PI/4
   );
   strokeWeight(1);
   line(137,0,142,0);
   arc(
      0,0,
      285,285,
      0,PI/4

   );
   popMatrix();      

   if (keyPress1 == true)
   {
      strokeWeight(15);
      stroke(26, 157, 255);
      arc(
         0,0,
         700,700,
         0,PI/4
      );      
      strokeWeight(5);
      line(100,100,250,250);
   }

   if (keyPress2 == true)
   {
      strokeWeight(15);
      stroke(26, 157, 255);
      arc(
         0,0,
         500,500,
         PI/2+PI/4,PI
      );      
      strokeWeight(1);
      line(-150,7,-257,7);      
      strokeWeight(5);
      line(-150,0,-257,0);
      line(-172,172,-230,230);
   }
   
   if (keyPress3 == true)
   {
      strokeWeight(15);
      stroke(26, 157, 255);
      arc(
         0,0,
         650,650,
         PI+PI/8,PI+PI/3
      );      
      strokeWeight(5);
      line(-75,-130,-165,-286);
   }   

   if (keyPress4 == true)
   {
      strokeWeight(15);
      stroke(26, 157, 255);
      arc(
         0,0,
         450,450,
         3*PI/2,2*PI
      );
      strokeWeight(1);
      arc(
         0,0,
         425,425,
         3*PI/2,7*PI/4
      );      
      strokeWeight(5);
      line(110,-110,160,-160);
      line(217,0,320,0);
   }
}

void keyPressed()
{
   if(key=='1')
   {
      if (keyPress1 == true)
      {
         keyPress1 = false;
         return;
      }
      else 
      {
         keyPress1 = true;
         return;
      }
   }
   if(key=='2')
   {
      if (keyPress2 == true)
      {
         keyPress2 = false;
         return;
      }
      else 
      {
         keyPress2 = true;
         return;
      }
   }
   if(key=='3')
   {
      if (keyPress3 == true)
      {
         keyPress3 = false;
         return;
      }
      else 
      {
         keyPress3 = true;
         return;
      }
   }
   if(key=='4')
   {
      if (keyPress4 == true)
      {
         keyPress4 = false;
         return;
      }
      else 
      {
         keyPress4 = true;
         return;
      }
   }            
}