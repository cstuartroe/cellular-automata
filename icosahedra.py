from math import pi, sin, cos, log2
import random
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, GeomTriangles, GeomNode

SR2 = 2**.5
NUM_ROWS = 20
HALFLIFE = 100

class Rhomdo(NodePath):
    def __init__(self,x,y,z,array):
        self.geomnode = GeomNode("rhomdo")
        super(Rhomdo,self).__init__(self.geomnode)
        self.x, self.y, self.z = x,y,z
        self.id = x*(NUM_ROWS**2) + y*NUM_ROWS + z
        self.array = array
        self.color = (x/NUM_ROWS),(y/NUM_ROWS),(z/NUM_ROWS),1
        self.lifespan = -HALFLIFE*log2(1-random.random())
        self.hidden = False
        
        format = GeomVertexFormat.getV3c4() 
        vdata = GeomVertexData("vertices", format, Geom.UHStatic) 
        vdata.setNumRows(14)

        vertexWriter = GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")

        for i in range(14):            
            colorWriter.addData4f(*self.color)

        realX = self.x*2 - NUM_ROWS
        realY = self.y*2 - NUM_ROWS
        realZ = self.z*SR2 - SR2*.5*NUM_ROWS
        if self.z%2 == 1:
            realX += .5
            realY += .5
        
        vertexWriter.addData3f(realX,   realY,   realZ+SR2)
        
        vertexWriter.addData3f(realX-1, realY,   realZ+(SR2/2))
        vertexWriter.addData3f(realX,   realY-1, realZ+(SR2/2))
        vertexWriter.addData3f(realX+1, realY,   realZ+(SR2/2))
        vertexWriter.addData3f(realX,   realY+1, realZ+(SR2/2))

        vertexWriter.addData3f(realX-1, realY-1, realZ)
        vertexWriter.addData3f(realX+1, realY-1, realZ)
        vertexWriter.addData3f(realX+1, realY+1, realZ)
        vertexWriter.addData3f(realX-1, realY+1, realZ)
        
        vertexWriter.addData3f(realX-1, realY,   realZ-(SR2/2))
        vertexWriter.addData3f(realX,   realY-1, realZ-(SR2/2))
        vertexWriter.addData3f(realX+1, realY,   realZ-(SR2/2))
        vertexWriter.addData3f(realX,   realY+1, realZ-(SR2/2))
        
        vertexWriter.addData3f(realX,   realY,   realZ-SR2)
        
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
        rhomGeom=Geom(vdata) 
        rhomGeom.addPrimitive(tris)
        #now put squareGeom in a GeomNode. You can now position your geometry in the scene graph. 
        self.geomnode.addGeom(rhomGeom)

    def update(self,time):
        if time > self.lifespan and not self.hidden:
            self.hide()
            self.hidden = True

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.rhomdos = []

        for x in range(NUM_ROWS):
            rhomdosY = []
            for y in range(NUM_ROWS):
                rhomdosZ = []
                for z in range(NUM_ROWS):
                    rhomdo = Rhomdo(x,y,z,self.rhomdos)
                    render.attachNewNode(rhomdo.geomnode)
                    rhomdosZ.append(rhomdo)
                rhomdosY.append(rhomdosZ)
            self.rhomdos.append(rhomdosY)

        print("Rhomdos loaded.")

        plight = PointLight('plight')
        plight.setColor(VBase4(1, 1, 1, 1))
        plight.setAttenuation((0,0,.0005))
        self.plnp = render.attachNewNode(plight)
        self.plnp.setPos(0,0,(NUM_ROWS*SR2)+40)
        render.setLight(self.plnp)
 
        # Disable the camera trackball controls.
        self.disableMouse()
 
        # Load the environment model.
        #self.scene = NodePath()
        # Reparent the model to render.
        #self.scene.reparentTo(self.render)
        #self.scene.setPos(-8, 42, 0)
        #self.scene.setColor(.9,.4,.7,1)
 
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.updateClock, "UpdateClock")
        self.clock = 0
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(100 * sin(angleRadians), -100.0 * cos(angleRadians), 50)
        self.camera.setHpr(angleDegrees, -30, 0)
        return Task.cont

    def updateRhomdos(self):
        for x in range(NUM_ROWS):
            for y in range(NUM_ROWS):
                for z in range(NUM_ROWS):
                    #print(self.rhomdos[x][y][z].id)
                    self.rhomdos[x][y][z].update(self.clock)
        return Task.cont

    def updateClock(self, task):
        adjusted_time = task.time * 20
        if round(adjusted_time) > self.clock:
            self.clock = round(adjusted_time)
            print(self.clock)
            self.updateRhomdos()
        return Task.cont
 
app = MyApp()
app.run()
