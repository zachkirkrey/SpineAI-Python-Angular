import { animate, style, transition, trigger } from '@angular/animations';

export const fadeInAndOut = trigger("fadeInAndOut", [
    transition(":enter", [
        style({ opacity: 0 }),
        animate("0.123s ease-out", style({ opacity: 1 }))
    ]),
    transition(":leave", [
        animate("0.123s ease-out", style({ opacity: 0 }))
    ]),
]);