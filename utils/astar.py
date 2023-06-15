import math, heapq, time


def blocked(cX, cY, dX, dY, matrix):
    if cX + dX < 0 or cX + dX >= matrix.shape[0]:
        return True
    if cY + dY < 0 or cY + dY >= matrix.shape[1]:
        return True
    if dX != 0 and dY != 0:
        if matrix[cX + dX][cY] == 1 and matrix[cX][cY + dY] == 1:
            return True
        if matrix[cX + dX][cY + dY] == 1:
            return True
    else:
        if dX != 0:
            if matrix[cX + dX][cY] == 1:
                return True
        else:
            if matrix[cX][cY + dY] == 1:
                return True
    return False


def heuristic(a, b, hchoice):
    if hchoice == 1:
        xdist = math.fabs(b[0] - a[0])
        ydist = math.fabs(b[1] - a[1])
        if xdist > ydist:
            return 14 * ydist + 10 * (xdist - ydist)
        else:
            return 14 * xdist + 10 * (ydist - xdist)
    if hchoice == 2:
        return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def method(matrix, start, goal, hchoice):
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal, hchoice)}

    pqueue = []

    heapq.heappush(pqueue, (fscore[start], start))

    starttime = time.time()

    while pqueue:

        current = heapq.heappop(pqueue)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path = path[::]
            #print(gscore[goal])
            endtime = time.time()
            return (path, round(endtime - starttime, 6))

        close_set.add(current)
        for dX, dY in [
            (0, 1),
            (0, -1),
            (1, 0),
            (-1, 0),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]:

            if blocked(current[0], current[1], dX, dY, matrix):
                continue

            neighbour = current[0] + dX, current[1] + dY

            if hchoice == 1:
                if dX != 0 and dY != 0:
                    tentative_g_score = gscore[current] + 14
                else:
                    tentative_g_score = gscore[current] + 10
            elif hchoice == 2:
                if dX != 0 and dY != 0:
                    tentative_g_score = gscore[current] + math.sqrt(2)
                else:
                    tentative_g_score = gscore[current] + 1

            if (
                neighbour in close_set
            ):  # and tentative_g_score >= gscore.get(neighbour,0):
                continue

            if tentative_g_score < gscore.get(
                neighbour, 0
            ) or neighbour not in [i[1] for i in pqueue]:
                came_from[neighbour] = current
                gscore[neighbour] = tentative_g_score
                fscore[neighbour] = tentative_g_score + heuristic(
                    neighbour, goal, hchoice
                )
                heapq.heappush(pqueue, (fscore[neighbour], neighbour))
        endtime = time.time()
    return (0, round(endtime - starttime, 6))
