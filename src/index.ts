import { Gra } from './mechanika/gra';

const gra = new Gra();
gra.start().catch((error: Error) => {
    console.error('Błąd podczas uruchamiania gry:', error.message);
    process.exit(1);
});