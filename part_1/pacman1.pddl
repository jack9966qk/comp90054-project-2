;Header and description

(define (domain pacman)

; ; remove requirements that are not needed
; (:requirements :typing)

; (:types integer - number)

; (:constants childA childB - childType1 
; )

; (:constants width height - number)

(:predicates (is-next ?pos ?pos)
             (is-same ?pos ?pos)
             (pacman-at ?fromx ?fromy)
             (is-home ?posx)
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
                (is-next ?fromx ?tox)
                (is-same ?fromy ?toy)
            )
            (and
                (is-next ?tox ?fromx)
                (is-same ?fromy ?toy)
            )
            (and
                (is-next ?fromy ?toy)
                (is-same ?fromx ?tox)
            )
            (and
                (is-next ?toy ?fromy)
                (is-same ?fromx ?tox)
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
                (is-next ?fromx ?tox)
                (is-same ?fromy ?toy)
            )
            (and
                (is-next ?tox ?fromx)
                (is-same ?fromy ?toy)
            )
            (and
                (is-next ?fromy ?toy)
                (is-same ?fromx ?tox)
            )
            (and
                (is-next ?toy ?fromy)
                (is-same ?fromx ?tox)
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