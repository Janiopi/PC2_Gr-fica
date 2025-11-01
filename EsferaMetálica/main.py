from glApp.PyOGApp import *
from glApp.Utils import *
from glApp.Square import *
from glApp.Triangle import *
from glApp.Axes import *
from glApp.Cube import *
from glApp.LoadMesh import *
from glApp.LoadMesh2 import *


vertex_shader = r'''
#version 330 core

in vec3 position;
in vec3 vertex_color;
in vec3 vertex_normal;

uniform mat4 projection_mat;
uniform mat4 model_mat;
uniform mat4 view_mat;

out vec3 frag_color;
out vec3 frag_normal;
out vec3 frag_pos;
out vec3 light_pos;

void main()
{
    // Posición de la luz = posición de la cámara (como antes)
    light_pos = vec3(inverse(model_mat) * 
                     vec4(view_mat[3][0], view_mat[3][1], view_mat[3][2], 1.0));

    gl_Position = projection_mat * inverse(view_mat) * model_mat * vec4(position, 1.0);

    frag_normal = mat3(transpose(inverse(model_mat))) * vertex_normal;  // Normal transformada correctamente
    frag_pos = vec3(model_mat * vec4(position, 1.0));
    frag_color = vertex_color;
}
'''

fragment_shader = r'''
#version 330 core

in vec3 frag_color;
in vec3 frag_normal;
in vec3 frag_pos;
in vec3 light_pos;

out vec4 final_color;

uniform vec3 view_pos;  // posición de la cámara (agregado)

void main()
{
    // === Configuración de la luz ===
    vec3 light_color = vec3(0.6, 0.6, 0.6);  // Luz gris
    float ambient_strength = 0.5;            // Luz ambiente suave
    float specular_strength = 1.5;           // Brillo especular
    int shininess = 128;                      // "Dureza" del brillo

    // === Componentes del modelo de Phong ===
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_pos);

    // 1. Componente ambiental
    vec3 ambient = ambient_strength * light_color;

    // 2. Componente difusa (Lambert)
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;

    // 3. Componente especular
    vec3 view_dir = normalize(view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    vec3 specular = specular_strength * spec * light_color;

    // === Resultado final ===
    vec3 result = (ambient + diffuse + specular) * frag_color;
    final_color = vec4(result, 1.0);
}
'''


class ShaderObjects(PyOGApp):

    def __init__(self):
        super().__init__(850, 200, 1000, 800)
        self.axes = None
        # self.moving_cube = None
        # self.teapot1 = None
        # self.donut = None
        self.sphere = None

    def initialise(self):
        self.program_id = create_program(vertex_shader, fragment_shader)
        #self.axes = Axes(self.program_id, pygame.Vector3(0, 0, 0))
        #self.moving_cube = Cube(self.program_id, location=pygame.Vector3(2, 1, 2),
         #                       move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
        #self.teapot1 = LoadMesh("models/teapot.obj", self.program_id,
         #                       move_translate=pygame.Vector3(0.1, 0, 0),
          #                      move_rotation=Rotation(2, pygame.Vector3(1, 1, 0)))
        # self.donut = LoadMesh("models/donut.obj", self.program_id,
        #                        location=pygame.Vector3(0, 0, 0),
        #                        scale=pygame.Vector3(0.5, 0.5, 0.5),
        #                        #move_rotation=Rotation(1, pygame.Vector3(0, 1, 0))
        #                        )
        self.sphere = LoadMesh2("models/sphere.obj", self.program_id,
                                  location=pygame.Vector3(0, 0, 0),
                               scale=pygame.Vector3(0.1, 0.1, 0.1),
                               move_rotation=Rotation(1, pygame.Vector3(0, 1, 0)))
        self.camera = Camera(self.program_id, self.screen_width, self.screen_height)
        glEnable(GL_DEPTH_TEST)

    def camera_init(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.program_id)
        self.camera.update()
        #self.axes.draw()
        #self.moving_cube.draw()
        #self.teapot1.draw()
        # self.donut.draw()
        self.sphere.draw()



ShaderObjects().mainloop()
