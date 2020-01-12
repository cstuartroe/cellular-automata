from math import pi, sin, cos, log2
import random
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, GeomTriangles, GeomNode

SR2 = 2**.5
NUM_ROWS = 20
#HALFLIFE = 100
START_DENSITY_TEST = .1
SURVIVAL_RULES_TEST = {0: False, 1: False, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}
BIRTH_RULES_TEST = {0: False, 1: False, 2: False, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False, 9: False, 10: False, 11: False, 12: False}

class Rhomdo(NodePath):
    def __init__(self,x,y,z,array):
        self.geomnode = GeomNode("rhomdo")
        super(Rhomdo,self).__init__(self.geomnode)
        self.x, self.y, self.z = x,y,z
        self.odd = self.z%2 == 1
        self.id = x*(NUM_ROWS**2) + y*NUM_ROWS + z
        self.array = array
        self.color = (x/NUM_ROWS),(y/NUM_ROWS),(z/NUM_ROWS),1
        self.lifespan = -HALFLIFE*log2(1-random.random())
        self.scheduled_alive = True

        if random.random() < START_DENSITY:
            self.be_born()
        else:
            self.die()
        
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
        if self.odd:
            realX += 1
            realY += 1
        
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

    def determine_life(self):
        if self.alive:
            self.scheduled_alive = SURVIVAL_RULES[self.adjacent_alive()]
        else:
            self.scheduled_alive = BIRTH_RULES[self.adjacent_alive()]

    def enact_life(self):
        if self.scheduled_alive and not self.alive:
            self.be_born()
        elif not self.scheduled_alive and self.alive:
            self.die()

    def die(self):
        self.hide()
        self.alive = False

    def be_born(self):
        self.show()
        self.alive = True

    def adjacent_alive(self):
        if self.odd:
            adjacents = [(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1),(0,0,-1),(1,0,-1),(0,1,-1),(1,1,-1)]
        else:
            adjacents = [(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(0,0,1),(-1,0,1),(0,-1,1),(-1,-1,1),(0,0,-1),(-1,0,-1),(0,-1,-1),(-1,-1,-1)]

        result = 0
        for adjacent in adjacents:
            adjX, adjY, adjZ = (self.x+adjacent[0]),(self.y+adjacent[1]),(self.z+adjacent[2])
            if not (-1 in (adjX,adjY,adjZ)) and not (NUM_ROWS in (adjX,adjY,adjZ)):
                result += (1 if self.array[adjX][adjY][adjZ].alive else 0)
        return result

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self,_survival_rules,_birth_rules,_start_density)
        self.SURVIVAL_RULES = _SURVIVAL_RULES
        self.BIRTH_RULES = _BIRTH_RULES
        self.START_DENSITY = _START_DENSITY

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
        #self.disableMouse()
 
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

        #to_kill = [(0,0,0),(0,0,1),(2,2,2)]
        #for x,y,z in to_kill:
        #    self.rhomdos[x][y][z].die()

        #for x in range(NUM_ROWS):
        #    for y in range(NUM_ROWS):
        #        for z in range(NUM_ROWS):
        #            rhomdo = self.rhomdos[x][y][z]
        #            print(x,y,z,rhomdo.alive,rhomdo.adjacent_alive())
 
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
                    self.rhomdos[x][y][z].determine_life()
        for x in range(NUM_ROWS):
            for y in range(NUM_ROWS):
                for z in range(NUM_ROWS):
                    self.rhomdos[x][y][z].enact_life()
        return Task.cont

    def updateClock(self, task):
        adjusted_time = task.time * 5
        if round(adjusted_time) > self.clock:
            self.clock = round(adjusted_time)
            print(self.clock)
            self.updateRhomdos()
        return Task.cont
 
app = Game(SURVIVAL_RULES_TEST,BIRTH_RULES_TEST,START_DENSITY_TEST)
app.run()
