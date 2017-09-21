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
             (powered)
             (is-last-powered-step ?time)
             (is-first-powered-step ?time)
             (time-at ?time)
             (next-time ?time ?time2)
             (food-at ?pos)
             (powercap-at ?pos)
             (wall-at ?pos)
             (ghost-at ?pos)
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
        (not (wall-at ?npos))
        (not (ghost-at ?npos))
        (not (powercap-at ?npos))
        (not (powered))
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
    )
)

(   :action move-eat-power
    :parameters (?pos ?npos ?time)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (not (wall-at ?npos))
        (not (ghost-at ?npos))
        (is-first-powered-step ?time)
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (powercap-at ?npos))
        (powered)
        (time-at ?time)
    )
)

(   :action move-powered
    :parameters (?pos ?npos ?time ?ntime)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (not (wall-at ?npos))
        (time-at ?time)
        (next-time ?time ?ntime)
        (powered)
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (powercap-at ?npos))
        (not (ghost-at ?npos))
        (not (time-at ?time))
        (time-at ?ntime)
    )
)

(   :action move-powered-last-step
    :parameters (?pos ?npos ?time)
    :precondition (and
        (pacman-at ?pos)
        (or 
            (connected ?pos ?npos)
            (connected ?npos ?pos)
        )
        (not (wall-at ?npos))
        (time-at ?time)
        (is-last-powered-step ?time)
        (powered)
    )
    :effect (and
        (not (pacman-at ?pos))
        (pacman-at ?npos)
        (not (food-at ?npos))
        (not (powercap-at ?npos))
        (not (ghost-at ?npos))
        (not (time-at ?time))
        (not (powered))
    )
)


)