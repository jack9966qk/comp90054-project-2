;Header and description

(define (domain ghost)

; ; remove requirements that are not needed
; (:requirements :typing)

; (:types integer - number)

; (:constants childA childB - childType1 
; )

; (:constants width height - number)

(:predicates (connected ?pos1 ?pos2)
             (pacman-at ?pos)
             (wall-at ?pos)
             (ghost-at ?pos)
)

; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here

(   :action move
    :parameters (?pos ?npos)
    :precondition (and
        (ghost-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (not (wall-at ?npos))
    )
    :effect (and
        (not (ghost-at ?pos))
        (ghost-at ?npos)
        (not (pacman-at ?npos))
    )
)

)