from math import pi, sin, cos
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, GeomTriangles, GeomNode

SR2 = 2**.5
NUM_ROWS = 10

class Rhomdo(GeomNode):
    def __init__(self,x,y,z):
        super(Rhomdo,self).__init__("rhomdo")
        
        format = GeomVertexFormat.getV3c4() 
        vdata = GeomVertexData("vertices", format, Geom.UHStatic) 
        vdata.setNumRows(14)

        vertexWriter = GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")

        for i in range(14):            
            colorWriter.addData4f((x/NUM_ROWS),(y/NUM_ROWS),(z/NUM_ROWS),1)

        if z%2 == 1:
            x += .5
            y += .5
        
        vertexWriter.addData3f((2*x),   (2*y),   SR2*(z+1))
        
        vertexWriter.addData3f((2*x)-1, (2*y),   SR2*(z+.5))
        vertexWriter.addData3f((2*x),   (2*y)-1, SR2*(z+.5))
        vertexWriter.addData3f((2*x)+1, (2*y),   SR2*(z+.5))
        vertexWriter.addData3f((2*x),   (2*y)+1, SR2*(z+.5))

        vertexWriter.addData3f((2*x)-1, (2*y)-1, SR2*(z))
        vertexWriter.addData3f((2*x)+1, (2*y)-1, SR2*(z))
        vertexWriter.addData3f((2*x)+1, (2*y)+1, SR2*(z))
        vertexWriter.addData3f((2*x)-1, (2*y)+1, SR2*(z))
        
        vertexWriter.addData3f((2*x)-1, (2*y),   SR2*(z-.5))
        vertexWriter.addData3f((2*x),   (2*y)-1, SR2*(z-.5))
        vertexWriter.addData3f((2*x)+1, (2*y),   SR2*(z-.5))
        vertexWriter.addData3f((2*x),   (2*y)+1, SR2*(z-.5))
        
        vertexWriter.addData3f((2*x),   (2*y),   SR2*(z-1))
        
        #step 2) make primitives and assign vertices to them 
        tris=GeomTriangles(Geom.UHStatic) 

        #top
        tris.addVertex(0) 
        tris.addVertex(1) 
        tris.addVertex(2) 
        tris.closePrimitive()
        tris.addVertex(0) 
        tris.addVertex(2) 
        tris.addVertex(3) 
        tris.closePrimitive()
        tris.addVertex(0) 
        tris.addVertex(3) 
        tris.addVertex(4) 
        tris.closePrimitive()
        tris.addVertex(0) 
        tris.addVertex(4) 
        tris.addVertex(1)
        tris.closePrimitive()
        
        tris.addVertex(1) 
        tris.addVertex(5) 
        tris.addVertex(2) 
        tris.closePrimitive()
        tris.addVertex(2) 
        tris.addVertex(6) 
        tris.addVertex(3) 
        tris.closePrimitive()
        tris.addVertex(3) 
        tris.addVertex(7) 
        tris.addVertex(4) 
        tris.closePrimitive()
        tris.addVertex(4) 
        tris.addVertex(8) 
        tris.addVertex(1) 
        tris.closePrimitive()

        #middle
        tris.addVertex(1)
        tris.addVertex(8) 
        tris.addVertex(9) 
        tris.closePrimitive()
        tris.addVertex(1) 
        tris.addVertex(9) 
        tris.addVertex(5) 
        tris.closePrimitive() 
        tris.addVertex(2) 
        tris.addVertex(5) 
        tris.addVertex(10) 
        tris.closePrimitive()  
        tris.addVertex(2) 
        tris.addVertex(10) 
        tris.addVertex(6) 
        tris.closePrimitive()
        tris.addVertex(3) 
        tris.addVertex(6) 
        tris.addVertex(11) 
        tris.closePrimitive()  
        tris.addVertex(3) 
        tris.addVertex(11) 
        tris.addVertex(7) 
        tris.closePrimitive()  
        tris.addVertex(4) 
        tris.addVertex(7) 
        tris.addVertex(12) 
        tris.closePrimitive()  
        tris.addVertex(4) 
        tris.addVertex(12) 
        tris.addVertex(8) 
        tris.closePrimitive()

        #bottom
        tris.addVertex(5) 
        tris.addVertex(9) 
        tris.addVertex(10) 
        tris.closePrimitive()
        tris.addVertex(6) 
        tris.addVertex(10) 
        tris.addVertex(11) 
        tris.closePrimitive()
        tris.addVertex(7) 
        tris.addVertex(11) 
        tris.addVertex(12) 
        tris.closePrimitive()
        tris.addVertex(8) 
        tris.addVertex(12) 
        tris.addVertex(9) 
        tris.closePrimitive()
        
        tris.addVertex(9) 
        tris.addVertex(13) 
        tris.addVertex(10) 
        tris.closePrimitive()
        tris.addVertex(10) 
        tris.addVertex(13) 
        tris.addVertex(11) 
        tris.closePrimitive()
        tris.addVertex(11) 
        tris.addVertex(13) 
        tris.addVertex(12) 
        tris.closePrimitive()
        tris.addVertex(12) 
        tris.addVertex(13) 
        tris.addVertex(9) 
        tris.closePrimitive()

        #step 3) make a Geom object to hold the primitives 
        cubeGeom=Geom(vdata) 
        cubeGeom.addPrimitive(tris)
        print(cubeGeom)
        #now put squareGeom in a GeomNode. You can now position your geometry in the scene graph. 
        self.addGeom(cubeGeom) 

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        for x in range(NUM_ROWS):
            for y in range(NUM_ROWS):
                for z in range(NUM_ROWS):
                    render.attachNewNode(Rhomdo(x,y,z))

        plight = PointLight('plight')
        plight.setColor(VBase4(1, 1, 1, 1))
        plight.setAttenuation((0,0,.001))
        self.plnp = render.attachNewNode(plight)
        self.plnp.setPos(NUM_ROWS,NUM_ROWS,(NUM_ROWS*SR2)+40)
        render.setLight(self.plnp)
 
        # Disable the camera trackball controls.
        #self.disableMouse()
 
        # Load the environment model.
        #self.scene = NodePath()
        # Reparent the model to render.
        #self.scene.reparentTo(self.render)
        #self.scene.setPos(-8, 42, 0)
        #self.scene.setColor(.9,.4,.7,1)
 
        # Add the spinCameraTask procedure to the task manager.
        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")

        
        self.camera.setPos(-(NUM_ROWS), -(NUM_ROWS), 0)
        self.camera.setHpr(0, 0, 0)
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(30 * sin(angleRadians), -30.0 * cos(angleRadians), 20)
        self.camera.setHpr(angleDegrees, -30, 0)
        return Task.cont
 
app = MyApp()
app.run()
