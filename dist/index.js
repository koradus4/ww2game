"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const gra_1 = require("./mechanika/gra");
const gra = new gra_1.Gra();
gra.start().catch((error) => {
    console.error('Błąd podczas uruchamiania gry:', error.message);
    process.exit(1);
});
