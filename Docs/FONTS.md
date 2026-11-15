# Beatch Slash! — Font e identità tipografica

## Font scelti

- **Luckiest Guy** — Font principale per logo, titoli e annunci. Stile fumettistico, arcade, dinamico e ironico.
- **Fredoka** — Font principale per l'interfaccia di gioco. Stile arrotondato, morbido e leggibile, coerente con i personaggi chibi.

Entrambi sono disponibili gratuitamente su Google Fonts e utilizzabili commercialmente.

## Utilizzo dei font

| Elemento | Font | Dimensione indicativa (1080p) |
|---|---|---|
| Logo principale | Luckiest Guy personalizzato | — |
| Titoli delle schermate | Luckiest Guy | 48–64 px |
| GAME OVER | Luckiest Guy | 80–100 px |
| Annuncio nuova ondata | Luckiest Guy | 48–64 px |
| Pulsanti del menu | Fredoka SemiBold | 28–36 px |
| HUD e contatori | Fredoka Bold | 22–28 px |
| Descrizioni degli oggetti | Fredoka Regular | 20–24 px |
| Tutorial e dialoghi | Fredoka Medium | 20–26 px |

## Logo e titolo del gioco

Il logo **Beatch Slash!** deve utilizzare Luckiest Guy come base per un lettering personalizzato, coerente con lo stile della copertina e dei concept dei personaggi.

| Elemento | Specifica grafica |
|---|---|
| BEATCH | Giallo sabbia con riflessi crema |
| SLASH! | Rosso corallo, leggermente più grande |
| Contorno | Marrone scurissimo `#3A1418` |
| Ombreggiatura | Tonalità calde, terracotta |
| Composizione | Due righe, leggermente inclinate |
| Decorazioni | Granelli di sabbia ed effetti fumettistici |

Il logo deve sembrare parte integrante dell'illustrazione, non un semplice testo sovrapposto.

## Integrazione in Godot 4

- Creare un `Theme` condiviso per tutta l'interfaccia.
- Impostare Fredoka come font predefinito del tema.
- Utilizzare Luckiest Guy per titoli e annunci attraverso le variazioni del tema o gli override dei singoli nodi.
- Adattare le dimensioni indicate alla risoluzione effettiva dell'interfaccia.
- Mantenere la palette grafica del progetto: sabbia, terracotta, rosso corallo, azzurro e verde smeraldo.
- Conservare le licenze dei font all'interno del progetto e della distribuzione.

## Valori applicati nel gioco

La risoluzione logica è 1152×648. Le dimensioni qui sotto sono pixel logici: crescono proporzionalmente con la finestra, mantenendo la stessa visuale. Le misure indicative a 1080p sopra restano il riferimento di stile, non valori da copiare nei nodi.

| Uso | Font e peso | Dimensione logica |
|---|---|---|
| Titolo menu, Opzioni, Pausa | Luckiest Guy | 48 |
| Game Over | Luckiest Guy | 64 |
| Conto alla rovescia e titolo negozio | Luckiest Guy | 32 |
| Pulsanti | Fredoka SemiBold 600 | 26 |
| Tab del negozio | Fredoka SemiBold 600 | 22 |
| HUD | Fredoka Bold 700 | 20 |
| Tutorial | Fredoka Medium 500 | 20 |
| Invito al negozio | Fredoka SemiBold 600 | 20 |
| Nomi oggetti | Fredoka SemiBold 600 | 18 |
| Descrizioni nelle schede da 200 px | Fredoka Regular 400 | 16 |
| Testi generici | Fredoka Regular 400 | 20 |

Tema globale: `Assets/UI/game_theme.tres`, assegnato da `gui/theme/custom` in `project.godot`. Le scene scelgono il ruolo con `theme_type_variation`; i pesi sono FontVariation del singolo Fredoka variabile. Il lettering illustrato del logo rimane una risorsa distinta dal titolo testuale del menu.

Font originali: `Assets/Fonts/LuckiestGuy-Regular.ttf` e `Assets/Fonts/Fredoka.ttf`. Licenze originali in `Assets/Fonts/Licenses/`: **Apache 2.0 per Luckiest Guy**, **OFL per Fredoka**. I tre preset di esportazione includono esplicitamente `Assets/Fonts/Licenses/*.txt`.

## Riferimenti ufficiali

- Luckiest Guy: https://fonts.google.com/specimen/Luckiest+Guy
- Fredoka: https://fonts.google.com/specimen/Fredoka
- Sorgenti e licenza Luckiest Guy: https://github.com/google/fonts/tree/main/apache/luckiestguy
- Sorgenti e licenza Fredoka: https://github.com/google/fonts/tree/main/ofl/fredoka
