from .LoadMesh import LoadMesh
import pygame
import math

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
        # If the OBJ had no vt entries, generate spherical UVs per vertex
        if len(uvs) == 0 and len(vertices) > 0:
            uvs = []
            for (x, y, z) in vertices:
                r = math.sqrt(x * x + y * y + z * z)
                if r == 0:
                    r = 1.0
                u = 0.5 + math.atan2(z, x) / (2 * math.pi)
                v = 0.5 - math.asin(y / r) / math.pi
                uvs.append((u, v))
            # map uvs indices directly from vertex triangles
            uvs_ind = list(triangles)

        # If normals missing, compute per-vertex normals by accumulating face normals
        if len(normals) == 0 and len(vertices) > 0:
            normals_acc = [(0.0, 0.0, 0.0) for _ in vertices]
            for i in range(0, len(triangles), 3):
                i0 = triangles[i]
                i1 = triangles[i + 1]
                i2 = triangles[i + 2]
                v0 = vertices[i0]
                v1 = vertices[i1]
                v2 = vertices[i2]
                ax = v1[0] - v0[0]
                ay = v1[1] - v0[1]
                az = v1[2] - v0[2]
                bx = v2[0] - v0[0]
                by = v2[1] - v0[1]
                bz = v2[2] - v0[2]
                # cross product a x b
                cx = ay * bz - az * by
                cy = az * bx - ax * bz
                cz = ax * by - ay * bx
                n0 = normals_acc[i0]
                normals_acc[i0] = (n0[0] + cx, n0[1] + cy, n0[2] + cz)
                n1 = normals_acc[i1]
                normals_acc[i1] = (n1[0] + cx, n1[1] + cy, n1[2] + cz)
                n2 = normals_acc[i2]
                normals_acc[i2] = (n2[0] + cx, n2[1] + cy, n2[2] + cz)
            normals = []
            for (nx, ny, nz) in normals_acc:
                length = math.sqrt(nx * nx + ny * ny + nz * nz)
                if length == 0:
                    normals.append((0.0, 0.0, 1.0))
                else:
                    normals.append((nx / length, ny / length, nz / length))
            normal_ind = list(triangles)

        return vertices, triangles, uvs, uvs_ind, normals, normal_ind