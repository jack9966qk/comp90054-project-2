;Header and description

(define (domain pacman)

; ; remove requirements that are not needed
(:requirements :typing :equality)

(:types integer - number)

; (:constants childA childB - childType1 
; )

(:constants width height - number)

(:predicates (pacman-at ?x ?y)
             (food-at ?x ?y)
             (wall-at ?x ?y)
             (ghost-at ?x ?y)
)


; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here
; (:action move
;  :parameters (?x ?y ?nx ?ny)
;  :precondition (and
;     (pacman-at (?x ?y))
;     (not (wall-at ?nx ?ny))
;     (not (ghost-at ?nx ?ny))
;     (=
;         (+
;             (abs (- ?x ?nx))
;             (abs (- ?y ?ny))
;         1
;         )
;     )
;  )
;  :effect (and
;     (not pacman-at (?x ?y))
;     (pacman-at (?nx ?ny))
;     (not food-at (?nx ?ny))
;  )
; )


(   :action move-north
    :parameters (?x ?y)
    :precondition (and
        (pacman-at ?x ?y)
        (<= (+ ?y 1) height)
        (not (wall-at ?x (+ ?y 1)))
        (not (ghost-at ?x (+ ?y 1)))
    )

    :effect (and
        (not (pacman-at ?x ?y))
        (pacman-at ?x (+ ?y 1))
        (not (food-at ?x (+ ?y 1)))
    )
)

(   :action move-south
    :parameters (?x ?y)
    :precondition (and
        (pacman-at ?x ?y)
        (>= (- ?y 1) 0)
        (not (wall-at ?x (+ ?y 1)))
        (not (ghost-at ?x (+ ?y 1)))
    )

    :effect (and
        (not (pacman-at ?x ?y))
        (pacman-at ?x (- ?y 1))
        (not (food-at ?x (- ?y 1)))
    )
)

(   :action move-east
    :parameters (?x ?y)
    :precondition (and
        (pacman-at ?x ?y)
        (<= (+ ?x 1) width)
        (not (wall-at (+ ?x 1) ?y))
        (not (ghost-at (+ ?x 1) ?y))
    )

    :effect (and
        (not (pacman-at ?x ?y))
        (pacman-at (+ ?x 1) ?y)
        (not (food-at (+ ?x 1) ?y))
    )
)

(   :action move-west
    :parameters (?x ?y)
    :precondition (and
        (pacman-at ?x ?y)
        (>= (- ?x 1) 0)
        (not (wall-at (- ?x 1) ?y))
        (not (ghost-at (- ?x 1) ?y))
    )

    :effect (and
        (not (pacman-at ?x ?y))
        (pacman-at (- ?x 1) ?y)
        (not (food-at (- ?x 1) ?y))
    )
)

)