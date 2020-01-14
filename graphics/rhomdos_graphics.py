from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, \
    GeomTriangles, GeomNode


SR2 = 2 ** .5


class RhomdoRender(NodePath):
    def __init__(self, rhomdo, num_rows):
        self.rhomdo = rhomdo
        self.geomnode = GeomNode("rhomdo")
        super().__init__(self.geomnode)
        self.color = (rhomdo.x / num_rows), (rhomdo.y / num_rows), (rhomdo.z / num_rows), 1

        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("vertices", format, Geom.UHStatic)
        vdata.setNumRows(14)

        vertexWriter = GeomVertexWriter(vdata, "vertex")
        colorWriter = GeomVertexWriter(vdata, "color")

        for i in range(14):
            colorWriter.addData4f(*self.color)

        realX = rhomdo.x * 2 - num_rows
        realY = rhomdo.y * 2 - num_rows
        realZ = rhomdo.z * SR2 - SR2 * .5 * num_rows
        if self.rhomdo.odd:
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

        for depth in self.game.rhomdos:
            for column in depth:
                for rhomdo in column:
                    rr = RhomdoRender(rhomdo, game.num_rows)
                    rhomdo.add_rr(rr)
                    render.attachNewNode(rr.geomnode)

        plight = PointLight('plight')
        plight.setColor(VBase4(1, 1, 1, 1))
        plight.setAttenuation((0, 0, .0005))
        self.plnp = render.attachNewNode(plight)
        self.plnp.setPos(0, 0, (game.num_rows * SR2) + 40)
        render.setLight(self.plnp)

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

    def updateClock(self, task):
        adjusted_time = task.time * 5
        if round(adjusted_time) > self.clock:
            self.clock = round(adjusted_time)
            self.game.updateRhomdos()
        return Task.cont