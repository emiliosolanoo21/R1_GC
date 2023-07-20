'''
Libreria para simular las variables como
si estuvieran escritas en C.
'''
import struct
from collections import namedtuple
from obj import Obj
from operations import MxM

V3 = namedtuple('Point2', ['x', 'y', 'z'])
triangles = 2

def char(c):
    #1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def color(r, g, b):
    '''
    Lo que regresa esto es un pixel y,
    la cantidad de rojo, verde y azul
    que tendrá.
    '''
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)])

class Model(object):
    def __init__(self, filename, translate = (0, 0, 0), scale = (1, 1, 1)):
        model = Obj(filename)

        self.vertices = model.vertices
        self.textcoords = model.textcoords
        self.normals = model.normals
        self.faces = model.faces
        
        self.translate = translate
        self.scale = scale

class Renderer(object):
    #Constructor
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.glClearColor(0, 0, 0)
        self.glClear()
        
        self.glColor(1, 1, 1)

        self.vertexShader = None
        self.fragmentShader = None
        self.primitiveType = triangles
        self.vertexBuffer = []

        self.objects = []
        
    #Definir color del fondo
    def glClearColor(self, r, g, b):
        self.clearColor = color(r, g, b)
    
    def glClear(self):
        self.pixels = [[self.clearcolor for y in range(self.height)]
                        for x in range(self.width)]
    
    def glColor(self, r, g, b):
        self.currColor = color(r, g, b)
        
    def glPoint(self, x, y, clr = None):
        if(0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor
    
    def glClear(self):
        self.pixels = [[self.clearColor for y in range(self.height)]
                        for x in range(self.width)]
    
    def glLine(self, v0, v1, clr = None):
        x0 = int(v0[0])
        x1 = int(v1[0])
        y0 = int(v0[1])
        y1 = int(v1[1])

        if (x0 == x1 and y0 == y1):
            self.glPoint(x0, y0)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        
        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        m = dy / dx
        y = y0

        offset = 0
        limit = 0.5

        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x, clr or self.currColor)
            else:
                self.glPoint(x, y, clr or self.currColor)
            offset += m

            if (offset >= limit):
                if (y0 < y1):
                    y += 1
                else:
                    y -= 1
                limit += 1


    def glTriangle(self, v0, v1, v2, clr = None):
        self.glLine(v0, v1, clr or self.currColor)
        self.glLine(v1, v2, clr or self.currColor)
        self.glLine(v2, v0, clr or self.currColor)


    def glAddVertices(self, verts):
        for v in verts:
            self.vertexBuffer.append(v)


    def glPrimitiveAssembly(self, tVerts):
        primitives = []

        if (self.primitiveType == triangles):
            for i in range(0, len(tVerts), 3):
                triangle = []
                triangle.append(tVerts[i])
                triangle.append(tVerts[i + 1])
                triangle.append(tVerts[i + 2])
                primitives.append(triangle)
            
        return primitives

    def glLoadModel(self, filename, translate = (0, 0, 0), scale = (1, 1, 1)):
        self.objects.append(Model(filename, translate, scale))
    
    def glRender(self):
        tVerts = []

        for model in self.objects:
            mMatrix = self.glModelMatrix(model.translate, model.scale)

            for face in model.faces:
                vertCount = len(face)
                
                v0 = model.vertices[face[0][0] - 1]
                v1 = model.vertices[face[1][0] - 1]
                v2 = model.vertices[face[2][0] - 1]

                if vertCount == 4:
                    v3 = model.vertices[face[3][0] - 1]
                
                if self.vertexShader:
                    v0 = self.vertexShader(v0, modelMatrix = mMatrix)
                    v1 = self.vertexShader(v1, modelMatrix = mMatrix)
                    v2 = self.vertexShader(v2, modelMatrix = mMatrix)
                    if vertCount == 4:
                        v3 = self.vertexShader(v3, modelMatrix = mMatrix)
                
                tVerts.append(v0)
                tVerts.append(v1)
                tVerts.append(v2)
                if vertCount == 4:
                    tVerts.append(v0)
                    tVerts.append(v2)
                    tVerts.append(v3)
        
        primitives = self.glPrimitiveAssembly(tVerts)

        if (self.fragmentShader):
            primColor = self.fragmentShader()
            primColor = color(primColor[0], primColor[1], primColor[2])
        else:
            primColor = self.currColor

        for prim in primitives:
            if (self.primitiveType == triangles):
                self.glTriangle(prim[0], prim[1], prim[2], primColor)

    def glModelMatrix(self, translate = (0, 0, 0), scale = (1, 1, 1)):
        translation = [[1, 0, 0, translate[0]],
                        [0, 1, 0, translate[1]],
                        [0, 0, 1, translate[2]],
                        [0, 0, 0, 1]]

        scaleMat = [[scale[0], 0, 0, 0],
                    [0, scale[1], 0, 0],
                    [0, 0, scale[2], 0],
                    [0, 0, 0, 1]]

        return MxM(translation, scaleMat)
    
    def glFinish(self, filename):
        with open(filename, "wb") as file:
        #Formato de un archivo bmp:
            #Header
            file.write(char("B"))
            file.write(char("M"))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))
            
            #InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            
            #ColorTable
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])
    