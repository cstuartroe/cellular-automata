from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, \
    GeomTriangles, GeomNode


SR2 = 2 ** .5


class RhomdoRender(NodePath):
    def __init__(self, position, gridshape):
        self.geomnode = GeomNode("rhomdo")
        super().__init__(self.geomnode)

        z, y, x = position
        depth, height, width = gridshape
        self.color = (x / width), (y / height), (z / depth), 1

        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("vertices", format, Geom.UHStatic)
        vdata.setNumRows(14)

        vertexWriter = GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")

        for i in range(14):
            colorWriter.addData4f(*self.color)

        realX = x * 2 - width
        realY = y * 2 - height
        realZ = z * SR2 - SR2 * .5 * depth
        odd = z % 2 == 1
        if odd:
            realX += 1
            realY += 1

        vertexWriter.addData3f(realX, realY, realZ + SR2)

        vertexWriter.addData3f(realX - 1, realY, realZ + (SR2 / 2))
        vertexWriter.addData3f(realX, realY - 1, realZ + (SR2 / 2))
        vertexWriter.addData3f(realX + 1, realY, realZ + (SR2 / 2))
        vertexWriter.addData3f(realX, realY + 1, realZ + (SR2 / 2))

        vertexWriter.addData3f(realX - 1, realY - 1, realZ)
        vertexWriter.addData3f(realX + 1, realY - 1, realZ)
        vertexWriter.addData3f(realX + 1, realY + 1, realZ)
        vertexWriter.addData3f(realX - 1, realY + 1, realZ)

        vertexWriter.addData3f(realX - 1, realY, realZ - (SR2 / 2))
        vertexWriter.addData3f(realX, realY - 1, realZ - (SR2 / 2))
        vertexWriter.addData3f(realX + 1, realY, realZ - (SR2 / 2))
        vertexWriter.addData3f(realX, realY + 1, realZ - (SR2 / 2))

        vertexWriter.addData3f(realX, realY, realZ - SR2)

        # step 2) make primitives and assign vertices to them
        tris = GeomTriangles(Geom.UHStatic)

        # top
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

        # middle
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

        # bottom
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

        # step 3) make a Geom object to hold the primitives
        rhomGeom = Geom(vdata)
        rhomGeom.addPrimitive(tris)
        # now put squareGeom in a GeomNode. You can now position your geometry in the scene graph.
        self.geomnode.addGeom(rhomGeom)


class GameRender(ShowBase):
    def __init__(self, game):
        self.game = game
        ShowBase.__init__(self)

        depth, height, width = game.shape
        self.rhomdos = []

        for z in range(depth):
            self.rhomdos.append([])
            for y in range(height):
                self.rhomdos[-1].append([])
                for x in range(width):
                    rr = RhomdoRender((z, y, x), game.shape)
                    render.attachNewNode(rr.geomnode)
                    self.rhomdos[-1][-1].append(rr)

        plight = PointLight('plight')
        plight.setColor(VBase4(1, 1, 1, 1))
        plight.setAttenuation((0, 0, .0005))
        self.plnp = render.attachNewNode(plight)
        self.plnp.setPos(0, 0, (game.shape[0] * SR2) + 40)
        render.setLight(self.plnp)

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.updateClock, "UpdateClock")
        self.clock = 0

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 40.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(100 * sin(angleRadians), -100.0 * cos(angleRadians), 50)
        self.camera.setHpr(angleDegrees, -30, 0)
        return Task.cont

    def updateClock(self, task):
        adjusted_time = task.time * 8
        if round(adjusted_time) > self.clock:
            self.updateRhomdos()
            self.clock = round(adjusted_time)
        return Task.cont

    def updateRhomdos(self):
        self.game.advance()
        depth, height, width = self.game.shape
        for z in range(depth):
            for y in range(height):
                for x in range(width):
                    rr = self.rhomdos[z][y][x]
                    if self.game.grid[-1, z, y, x, 0] == 1:
                        rr.show()
                    else:
                        rr.hide()