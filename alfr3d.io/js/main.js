console.log("starting script");
var scene, camera, renderer;
var background_geometry, background_material, background_mesh;
var dot_geometry, dot_material, dot_mesh;                
var mouse, center;
var controls;

var alfr3d_blue = 0x33b5e5;
var alfr3d_orange = 0xFF8400;
var alfr3d_black = 0x071a21;
var alfr3d_dot = 0xFF194C;

// create 2D array grid*grid large
var grid = 48;
var dots = [];
for(var i=0; i<grid; i++){
    dots[i]=[];
}

init();
animate();

function init() {
    console.log("init");
    scene = new THREE.Scene();
    center = new THREE.Vector3();
    center.z = - 1000;
    var cust_step = window.innerWidth*0.05;      
    console.log("cust_step = "+cust_step);

    camera = new THREE.PerspectiveCamera( 30, window.innerWidth / window.innerHeight, 1, 10000 );
    camera.position.z = 1000;

    // button
    console.log("creating button");
    var dummy_button = document.createElement('button');
    var t = document.createTextNode("Littl3.1");
    dummy_button.className = 'dm_but';
    dummy_button.style.backgroundColor = alfr3d_blue;
    dummy_button.appendChild(t);
    dummy_button.addEventListener('click', function (event) {
        console.log("clicked");
        window.location.href = "http://littl31.com";
    }, false);
    var container = document.getElementById('container');
    container.appendChild(dummy_button);                    

    // gird
    dot_geometry = new THREE.SphereGeometry(6,32,32);
    dot_material = new THREE.MeshBasicMaterial({ color: alfr3d_blue, transparent: true, opacity: 0.3 , side:THREE.DoubleSide});              
    for(var i=0; i < grid; i++){
        for(var j=0; j < grid; j++){
            var stepx = (window.innerWidth/grid)*2;
            var stepy = (window.innerWidth/grid)*2;
            dots[i][j] = new THREE.Mesh(dot_geometry, dot_material);
            dots[i][j].position.set(((stepx*i)-window.innerWidth/2)*8,((stepy*j)-window.innerHeight/2)*8,-100*cust_step);
            scene.add(dots[i][j]);
        }
    }                

    // background window
    // test_bgd_geometry = new THREE.BoxGeometry(window.innerWidth/2,window.innerHeight/2, 1, 1, 1, 1);
    // test_bgd_material = new THREE.MeshBasicMaterial({ color: alfr3d_blue, transparent: true, opacity: 0.1 });
    // test_bgd_mesh = new THREE.Mesh(test_bgd_geometry,test_bgd_material);                
    // test_bgd_mesh.position.set(0,0,-100); 
    // scene.add(test_bgd_mesh);                   

    // testing custom geometry
    var cust_geo = new THREE.Geometry();                

    cust_geo.vertices.push(
        new THREE.Vector3(0*cust_step,0*cust_step,0),
        new THREE.Vector3(1*cust_step,1*cust_step,0),
        new THREE.Vector3(13*cust_step,1*cust_step,0),
        new THREE.Vector3(14*cust_step,2*cust_step,0),
        new THREE.Vector3(22*cust_step,2*cust_step,0),
        new THREE.Vector3(23*cust_step,1*cust_step,0),
        new THREE.Vector3(23*cust_step,-7*cust_step,0),
        new THREE.Vector3(22*cust_step,-8*cust_step,0),
        new THREE.Vector3(22*cust_step,-14*cust_step,0),
        new THREE.Vector3(21*cust_step,-15*cust_step,0),
        new THREE.Vector3(9*cust_step,-15*cust_step,0),
        new THREE.Vector3(8*cust_step,-16*cust_step,0),
        new THREE.Vector3(0*cust_step,-16*cust_step,0),
        new THREE.Vector3(-1*cust_step,-15*cust_step,0),
        new THREE.Vector3(-1*cust_step,-7*cust_step,0),
        new THREE.Vector3(0*cust_step,-6*cust_step,0)
    );

    // join the vertices above into triangles
    cust_geo.faces.push(new THREE.Face3(0,1,2));
    cust_geo.faces.push(new THREE.Face3(0,2,15));
    cust_geo.faces.push(new THREE.Face3(2,10,15));
    cust_geo.faces.push(new THREE.Face3(10,11,15));
    cust_geo.faces.push(new THREE.Face3(11,12,15));
    cust_geo.faces.push(new THREE.Face3(12,13,15));                
    cust_geo.faces.push(new THREE.Face3(13,14,15));
    cust_geo.faces.push(new THREE.Face3(2,3,4));
    cust_geo.faces.push(new THREE.Face3(2,4,5));
    cust_geo.faces.push(new THREE.Face3(2,5,6));
    cust_geo.faces.push(new THREE.Face3(2,6,7));
    cust_geo.faces.push(new THREE.Face3(2,7,10));
    cust_geo.faces.push(new THREE.Face3(7,8,9));
    cust_geo.faces.push(new THREE.Face3(7,9,10));

    // not sure what these do yet
    //cust_geo.computeBoundingSphere();
    //cust_geo.computeFaceNormals();

    cust_geo_mat = new THREE.MeshBasicMaterial({ color: alfr3d_black, 
                                                 transparent: true, 
                                                 opacity: 0.8, 
                                                 side:THREE.DoubleSide});
    geo_mesh = new THREE.Mesh(cust_geo,cust_geo_mat);
    geo_mesh.position.set(-window.innerWidth*0.5,window.innerHeight*0.5,-50*cust_step);
    geo_mesh.callback = function() { console.log("clicked 1"); }
    scene.add(geo_mesh); 

    var cust_geo_border = new THREE.EdgesGeometry(cust_geo);
    cust_geo_border_mat = new THREE.LineBasicMaterial( { color: alfr3d_blue, linewidth: 10});
    var cust_geo_frame = new THREE.LineSegments( cust_geo_border, cust_geo_border_mat);
    cust_geo_frame.position.set(-window.innerWidth*0.5,window.innerHeight*0.5,-50*cust_step);
    scene.add( cust_geo_frame );

    var cust_geo2 = new THREE.Geometry();

    cust_geo2.vertices.push(
        new THREE.Vector3(0*cust_step/5,0*cust_step/5,0),
        new THREE.Vector3(1*cust_step/5,1*cust_step/5,0),
        new THREE.Vector3(10*cust_step/5,1*cust_step/5,0),
        new THREE.Vector3(11*cust_step/5,0*cust_step/5,0),
        new THREE.Vector3(11*cust_step/5,-4*cust_step/5,0),
        new THREE.Vector3(10*cust_step/5,-5*cust_step/5,0),
        new THREE.Vector3(1*cust_step/5,-5*cust_step/5,0),
        new THREE.Vector3(0*cust_step/5,-4*cust_step/5,0)
    );

    // join the vertices above into triangles
    cust_geo2.faces.push(new THREE.Face3(0,1,2));
    cust_geo2.faces.push(new THREE.Face3(0,2,3));
    cust_geo2.faces.push(new THREE.Face3(0,3,4));
    cust_geo2.faces.push(new THREE.Face3(0,4,5));
    cust_geo2.faces.push(new THREE.Face3(0,5,6));
    cust_geo2.faces.push(new THREE.Face3(0,6,7));                

    cust_geo2_mat = new THREE.MeshBasicMaterial({ color: alfr3d_black, 
                                                  transparent: true, 
                                                  opacity: 0.8, 
                                                  side:THREE.DoubleSide});  
    cust_geo2_border_mat = new THREE.LineBasicMaterial({ color: alfr3d_blue, 
                                                         linewidth: 10});
    
    geo_mesh2 = new THREE.Mesh(cust_geo2,cust_geo2_mat);
    geo_mesh2.position.set(-window.innerWidth*0.5+100,window.innerHeight*0.5+20,-40*cust_step);
    geo_mesh2.callback = function() { console.log("clicked 2"); }
    var cust_geo2_border = new THREE.EdgesGeometry(cust_geo2);
    var cust_geo2_frame = new THREE.LineSegments(cust_geo2_border,cust_geo2_border_mat);
    cust_geo2_frame.position.set(-window.innerWidth*0.5+100,window.innerHeight*0.5+20,-40*cust_step);
    scene.add(geo_mesh2);
    scene.add(cust_geo2_frame);
    
    geo_mesh3 = new THREE.Mesh(cust_geo2,cust_geo2_mat);
    geo_mesh3.position.set(-window.innerWidth*0.5+220,window.innerHeight*0.5+20,-40*cust_step);
    geo_mesh3.callback = function() { console.log("clicked 3"); }
    var cust_geo3_border = new THREE.EdgesGeometry(cust_geo2);
    var cust_geo3_frame = new THREE.LineSegments(cust_geo3_border,cust_geo2_border_mat);
    cust_geo3_frame.position.set(-window.innerWidth*0.5+220,window.innerHeight*0.5+20,-40*cust_step);
    scene.add(geo_mesh3);    
    scene.add(cust_geo3_frame);

    geo_mesh4 = new THREE.Mesh(cust_geo2,cust_geo2_mat);
    geo_mesh4.position.set(-window.innerWidth*0.5+340,window.innerHeight*0.5+20,-40*cust_step);
    geo_mesh4.callback = function() { console.log("clicked 4"); }
    var cust_geo4_border = new THREE.EdgesGeometry(cust_geo2);
    var cust_geo4_frame = new THREE.LineSegments(cust_geo4_border,cust_geo2_border_mat);
    cust_geo4_frame.position.set(-window.innerWidth*0.5+340,window.innerHeight*0.5+20,-40*cust_step);
    scene.add(geo_mesh4);
    scene.add(cust_geo4_frame);

    geo_mesh5 = new THREE.Mesh(cust_geo2,cust_geo2_mat);
    geo_mesh5.position.set(-window.innerWidth*0.5+460,window.innerHeight*0.5+20,-40*cust_step);
    geo_mesh5.callback = function() { console.log("clicked 5"); }
    var cust_geo5_border = new THREE.EdgesGeometry(cust_geo2);
    var cust_geo5_frame = new THREE.LineSegments(cust_geo5_border,cust_geo2_border_mat);
    cust_geo5_frame.position.set(-window.innerWidth*0.5+460,window.innerHeight*0.5+20,-40*cust_step);
    scene.add(geo_mesh5);
    scene.add(cust_geo5_frame);

    // text play
    var label1 = makeTextSprite("status");
    label1.position.set(-window.innerWidth*0.5+520,window.innerHeight*0.5,-39*cust_step);
    scene.add(label1);


    renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setClearColor(0xffffff, 0);

    document.body.appendChild( renderer.domElement );

    // Trackball controlls: Zoom
    controls = new THREE.TrackballControls( camera );
    controls.noRotate = true;
    controls.zoomSpeed = 0.8;
    controls.minDistance = 500;
    controls.maxDistance = 2000;
    controls.addEventListener( 'change', render );      

    raycaster = new THREE.Raycaster();              
    mouse = new THREE.Vector3( 0, 0, 1 );

    document.addEventListener( 'mousemove', onDocumentMouseMove, false );
    document.addEventListener( 'mousedown', onDocumentMouseDown, false);
    window.addEventListener( 'resize', onWindowResize, false );

}

