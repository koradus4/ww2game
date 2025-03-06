export interface Token {
    nation: string;           // nacja (np. "Polska")
    unit_type: string;        // typ jednostki (np. "P" dla piechoty)
    unit_size: string;        // rozmiar jednostki
    movement_points: number;   // punkty ruchu
    attack_range: number;     // zasięg ataku
    attack_value: number;     // wartość ataku
    combat_value: number;     // wartość bojowa
    supply_points: number;    // punkty zaopatrzenia
    selected_supports?: string[]; // wybrane wsparcia
    selected_transport?: string;  // wybrany transport
}

export interface TokenData {
    [key: string]: Token;
}