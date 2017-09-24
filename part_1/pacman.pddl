;Header and description

(define (domain pacman)

; ; remove requirements that are not needed
; (:requirements :typing)

; (:types integer - number)

; (:constants childA childB - childType1 
; )

; (:constants width height - number)

(:predicates (adjcent ?pos1 ?pos2)
             (same ?pos1 ?pos2)
             (pacman-at ?fromx ?fromy)
             (is-home ?pos)
             (at-home)
             (food-at ?posx ?posy)
             (wall-at ?posx ?posy)
             (ghost-at ?posx ?posy)
             (scared-ghost-at ?posx ?posy)
)

; (:functions (function1 ?c - childType2)
;             (cost)
; )

;define actions here

(   :action move-to-home
    :parameters (?fromx ?fromy ?tox ?toy)
    :precondition (and
        (pacman-at ?fromx ?fromy)
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
        (is-home ?tox)
        (not (wall-at ?tox ?toy))
        (not (ghost-at ?tox ?toy))
    )
    :effect (and
        (not (pacman-at ?fromx ?fromy))
        (pacman-at ?tox ?toy)
        (not (food-at ?tox ?toy))
        (not (scared-ghost-at ?tox ?toy))
        (at-home)
    )
)

(   :action move-to-not-home
    :parameters (?fromx ?fromy ?tox ?toy)
    :precondition (and
        (pacman-at ?fromx ?fromy)
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
        (not (is-home ?tox))
        (not (wall-at ?tox ?toy))
        (not (ghost-at ?tox ?toy))
    )
    :effect (and
        (not (pacman-at ?fromx ?fromy))
        (pacman-at ?tox ?toy)
        (not (food-at ?tox ?toy))
        (not (scared-ghost-at ?tox ?toy))
        (not (at-home))
    )
)


)