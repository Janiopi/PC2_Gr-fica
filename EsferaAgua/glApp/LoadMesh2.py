from .LoadMesh import LoadMesh
import pygame

class LoadMesh2(LoadMesh):
    def load_drawing(self, filename):
        # implementación robusta: acepta v/vt/vn, v//vn, triangula polígonos
        vertices = []
        triangles = []
        normals = []
        normal_ind = []
        uvs = []
        uvs_ind = []

        def to_idx(s, length):
            if s is None:
                return None
            i = int(s)
            if i < 0:
                return length + i
            return i - 1

        with open(filename, 'r', encoding='utf-8', errors='ignore') as fp:
            for raw in fp:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('v '):
                    parts = line.split()
                    vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif line.startswith('vn '):
                    parts = line.split()
                    normals.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif line.startswith('vt '):
                    parts = line.split()
                    uvs.append((float(parts[1]), float(parts[2])))
                elif line.startswith('f '):
                    toks = line[2:].split()
                    face = []
                    for tok in toks:
                        vals = tok.split('/')
                        vi = vals[0] if len(vals) > 0 and vals[0] != '' else None
                        ti = vals[1] if len(vals) > 1 and vals[1] != '' else None
                        ni = vals[2] if len(vals) > 2 and vals[2] != '' else None
                        face.append((to_idx(vi, len(vertices)), to_idx(ti, len(uvs)), to_idx(ni, len(normals))))
                    for i in range(1, len(face)-1):
                        v0, v1, v2 = face[0], face[i], face[i+1]
                        triangles.extend([v0[0], v1[0], v2[0]])
                        uvs_ind.extend([v0[1] if v0[1] is not None else 0,
                                        v1[1] if v1[1] is not None else 0,
                                        v2[1] if v2[1] is not None else 0])
                        normal_ind.extend([v0[2] if v0[2] is not None else 0,
                                           v1[2] if v1[2] is not None else 0,
                                           v2[2] if v2[2] is not None else 0])
        return vertices, triangles, uvs, uvs_ind, normals, normal_ind