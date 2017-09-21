;Header and description

(define (domain pacman)

; ; remove requirements that are not needed
; (:requirements :strips :fluents :durative-actions :timed-initial-literals :typing :conditional-effects :negative-preconditions :duration-inequalities)
(:requirements :equality)

; (:types childType1 childType2 - parentType)

; (:constants childA childB - childType1 
; )

(:predicates (pacman-at ?x ?y)
             (food-at ?x ?y)
             (wall-at ?x ?y)
             (ghost-at ?x ?y)
)


; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here
(:action move
 :parameters (?x ?y ?nx ?ny)
 :precondition (and
    (pacman-at (?x ?y))
    (not (wall-at ?nx ?ny))
    (not (ghost-at ?nx ?ny))
    (=
        (+
            (abs (- ?x ?nx))
            (abs (- ?y ?ny))
        1
        )
    )
 )
 :effect (and
    (not pacman-at (?x ?y))
    (pacman-at (?nx ?ny))
    (not food-at (?nx ?ny))
 )
)


)