function onDocumentMouseMove( event ) {
    mouse.x = ( event.clientX - window.innerWidth / 2 ) * 0.5;
    mouse.y = ( event.clientY - window.innerHeight / 2 ) * 0.5;
}                

function animate() {
    requestAnimationFrame( animate );
    controls.update();

    camera.position.x += ( - mouse.x - camera.position.x ) * 0.05;
    camera.position.y += (  mouse.y - camera.position.y ) * 0.05;
    camera.lookAt( center );

    render()
}

function onDocumentMouseDown( event ) {

    console.log("mouse clicked");
    event.preventDefault();

    mouse.x = ( event.clientX / renderer.domElement.clientWidth ) * 2 - 1;
    mouse.y = - ( event.clientY / renderer.domElement.clientHeight ) * 2 + 1;

    raycaster.setFromCamera( mouse, camera );

    var intersects = raycaster.intersectObjects( scene.children ); 

    if ( intersects.length > 0 ) {

        intersects[0].object.callback();

    }

}            

function render() {
    renderer.render( scene, camera );
}                

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

    render();
}

function makeTextSprite( message, parameters )
{
    if ( parameters === undefined ) parameters = {};
    var fontface = parameters.hasOwnProperty("fontface") ? parameters["fontface"] : "Arial";
    var fontsize = parameters.hasOwnProperty("fontsize") ? parameters["fontsize"] : 120;
    var borderThickness = parameters.hasOwnProperty("borderThickness") ? parameters["borderThickness"] : 4;
    var borderColor = parameters.hasOwnProperty("borderColor") ?parameters["borderColor"] : { r:0, g:0, b:0, a:1.0 };
    var backgroundColor = parameters.hasOwnProperty("backgroundColor") ?parameters["backgroundColor"] : { r:255, g:255, b:255, a:1.0 };
    var textColor = parameters.hasOwnProperty("textColor") ?parameters["textColor"] : { r:255, g:255, b:255, a:1.0 };

    var canvas = document.createElement('canvas');
    canvas.width = 500;
    canvas.heaight = 100;
    var context = canvas.getContext('2d');
    context.font = "Bold " + fontsize + "px " + fontface;
    var metrics = context.measureText( message );
    var textWidth = metrics.width;

    context.fillStyle   = "rgba(" + backgroundColor.r + "," + backgroundColor.g + "," + backgroundColor.b + "," + backgroundColor.a + ")";
    context.strokeStyle = "rgba(" + borderColor.r + "," + borderColor.g + "," + borderColor.b + "," + borderColor.a + ")";

    context.lineWidth = borderThickness;
    //roundRect(context, borderThickness/2, borderThickness/2, (textWidth + borderThickness) * 1.1, fontsize * 1.4 + borderThickness, 8);

    context.fillStyle = "rgba("+textColor.r+", "+textColor.g+", "+textColor.b+", 1.0)";
    context.fillText( message, borderThickness, fontsize + borderThickness);

    var texture = new THREE.Texture(canvas) 
    texture.needsUpdate = true;

    var spriteMaterial = new THREE.SpriteMaterial( { map: texture, useScreenCoordinates: false } );
    var sprite = new THREE.Sprite( spriteMaterial );
    //sprite.scale.set(0.5 * fontsize, 0.25 * fontsize, 0.75 * fontsize);
    sprite.scale.set(100, 50, 1);
    return sprite;  
}