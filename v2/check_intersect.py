def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect


def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def boolHexagonalLineIntersect(hexagonalCoordinates, p1, p2):
    for i in range(0, len(hexagonalCoordinates) - 1):
        point1 = (hexagonalCoordinates[i][0], hexagonalCoordinates[i][1])
        point2 = (hexagonalCoordinates[i+1][0], hexagonalCoordinates[i+1][1])
        if intersect(p1, p2, point1, point2):
            return True
    return False

hexagonalCoordinates = [
    [
        1,
        1
    ],
    [
        3,
        3
    ],
    [
        -112.07487793157966,
        33.35969573361516
    ],
    [
        -112.1154646018878,
        33.37213303894667
    ],
    [
        -112.14910880414443,
        33.34917391297312
    ],
    [
        -112.14216470823824,
        33.31378483521286
    ],
    [
        -112.10159788091084,
        33.30135043883555
    ]
]

p1 = (
    3,
    1
)

p2 = (
    1,
    3
)

print(boolHexagonalLineIntersect(hexagonalCoordinates, p1, p2))