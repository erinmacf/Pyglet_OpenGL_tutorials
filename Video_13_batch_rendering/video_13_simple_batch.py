from pyglet.gl import *
import ShaderLoader
from ObjLoader import ObjLoader
from pyrr import Vector3, matrix44, Matrix44
import time
import numpy


class Monkey:
    def __init__(self):

        mesh = ObjLoader()
        mesh.load_model("../models/monkey.obj")

        num_verts = len(mesh.model_vertices) // 3

        self.batch = pyglet.graphics.Batch()
        self.verts = self.batch.add(num_verts, GL_TRIANGLES, None, ('v3f', mesh.model_vertices),
                                                                   ('t2f', mesh.model_textures))

        shader = ShaderLoader.compile_shader("shaders/video_13_vert.glsl", "shaders/video_13_frag.glsl")

        glUseProgram(shader)

        # vertices
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.verts.vertices)
        glEnableVertexAttribArray(0)
        # textures
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, self.verts.tex_coords)
        glEnableVertexAttribArray(1)

        projection = matrix44.create_perspective_projection_matrix(45.0, 1280 / 720, 0.1, 100.0).flatten().astype("float32")
        view = matrix44.create_from_translation(Vector3([0.0, 0.0, -2.0])).flatten().astype("float32")
        self.translation = matrix44.create_from_translation(Vector3([0.0, 0.0, -2.0]))

        c_projection = numpy.ctypeslib.as_ctypes(projection)
        c_view = numpy.ctypeslib.as_ctypes(view)

        view_loc = glGetUniformLocation(shader, b"view")
        proj_loc = glGetUniformLocation(shader, b"projection")
        self.model_loc = glGetUniformLocation(shader, b"model")

        glUniformMatrix4fv(view_loc, 1, GL_FALSE, c_view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, c_projection)

        # region texture settings and loading
        texture = GLuint(0)
        glGenTextures(1, texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        # set the texture wrapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set the texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # endregion

        image = pyglet.image.load('../models/monkey.jpg')
        image_data = image.get_data('RGB', image.pitch)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    def rotate(self):
        ct = time.clock()
        rot_y = Matrix44.from_y_rotation(ct)
        transform = matrix44.multiply(rot_y, self.translation).flatten().astype("float32")
        c_transform = numpy.ctypeslib.as_ctypes(transform)

        glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, c_transform)


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(400, 300)
        glClearColor(0.2, 0.3, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)

        self.monkey = Monkey()

    def on_draw(self):
        self.clear()
        self.monkey.rotate()
        self.monkey.batch.draw()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    def update(self, dt):
        pass


if __name__ == "__main__":
    window = MyWindow(1280, 720, "My Pyglet Window", resizable=True)
    pyglet.clock.schedule_interval(window.update, 1/60.0)
    pyglet.app.run()
