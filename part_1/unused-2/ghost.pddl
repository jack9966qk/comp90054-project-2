;Header and description

(define (domain ghost)

; ; remove requirements that are not needed
; (:requirements :typing)

; (:types integer - number)

; (:constants childA childB - childType1 
; )

; (:constants width height - number)

(:predicates (adjcent ?pos1 ?pos2)
             (same ?pos1 ?pos2)
             (pacman-at ?posx ?posy)
             (wall-at ?posx ?posy)
             (ghost-at ?posx ?posy)
)

; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here

(   :action move
    :parameters (?fromx ?fromy ?tox ?toy)
    :precondition (and
        (ghost-at ?fromx ?fromy)
        (or
            (and
                (adjcent ?fromx ?tox)
                (same ?fromy ?toy)
            )
            (and
                (adjcent ?tox ?fromx)
                (same ?fromy ?toy)
            )
            (and
                (adjcent ?fromy ?toy)
                (same ?fromx ?tox)
            )
            (and
                (adjcent ?toy ?fromy)
                (same ?fromx ?tox)
            )
        )
        (not (wall-at ?tox ?toy))
    )
    :effect (and
        (not (ghost-at ?fromx ?fromy))
        (ghost-at ?tox ?toy)
        (not (pacman-at ?tox ?toy))
    )
)

)