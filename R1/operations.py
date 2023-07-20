def MxM(m1, m2):
    r = [[0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]]

    for i in range(len(m1)):
        for j in range(len(m2[0])):
            for k in range(len(m1[0])):
                r[i][j] += m1[i][k]*m2[k][j]
    return r

def MxV(m, v):
    r = [0, 0, 0, 0]
    for i in range(len(m)):
        for j in range(len(m[0])):
            r[i] += m[i][j]*v[j]
    return r