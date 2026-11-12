# Genera le griglie di caratteri del puff (6 frame 32x32) da incollare in Pixelorama con draw_pixels; palette o=#3a1418 h=#fff6e8 b=#f6e2b0 s=#e3c084.
import json, math
N = 32
F = [
 [(16,19,4),(13,20,3),(19,20,3)],
 [(16,22,5),(10,20,5),(22,20,5),(16,17,7)],
 [(8,19,5),(24,19,5),(12,23,5),(20,23,5),(16,21,7),(16,13,6),(10,15,5),(22,15,5)],
 [(6,18,4),(26,18,4),(10,24,4),(22,24,4),(16,15,7),(16,9,4)],
 [(5,16,3),(27,16,3),(7,24,3),(25,24,3),(16,12,4),(16,6,2)],
 [(4,13,2),(28,12,2),(5,25,2),(27,25,2),(15,8,2),(9,5,1)],
]
def tone(lobes):
    t = [[None]*N for _ in range(N)]
    for cx,cy,r in lobes:
        for y in range(N):
            for x in range(N):
                if (x-cx)**2+(y-cy)**2 <= r*r+r*0.6:
                    l = ((cx-x)+(cy-y))/math.sqrt(2)/max(r,1)   # >0: lato alto-sinistra
                    t[y][x] = 'h' if l > 0.45 else ('s' if l < -0.35 else 'b')
    return t
def grid(t):
    P = [[None]*(N+2) for _ in range(N+2)]
    for y in range(N):
        for x in range(N): P[y+1][x+1] = t[y][x]
    out = []
    for y in range(N):
        row = ''
        for x in range(N):
            if t[y][x]: row += t[y][x]
            else:
                nb = P[y][x+1] or P[y+2][x+1] or P[y+1][x] or P[y+1][x+2]
                row += 'o' if nb else '.'
        out.append(row)
    return out
frames = [grid(tone(l)) for l in F]
json.dump(frames, open("puff.json","w"))
print("\n".join(frames[2])); print(); print("\n".join(frames[1][10:28]))
