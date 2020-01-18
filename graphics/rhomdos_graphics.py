from math import pi, sin, cos, ceil

from direct.showbase.ShowBase import ShowBase, exitfunc
from direct.task import Task
from panda3d.core import PointLight, VBase4, NodePath, Geom, GeomVertexWriter, GeomVertexFormat, GeomVertexData, \
    GeomTriangles, GeomNode
import imageio
from tqdm import tqdm

import os

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
            self.color = max(self.color[0] - .03, 0), max(self.color[1] - .03, 0), max(self.color[2] - .03, 0), 1

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

        rhomGeom = Geom(vdata)
        rhomGeom.addPrimitive(tris)
        self.geomnode.addGeom(rhomGeom)


class RhomdosRender:
    def __init__(self, game, duration=None, storage_path="storage/3d/frame", fps=30, as_gif=False, gif_name=None):
        self.game = game
        self.duration = duration
        self.storage_path = storage_path
        self.fps = fps
        self.as_gif = as_gif
        self.gif_name = gif_name
        self.base = ShowBase(windowType=('offscreen' if as_gif else None))

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

        if self.as_gif:
            self.base.movie(self.storage_path, duration=self.duration, fps=self.fps)

        self.base.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.base.taskMgr.add(self.updateClock, "UpdateClock")

        self.frame = 0
        self.game_step = 0

    def spinCameraTask(self, task):
        angleDegrees = task.time * 40.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.base.camera.setPos(60 * sin(angleRadians), -60 * cos(angleRadians), 32)
        self.base.camera.setHpr(angleDegrees, -30, 0)
        return Task.cont
    
    def run(self):
        if self.as_gif:
            for i in tqdm(list(range(self.duration*self.fps))):
                self.base.taskMgr.step()
            self.generate_gif()
        else:
            while True:
                self.base.taskMgr.step()

    def updateClock(self, task):
        self.frame = task.time

        adjusted_time = task.time * 8
        if ceil(adjusted_time) > self.game_step:
            self.updateRhomdos()
            self.game_step = ceil(adjusted_time)

        return Task.cont

    def generate_gif(self):
        with imageio.get_writer(self.gif_name, mode='I') as writer:
            for i in tqdm(list(range(1, self.duration*self.fps))):
                filename = f"{self.storage_path}_{str(i).rjust(4, '0')}.png"
                writer.append_data(imageio.imread(filename))
                os.remove(filename)

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
