; 4x4 sized maze
; p: pacman, x: wall, .: food, g: ghost, s: scared ghost
;   0 1 2 3 | 4 5 6 7
;   . x . g | x   x   0
;     x   . | x       1
;   . x . . |         2
;   . s   x | x     p 3 

(define (problem pacmanSample) (:domain pacman)
(:objects
    posx-0
    posx-1
    posx-2
    posx-3
    posx-4
    posx-5
    posx-6
    posx-7
    
    posy-0
    posy-1
    posy-2
    posy-3
)

(:init
    (is-next posx-0 posx-1)
    (is-next posx-1 posx-2)
    (is-next posx-2 posx-3)
    (is-next posx-3 posx-4)
    (is-next posx-4 posx-5)
    (is-next posx-5 posx-6)
    (is-next posx-6 posx-7)
    
    (is-next posy-0 posy-1)
    (is-next posy-1 posy-2)
    (is-next posy-2 posy-3)
    
    (is-same posx-0 posx-0)
    (is-same posx-1 posx-1)
    (is-same posx-2 posx-2)
    (is-same posx-3 posx-3)
    (is-same posx-4 posx-4)
    (is-same posx-5 posx-5)
    (is-same posx-6 posx-6)
    (is-same posx-7 posx-7)
    
    (is-same posy-0 posy-0)
    (is-same posy-1 posy-1)
    (is-same posy-2 posy-2)
    (is-same posy-3 posy-3)
    
    (wall-at posx-1 posy-0)
    (wall-at posx-1 posy-1)
    (wall-at posx-1 posy-2)
    (wall-at posx-3 posy-3)
    (wall-at posx-4 posy-0)
    (wall-at posx-4 posy-1)
    (wall-at posx-4 posy-3)
    (wall-at posx-6 posy-0)
    
    (is-home posx-0)
    (is-home posx-1)
    (is-home posx-2)
    (is-home posx-3)

    (pacman-at posx-7 posy-3)
    
    (ghost-at posx-3 posy-0)
    (scared-ghost-at posx-1 posy-3)
    
    
    (food-at posx-0 posy-0)
    (food-at posx-2 posy-0)
    (food-at posx-3 posy-1)
    (food-at posx-2 posy-2)
    (food-at posx-3 posy-2)
    (food-at posx-0 posy-2)
    (food-at posx-0 posy-3)
    
)

(:goal
    (and
        (not (food-at posx-0 posy-0))
        (not (food-at posx-2 posy-0))
        (not (food-at posx-3 posy-1))
        (not (food-at posx-2 posy-2))
        (not (food-at posx-3 posy-2))
        (not (food-at posx-0 posy-2))
        (not (food-at posx-0 posy-3))
        (at-home)
    )
)

; (:metric minimize (cost))
)
