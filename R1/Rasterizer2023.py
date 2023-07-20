from gl import Renderer
import shaders
width = 2048
height = 2048

rend = Renderer(width, height)

rend.vertexShader = shaders.vertexShader
rend.fragmentShader = shaders.fragmentShader

rend.glLoadModel("cap.obj", translate=(width/2, height/4, 0), scale=(4, 4, 4))

rend.glRender()

#Nombre del framebuffer creado y guardado.
rend.glFinish("result.bmp")