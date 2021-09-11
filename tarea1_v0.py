import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy
import sys

__author__ = "Ivan Sipiran"
__license__ = "MIT"

# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4

# Se modificó la función para generar un pequeño degradado en las fichas.
def crear_dama(x,y,r,g,b,radius):
    
    ANGULO_ABAJO = 0
    SHADING_LEVEL = 0.3

    circle = []
    for angle in range(0,360,10):
        x1 = x
        y1 = y
        c1 = (r,g,b)
        x2 = x+numpy.cos(numpy.radians(angle))*radius
        y2 = y+numpy.sin(numpy.radians(angle))*radius
        shading = abs((y2-(y+radius)))/radius
        # shading = max(abs(angle - 270)/180, abs(angle+90)/180)
        c2 = (r - SHADING_LEVEL * shading, g - SHADING_LEVEL * shading, b - SHADING_LEVEL * shading)

        x3 = x+numpy.cos(numpy.radians(angle+10))*radius
        y3 = y+numpy.sin(numpy.radians(angle+10))*radius
        shading = abs((y2-(y+radius)))/radius
        c3 = (r - SHADING_LEVEL * shading, g - SHADING_LEVEL * shading, b - SHADING_LEVEL * shading)

        circle.extend([x1, y1, 0.0, c1[0], c1[1], c1[2]])
        circle.extend([x2, 
                       y2, 
                       0.0, c2[0], c2[1], c2[2]])
        circle.extend([x3, 
                       y3, 
                       0.0, c3[0], c3[1], c3[2]])
    
    return numpy.array(circle, dtype = numpy.float32)


# Esta función genera la geometría completa del tabletro.
def crear_tablero():
    """None -> np.array"""
    """Crea la geometría del tablero de damas."""    
    board = []

    # Un tablero de damas es en esencia una matriz de 8x8 por lo que
    # no tendremos ajustes variables, intentaremos siempre rellenar el espacio de clipping
    # de -1 a 1.
    for x in range(0,8):
        for y in range(0,8):
            
            # Definimos para cada iteración las esquinas de un quad:
            # x1: esquina izquierda
            # x2: esquina derecha
            # y1: esquina superior
            # y2: esquina inferior

            x1 = -1 + x*(2/8)
            x2 = -1 + (x+1)*(2/8)
            y1 = 1 - y*(2/8)
            y2 = 1 - (y+1)*(2/8)
            
            # Definiremos el color del tile según su paridad, así contando desde
            # arriba a la izquierda hacia abajo a la derecha los impares serán negros
            # y los impares serán blancos.
            color1 = (0.2,0.2,0.2)
            color2 = (0,0,0)
            if (x+y)%2 != 0:
                color1 = (1,1,1)
                color2 = (0.8,0.8,0.8)
            
            # Primer triángulo para formar el quad
            board.extend([x1,y2,0.0,color2[0], color2[1], color2[2]])
            board.extend([x1,y1,0.0,color1[0], color1[1], color1[2]])
            board.extend([x2,y1,0.0,color1[0], color1[1], color1[2]])
            
            # Segundo triángulo para formar el quad
            board.extend([x2,y1,0.0,color1[0], color1[1], color1[2]])
            board.extend([x2,y2,0.0,color2[0], color2[1], color2[2]])
            board.extend([x1,y2,0.0,color2[0], color2[1], color2[2]])
    
    return numpy.array(board, dtype = numpy.float32)

# Función auxiliar para ubicar bien las fichas.
def posicion_dama(i,j):
    """ int,int -> (float, float)"""
    """Dada una coordenada del tablero de las damas las traduce a coordenadas de clipping y la deja centrada para obtener el centro de una ficha."""
    x1 = -1 + i*(2/8)
    x2 = -1 + (i+1)*(2/8)
    y1 = 1 - j*(2/8)
    y2 = 1 - (j+1)*(2/8)

    return ((x1+x2)/2, (y1+y2)/2)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Tarea 1", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    tablero = crear_tablero()

    # Lista que guardará los vectores con las geometrías de cada una de las 24 damas.
    damas = []

    FICHAS_BRIGHTNESS = 0.3

    # Fichas rojas
    # Iteramos para generar las fichas de ambos lados.
    for i in range(4):
        for j in range(3):
            coord_dama = posicion_dama( (2*i + (j%2 != 0)) , j )
            dama = crear_dama(coord_dama[0],coord_dama[1], 1.0, 0.0+FICHAS_BRIGHTNESS, 0.0+FICHAS_BRIGHTNESS, 0.1) 
            damas.append(dama)

    # Fichas azules
    for i in range(4):
        for j in range(3):
            coord_dama = posicion_dama( (1 + 2*i - (j%2 != 0)) , 7-j )
            dama = crear_dama(coord_dama[0],coord_dama[1], 0.0+FICHAS_BRIGHTNESS, 0.0+FICHAS_BRIGHTNESS, 1.0, 0.1) 
            damas.append(dama)

    # Defining shaders for our pipeline
    #region Shaders
    vertex_shader = """
    #version 330
    in vec3 position;
    in vec3 color;

    out vec3 newColor;
    void main()
    {
        gl_Position = vec4(position, 1.0f);
        newColor = color;
    }
    """

    fragment_shader = """
    #version 330
    in vec3 newColor;
    out vec4 outColor;

    void main()
    {   
        outColor = vec4(newColor, 1.0f);
    }
    """
    #endregion 

    # Binding artificial vertex array object for validation
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    # Assembling the shader program (pipeline) with both shaders
    shaderProgram = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    # Each shape must be attached to a Vertex Buffer Object (VBO)
    vboTablero = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vboTablero)
    glBufferData(GL_ARRAY_BUFFER, len(tablero) * SIZE_IN_BYTES, tablero, GL_STATIC_DRAW)


    # Lista de VBOs que almacenará los vértices con su información y color
    vbosDamas = []

    # Iteramos sobre los vectores de numpy con la geometría y los agregamos a un VBO cada una.
    for x in damas:
        vboDama = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboDama)
        glBufferData(GL_ARRAY_BUFFER, len(x) * SIZE_IN_BYTES, x, GL_STATIC_DRAW)
        vbosDamas.append(vboDama)

    # Telling OpenGL to use our shader program
    glUseProgram(shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.5,0.5, 0.5, 1.0)

    glClear(GL_COLOR_BUFFER_BIT)

    # ==============================================================
    # Se bindea en memoria del buffer el tablero
    glBindBuffer(GL_ARRAY_BUFFER, vboTablero)
    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)

    # Se cargan los atributos
    color = glGetAttribLocation(shaderProgram, "color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)
    
    # It renders a scene using the active shader program (pipeline) and the active VAO (shapes)
    glDrawArrays(GL_TRIANGLES, 0, int(len(tablero)))
    # ==============================================================

    # ==============================================================
    # Se itera sobre la lista de damas para dibujar cada una
    for x in range(len(damas)):
        vboDama = vbosDamas[x]
        dama = damas[x]
        # Se bindea en memoria del buffer la ficha que estamos iterando
        glBindBuffer(GL_ARRAY_BUFFER, vboDama)
        position = glGetAttribLocation(shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Se cargan los atributos
        color = glGetAttribLocation(shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)
        
        # It renders a scene using the active shader program (pipeline) and the active VAO (shapes)
        glDrawArrays(GL_TRIANGLES, 0, int(len(dama)/6))
    # ==============================================================

    # Moving our draw to the active color buffer
    glfw.swap_buffers(window)

    # Waiting to close the window
    while not glfw.window_should_close(window):

        # Getting events from GLFW
        glfw.poll_events()
        
    glfw.terminate()