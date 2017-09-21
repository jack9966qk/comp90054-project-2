; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost
;   0 1 2 3
;   . x . g 0
;   p x   . 1
;   . x . . 2
;   . .   x 3 

(define (problem pacmanSample) (:domain pacman)
; (:objects
;     object11 object12 - childType1
;     object21 object22 - childType2
; )
(:init
    (pacman-at 0 1)
    (ghost-at 3 0)
    (food-at 0 0)
    (food-at 2 0)
    (food-at 3 1)
    (food-at 0 2)
    (food-at 2 2)
    (food-at 3 2)
    (food-at 0 3)
    (food-at 1 3)
    (wall-at 1 0)
    (wall-at 1 1)
    (wall-at 1 2)
    (wall-at 3 3)
)

(:goal
    (and
        (not (food-at 0 0))
        (not (food-at 2 0))
        (not (food-at 3 1))
        (not (food-at 0 2))
        (not (food-at 2 2))
        (not (food-at 3 2))
        (not (food-at 0 3))
        (not (food-at 1 3))
    )
)

; (:metric minimize (cost))
)
