;Header and description

(define (domain pacman)

; ; remove requirements that are not needed
; (:requirements :typing)

; (:types integer - number)

; (:constants childA childB - childType1 
; )

; (:constants width height - number)

(:predicates (connected ?pos1 ?pos2)
             (pacman-at ?pos)
             (is-home ?pos)
             (at-home)
             (food-at ?pos)
             (wall-at ?pos)
             (ghost-at ?pos)
             (scared-ghost-at ?pos)
)

; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here

(   :action move-normal
    :parameters (?pos ?npos)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (or
            (and
                (is-home ?pos)
                (is-home ?npos)
            )
            (and
                (not (is-home ?pos))
                (not (is-home ?npos))
            )
        )
        (not (wall-at ?npos))
        (not (ghost-at ?npos))
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (scared-ghost-at ?npos))
    )
)

(   :action move-from-home
    :parameters (?pos ?npos)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (and 
            (is-home ?pos)
            (not (is-home ?npos))
        )
        (not (is-home ?npos))
        (not (wall-at ?npos))
        (not (ghost-at ?npos))
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (scared-ghost-at ?npos))
        (not (at-home))
    )
)

(   :action move-to-home
    :parameters (?pos ?npos)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (and 
            (not (is-home ?pos))
            (is-home ?npos)
        )
        (not (wall-at ?npos))
        (not (ghost-at ?npos))
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (scared-ghost-at ?npos))
        (at-home)
    )
)


)