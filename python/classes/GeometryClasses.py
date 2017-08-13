def fix_mesh(mesh, detail="normal"):
    from numpy.linalg import norm
    import pymesh

    bbox_min, bbox_max = mesh.bbox
    diag_len = norm(bbox_max - bbox_min)
    if detail == "normal":
        target_len = diag_len * 1e-2
    elif detail == "high":
        target_len = diag_len * 5e-3
    elif detail == "low":
        target_len = diag_len * 0.03
    print("Target resolution: {} mm".format(target_len))

    count = 0
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100)
    mesh, __ = pymesh.split_long_edges(mesh, target_len)
    num_vertices = mesh.num_vertices
    while True:
        mesh, __ = pymesh.collapse_short_edges(mesh, 1e-6)
        mesh, __ = pymesh.collapse_short_edges(mesh, target_len,
                preserve_feature=True)
        mesh, __ = pymesh.remove_obtuse_triangles(mesh, 150.0, 100)
        if mesh.num_vertices == num_vertices:
            break

        num_vertices = mesh.num_vertices
        print("#v: {}".format(num_vertices))
        count += 1
        if count > 10:
            break

    mesh = pymesh.resolve_self_intersection(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh = pymesh.compute_outer_hull(mesh)
    mesh, __ = pymesh.remove_duplicated_faces(mesh)
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5)
    mesh, __ = pymesh.remove_isolated_vertices(mesh)

    return mesh

def ray_triangle_intersection(ray_near, ray_dir, V):
    """
    Möller–Trumbore intersection algorithm in pure python
    Based on http://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
    """
    import numpy as np

    v1, v2, v3 = V
    eps = 0.000001
    edge1 = v2 - v1
    edge2 = v3 - v1
    pvec = np.cross(ray_dir, edge2)
    det = edge1.dot(pvec)

    if abs(det) < eps:
        return False, None

    inv_det = 1. / det
    tvec = ray_near - v1
    u = tvec.dot(pvec) * inv_det
    if u < 0. or u > 1.:
        return False, None

    qvec = np.cross(tvec, edge1)
    v = ray_dir.dot(qvec) * inv_det
    if v < 0. or u + v > 1.:
        return False, None

    t = edge2.dot(qvec) * inv_det
    if t < eps:
        return False, None

    return True, t

def lowestFaceVertex(v0, v1, v2):
    from numpy import array

    V = [v0, v1, v2]
    x0 = v0[0]
    y0 = v0[1]
    z0 = v0[2]
    x1 = v1[0]
    y1 = v1[1]
    z1 = v1[2]
    x2 = v2[0]
    y2 = v2[1]
    z2 = v2[2]
    X = [x0, x1, x2]
    Y = [y0, y1, y2]
    Z = [z0, z1, z2]


    Zsort = Z.sort()
    print('Z:', Z)
    if Zsort[0] == Zsort[2]:
        return array([sum(X)/3, sum(Y)/3, sum(Z)/3])

    elif Zsort[0] > Zsort[1]:
        i = Z.index[Zsort[0]]
        return V[i]

    elif Zsort[0] == Zsort[1]:
        i0 = Z.index[Zsort[0]]
        i1 = Z.index[Zsort[1]]
        x = 0.5*(X[i0] + X[i1])
        y = 0.5*(Y[i0] + Y[i1])
        return array([x, y, Zsort[0]])


