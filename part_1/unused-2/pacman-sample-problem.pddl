; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost, o: powercap
;   0 1 2 3
;   . x . g 0
;   p x   . 1
;   o x . . 2
;   . g   x 3 

(define (problem pacmanSample) (:domain pacman)
(:objects
    pos-0-0 pos-0-1 pos-0-2 pos-0-3
    pos-1-0 pos-1-1 pos-1-2 pos-1-3
    pos-2-0 pos-2-1 pos-2-2 pos-2-3
    pos-3-0 pos-3-1 pos-3-2 pos-3-3

    time-0 time-1 time-2 time-3
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

    (is-first-powered-step time-3)
    (is-last-powered-step time-0)

    (next-time time-3 time-2)
    (next-time time-2 time-1)
    (next-time time-1 time-0)

    (pacman-at pos-0-1)
    
    (ghost-at pos-3-0)
    (ghost-at pos-1-3)
    
    (powercap-at pos-0-2)
    
    (food-at pos-0-0)
    (food-at pos-2-0)
    (food-at pos-3-1)
    (food-at pos-2-2)
    (food-at pos-3-2)
    (food-at pos-0-3)
    
    (wall-at pos-1-0)
    (wall-at pos-1-1)
    (wall-at pos-1-2)
    (wall-at pos-3-3)
)

(:goal
    (and
        (not (food-at pos-0-0))
        (not (food-at pos-2-0))
        (not (food-at pos-3-1))
        (not (food-at pos-0-2))
        (not (food-at pos-2-2))
        (not (food-at pos-3-2))
        (not (food-at pos-0-3))
        (not (food-at pos-1-3))
    )
)

; (:metric minimize (cost))
)
