; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost
;   0 1 2 3
;   . x . g 0
;   p x   . 1
;   . x . . 2
;   . .   x 3 

(define (problem ghostSample) (:domain ghost)
(:objects
    posx-0 posx-1 posx-2 posx-3
    posy-0 posy-1 posy-2 posy-3
)

(:init
    (adjcent posx-0 posx-1)
    (adjcent posx-1 posx-2)
    (adjcent posx-2 posx-3)

    (adjcent posy-0 posy-1)
    (adjcent posy-1 posy-2)
    (adjcent posy-2 posy-3)

    (same posx-0 posx-0)
    (same posx-1 posx-1)
    (same posx-2 posx-2)
    (same posx-3 posx-3)

    (same posy-0 posy-0)
    (same posy-1 posy-1)
    (same posy-2 posy-2)
    (same posy-3 posy-3)

    (pacman-at posx-0 posy-1)
    (ghost-at posx-3 posy-0)
    (wall-at posx-1 posy-0)
    (wall-at posx-1 posy-1)
    (wall-at posx-1 posy-2)
    (wall-at posx-3 posy-3)
)

(:goal (and
        (not (pacman-at posx-0 posy-0))
        (not (pacman-at posx-0 posy-1))
        (not (pacman-at posx-0 posy-2))
        (not (pacman-at posx-0 posy-3))
        (not (pacman-at posx-1 posy-0))
        (not (pacman-at posx-1 posy-1))
        (not (pacman-at posx-1 posy-2))
        (not (pacman-at posx-1 posy-3))
        (not (pacman-at posx-2 posy-0))
        (not (pacman-at posx-2 posy-1))
        (not (pacman-at posx-2 posy-2))
        (not (pacman-at posx-2 posy-3))
        (not (pacman-at posx-3 posy-0))
        (not (pacman-at posx-3 posy-1))
        (not (pacman-at posx-3 posy-2))
        (not (pacman-at posx-3 posy-3))
    )
)

; (:metric minimize (cost))
)
