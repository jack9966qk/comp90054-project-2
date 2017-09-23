; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost
;   0 1 2 3
;   . x . g 0
;   p x   . 1
;   . x . . 2
;   . .   x 3 

(define (problem ghostSample) (:domain ghost)
(:objects
    pos-0-0 pos-0-1 pos-0-2 pos-0-3
    pos-1-0 pos-1-1 pos-1-2 pos-1-3
    pos-2-0 pos-2-1 pos-2-2 pos-2-3
    pos-3-0 pos-3-1 pos-3-2 pos-3-3
)

(:init
    (connected pos-0-0 pos-0-1)
    (connected pos-0-0 pos-1-0)
    (connected pos-0-1 pos-0-2)
    (connected pos-0-1 pos-1-1)
    (connected pos-0-2 pos-0-3)
    (connected pos-0-2 pos-1-2)
    (connected pos-0-3 pos-1-3)
    (connected pos-1-0 pos-1-1)
    (connected pos-1-0 pos-2-0)
    (connected pos-1-1 pos-1-2)
    (connected pos-1-1 pos-2-1)
    (connected pos-1-2 pos-1-3)
    (connected pos-1-2 pos-2-2)
    (connected pos-1-3 pos-2-3)
    (connected pos-2-0 pos-2-1)
    (connected pos-2-0 pos-3-0)
    (connected pos-2-1 pos-2-2)
    (connected pos-2-1 pos-3-1)
    (connected pos-2-2 pos-2-3)
    (connected pos-2-2 pos-3-2)
    (connected pos-2-3 pos-3-3)
    (connected pos-3-0 pos-3-1)
    (connected pos-3-1 pos-3-2)
    (connected pos-3-2 pos-3-3)

    (pacman-at pos-0-1)
    (ghost-at pos-3-0)
    (wall-at pos-1-0)
    (wall-at pos-1-1)
    (wall-at pos-1-2)
    (wall-at pos-3-3)
)

(:goal (and
        (not (pacman-at pos-0-0))
        (not (pacman-at pos-0-1))
        (not (pacman-at pos-0-2))
        (not (pacman-at pos-0-3))
        (not (pacman-at pos-1-0))
        (not (pacman-at pos-1-1))
        (not (pacman-at pos-1-2))
        (not (pacman-at pos-1-3))
        (not (pacman-at pos-2-0))
        (not (pacman-at pos-2-1))
        (not (pacman-at pos-2-2))
        (not (pacman-at pos-2-3))
        (not (pacman-at pos-3-0))
        (not (pacman-at pos-3-1))
        (not (pacman-at pos-3-2))
        (not (pacman-at pos-3-3))
    )
)

; (:metric minimize (cost))
)
