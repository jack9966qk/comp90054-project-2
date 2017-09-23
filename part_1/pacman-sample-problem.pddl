; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost, s: scared ghost
;   0 1 2 3 | 4 5 6 7
;   . x . g | x   x   0
;     x   . | x       1
;   . x . . |         2
;   . s   x | x     p 3 

(define (problem pacmanSample) (:domain pacman)
(:objects
    pos-0-0 pos-0-1 pos-0-2 pos-0-3
    pos-1-0 pos-1-1 pos-1-2 pos-1-3
    pos-2-0 pos-2-1 pos-2-2 pos-2-3
    pos-3-0 pos-3-1 pos-3-2 pos-3-3
    pos-4-0 pos-4-1 pos-4-2 pos-4-3
    pos-5-0 pos-5-1 pos-5-2 pos-5-3
    pos-6-0 pos-6-1 pos-6-2 pos-6-3
    pos-7-0 pos-7-1 pos-7-2 pos-7-3
)

(:init
    (connected pos-0-0 pos-1-0)
    (connected pos-0-0 pos-0-1)
    (connected pos-0-1 pos-1-1)
    (connected pos-0-1 pos-0-2)
    (connected pos-0-2 pos-1-2)
    (connected pos-0-2 pos-0-3)
    (connected pos-0-3 pos-1-3)
    (connected pos-1-0 pos-2-0)
    (connected pos-1-0 pos-1-1)
    (connected pos-1-1 pos-2-1)
    (connected pos-1-1 pos-1-2)
    (connected pos-1-2 pos-2-2)
    (connected pos-1-2 pos-1-3)
    (connected pos-1-3 pos-2-3)
    (connected pos-2-0 pos-3-0)
    (connected pos-2-0 pos-2-1)
    (connected pos-2-1 pos-3-1)
    (connected pos-2-1 pos-2-2)
    (connected pos-2-2 pos-3-2)
    (connected pos-2-2 pos-2-3)
    (connected pos-2-3 pos-3-3)
    (connected pos-3-0 pos-4-0)
    (connected pos-3-0 pos-3-1)
    (connected pos-3-1 pos-4-1)
    (connected pos-3-1 pos-3-2)
    (connected pos-3-2 pos-4-2)
    (connected pos-3-2 pos-3-3)
    (connected pos-3-3 pos-4-3)
    (connected pos-4-0 pos-5-0)
    (connected pos-4-0 pos-4-1)
    (connected pos-4-1 pos-5-1)
    (connected pos-4-1 pos-4-2)
    (connected pos-4-2 pos-5-2)
    (connected pos-4-2 pos-4-3)
    (connected pos-4-3 pos-5-3)
    (connected pos-5-0 pos-6-0)
    (connected pos-5-0 pos-5-1)
    (connected pos-5-1 pos-6-1)
    (connected pos-5-1 pos-5-2)
    (connected pos-5-2 pos-6-2)
    (connected pos-5-2 pos-5-3)
    (connected pos-5-3 pos-6-3)
    (connected pos-6-0 pos-7-0)
    (connected pos-6-0 pos-6-1)
    (connected pos-6-1 pos-7-1)
    (connected pos-6-1 pos-6-2)
    (connected pos-6-2 pos-7-2)
    (connected pos-6-2 pos-6-3)
    (connected pos-6-3 pos-7-3)
    (connected pos-7-0 pos-7-1)
    (connected pos-7-1 pos-7-2)
    (connected pos-7-2 pos-7-3)


    (is-home pos-4-0)
    (is-home pos-4-1)
    (is-home pos-4-2)
    (is-home pos-4-3)
    (is-home pos-5-0)
    (is-home pos-5-1)
    (is-home pos-5-2)
    (is-home pos-5-3)
    (is-home pos-6-0)
    (is-home pos-6-1)
    (is-home pos-6-2)
    (is-home pos-6-3)
    (is-home pos-7-0)
    (is-home pos-7-1)
    (is-home pos-7-2)
    (is-home pos-7-3)

    (pacman-at pos-7-3)
    
    (ghost-at pos-3-0)
    (scared-ghost-at pos-1-3)
    
    
    (food-at pos-0-0)
    (food-at pos-2-0)
    (food-at pos-3-1)
    (food-at pos-2-2)
    (food-at pos-3-2)
    (food-at pos-0-2)
    (food-at pos-0-3)
    
    (wall-at pos-1-0)
    (wall-at pos-1-1)
    (wall-at pos-1-2)
    (wall-at pos-3-3)
    (wall-at pos-4-0)
    (wall-at pos-6-0)
    (wall-at pos-4-1)
    (wall-at pos-4-3)
)

(:goal
    (and
        (not (food-at pos-0-0))
        (not (food-at pos-2-0))
        (not (food-at pos-3-1))
        (not (food-at pos-2-2))
        (not (food-at pos-3-2))
        (not (food-at pos-0-2))
        (not (food-at pos-0-3))
        (at-home)
    )
)

; (:metric minimize (cost))
)
