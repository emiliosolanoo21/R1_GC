from operations import MxV

def vertexShader(vertex, **kwargs):
    modelMatrix = kwargs["modelMatrix"]
    vt = [vertex[0], 
        vertex[1], 
        vertex[2], 
        1]

    vt = MxV(modelMatrix, vt)

    vt = [vt[0] / vt[3],
        vt[1] / vt[3],
        vt[2] / vt[3]]

    return vt

def fragmentShader(**kwargs):
    color = (1, 0, 0)
    return color