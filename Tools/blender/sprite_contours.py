"""Maschera Freestyle delle silhouette visibili delle braccia, Blender 5.2."""
import bpy
import numpy as np


class ArmContours:
    def __init__(self, scene):
        if not bpy.app.build_options.freestyle:
            raise RuntimeError("Questa build di Blender non include Freestyle")
        body = scene.objects.get("Body")
        if body is None or body.type != 'MESH':
            raise RuntimeError("Il contorno delle braccia richiede la mesh Body")
        self.scene = scene
        self.layer = bpy.context.view_layer
        self.settings = self.layer.freestyle_settings

        arm_names = {name + side for name in ("upper_arm.", "forearm.", "hand.")
                     for side in "LR"}
        groups = {group.index for group in body.vertex_groups if group.name in arm_names}
        if not groups:
            raise RuntimeError("Body non ha i gruppi di pesi delle braccia")
        arm_vertices = {vertex.index for vertex in body.data.vertices
                        if sum(group.weight for group in vertex.groups
                               if group.group in groups) > .5}
        marks = body.data.attributes.get("freestyle_face")
        if marks is None:
            marks = body.data.attributes.new(name="freestyle_face", type='BOOLEAN', domain='FACE')
        if marks.domain != 'FACE' or marks.data_type != 'BOOLEAN':
            raise RuntimeError("freestyle_face deve essere un attributo BOOLEAN/FACE")
        marks.data.foreach_set("value", [all(index in arm_vertices for index in face.vertices)
                                         for face in body.data.polygons])
        body.data.update()

        self.lines = self.settings.linesets.get("SpriteArms")
        if self.lines is None:
            self.lines = self.settings.linesets.new("SpriteArms")
        enabled = {"select_silhouette", "select_by_visibility", "select_by_edge_types",
                   "select_by_face_marks"}
        for prop in self.lines.bl_rna.properties:
            if prop.type == 'BOOLEAN' and prop.identifier.startswith(("select_", "exclude_")):
                setattr(self.lines, prop.identifier, prop.identifier in enabled)
        self.lines.visibility = 'VISIBLE'
        self.lines.face_mark_condition = 'BOTH'
        self.lines.face_mark_negation = 'INCLUSIVE'
        self.lines.edge_type_negation = 'INCLUSIVE'
        self.lines.edge_type_combination = 'OR'
        self.lines.show_render = False

        style = self.lines.linestyle
        if style is None:
            style = bpy.data.linestyles.new("SpriteArms_" + scene.name)
            self.lines.linestyle = style
        elif style.users > 1:
            style = style.copy()
            self.lines.linestyle = style
        style.name = "SpriteArms_" + scene.name
        style.color = (0, 1, 0)
        style.thickness = 1
        style.thickness_position = 'OUTSIDE'

    def mask(self, path, grab) -> np.ndarray:
        render = self.scene.render
        settings = self.settings
        previous_lines = [(line, line.show_render) for line in settings.linesets]
        previous = (render.use_freestyle, settings.as_render_pass, settings.mode,
                    self.layer.use_freestyle, render.filepath)
        try:
            for line in settings.linesets:
                line.show_render = line == self.lines
            render.use_freestyle = True
            settings.as_render_pass = False
            settings.mode = 'EDITOR'
            self.layer.use_freestyle = True
            render.filepath = path
            bpy.ops.render.render(write_still=True, scene=self.scene.name)
            rgba = grab(path)
            red, green, blue = rgba[..., 0], rgba[..., 1], rgba[..., 2]
            return (green > .7) & (green > red + .3) & (green > blue + .3)
        finally:
            (render.use_freestyle, settings.as_render_pass, settings.mode,
             self.layer.use_freestyle, render.filepath) = previous
            for line, show in previous_lines:
                line.show_render = show
