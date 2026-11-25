# Piano di lavoro: pacchetti di ripristino e righe con icona nel negozio

File di lavoro per Claude Code e Codex. **Lo elimina solo l'utente**, quando lo dice lui. Non è un file di contesto: può contenere stato e storico del lavoro. Il funzionamento approvato va poi riscritto in `PROJECT_CONTEXT.md` e `CODE_MAP.md` secondo le regole di `AGENTS.md`.

Prima di lavorare leggi: `AGENTS.md`, `Docs/CODE_MAP.md` (sezione 15, negozio e oggetti), `Docs/PROJECT_CONTEXT.md` (sezione 4), la skill `game-tools` e, per l'icona, `Docs/GIMP.md` con la guida generica `references/gimp.md`. Le funzioni di `upgrades_purchase.gd` e `boyfriend.gd:_apply_bonus` vanno lette per intero prima di toccarle.

## Indice

1. [Obiettivo](#1-obiettivo)
2. [Decisioni dell'utente](#2-decisioni-dellutente)
3. [Scelte dell'agente](#3-scelte-dellagente)
4. [Compiti](#4-compiti)
5. [Stato di avanzamento](#5-stato-di-avanzamento)

## 1. Obiettivo

Aggiungere tre oggetti che ripristinano insieme moralità e fedeltà, pensati come ricompensa per chi resiste alle ondate difficili, e riorganizzare il pannello del negozio in righe con un'icona a inizio riga.

## 2. Decisioni dell'utente

- **I tagli dei ripristino restano 25% / 50% / 100%.** Non esiste il 75%. I prezzi dei singoli non cambiano (30 / 50 / 90¢ per moralità e per fedeltà): seguono già la logica degli abbonamenti (il 50% costa meno di due 25%, il 100% meno di quattro).
- **Tre pacchetti "Entrambi"**, più cari della somma dei due singoli dello stesso taglio, come ricompensa:

| Nome | Effetto | Prezzo base | Somma dei singoli | Disponibilità |
| --- | --- | --- | --- | --- |
| Acqua Tonica alla Menta | 25% di moralità e di fedeltà | 70¢ | 60¢ | pause dopo ondate multiple di 5 |
| Granita al Limone Aromatizzata | 50% di entrambe | 120¢ | 100¢ | pause dopo ondate multiple di 5 |
| Frullato Frutti di Bosco e Fragola | 100% di entrambe | 240¢ | 180¢ | pause dopo ondate multiple di 5, dalla pausa dopo l'ondata 10 |

  Immaginario dei nomi: l'acqua tonica con la menta è un mojito; la granita al limone ha un aroma di rosmarino (pezzetti di rosmarino tritato fine); il frullato unisce quello ai frutti di bosco e quello alla fragola. Il +25% ogni 5 ondate vale come per tutti gli oggetti senza massimo.
- **Pannello:** una sola sezione "Moralità e Fedeltà" al posto delle due attuali, con tre gruppi su righe separate (moralità, fedeltà, entrambi). Niente titoli di sottosezione: un separatore sottile tra i gruppi e, a inizio di ogni riga, un'icona.
- **Icona di riga** a inizio riga: scudo per la moralità, cuore per la fedeltà, per "entrambi" una nuova icona con scudo e cuore in diagonale (scudo in alto a sinistra, cuore in basso a destra, l'angolo in basso a destra dello scudo leggermente sovrapposto all'angolo in alto a sinistra del cuore), creata in GIMP dalle icone esistenti, rimpicciolite, e salvata con la stessa dimensione di tutte le altre icone (1254×1254).
- **Il meccanismo dell'icona di riga è generico**: serve anche per le altre righe del negozio in futuro. Dove non c'è ancora un'icona di riga, **segnaposto**.
- **Icone dei tre pacchetti e delle righe Giocatore e Bonus:** generate da Codex (`mint_tonic_water.png`, `herbed_lemon_granita.png`, `berry_strawberry_smoothie.png`, `row_player.png`, `row_bonus.png`) e inserite nel pannello.

## 3. Scelte dell'agente

Da correggere se non vanno bene.

- Ogni gruppo (riga) del pannello è un `HBoxContainer` con l'icona di riga a sinistra e la griglia a 3 colonne a destra; un gruppo con più di 3 oggetti prende più righe di griglia (moralità e fedeltà: 3 ripristini, una protezione massima e un oggetto temporaneo, cioè 5 oggetti su 2 righe di griglia).
- Le schede Giocatore e Bonus restano una sola griglia senza titolo, ma con l'icona di riga (palla di sabbia, regalo) a inizio riga.
- Segnaposto: `res://Assets/icon.svg`.
- File dell'icona doppia: `Assets/Icons/shield_health.png`; sorgente a livelli in `Tools/gimp/shield_health.xcf`.
- Sub-categoria dei pacchetti nel catalogo: `Both` (categoria `Target`, effetto `restore`).

## 4. Compiti

- [x] **4.1 Catalogo.** Tre righe in `Files/item_list.csv`: `little_both`, `medium_both`, `large_both`; `Target`, sub-categoria `Both`, `restore`, `bonus` 0,25 / 0,5 / 1, `order` 0 / 1 / 2, prezzi 70 / 120 / 240, `max_purchases` 0, `every` 5, `min_wave` 0 / 0 / 10, `cooldown` 0, descrizioni "Ripristina il N% di moralità e fedeltà del tuo partner", `image` segnaposto. Il separatore è `;`, la riga vuota finale resta.
- [x] **4.2 Effetto.** `boyfriend.gd:_apply_bonus`: caso `["restore", "Both"]` che ripristina `max_shield * bonus` e `max_hp * bonus` con i tetti dei massimi. `upgrades_purchase.gd:_is_useless`: un `restore` `Both` è inutile solo se moralità e fedeltà sono entrambe piene.
- [x] **4.3 Pannello.** `upgrades_purchase.gd`: sezione unica "Moralità e Fedeltà" con tre gruppi (Shield, Health, Both) in righe separate, separatore sottile tra i gruppi, icona a inizio riga da una tabella chiave → file (scudo, cuore, icona doppia; segnaposto per Giocatore e Bonus). Controllare che i nomi lunghi dei pacchetti stiano nella scheda (larghezza minima 240).
- [x] **4.4 Icona doppia.** In GIMP (guide lette prima), dalle icone `shield.png` e `health.png`: rimpicciolite, in diagonale, sovrapposizione leggera come da decisione, livelli separati, tela 1254×1254 trasparente, esportazione in `Assets/Icons/shield_health.png`, sorgente `Tools/gimp/shield_health.xcf`. Script generici nella libreria della skill, valori in una ricetta di `Tools/gimp/recipes/`. Mostrare l'anteprima all'utente.
- [x] **4.5 Prove.** Estendere `tests/test_shop_items.gd` (prezzi 70 / 120 / 240, sblocco del 100% dall'ondata 10, `every` 5, `Both` inutile solo con barre piene). In gioco: screenshot del pannello (sezione unica, tre righe, separatori, icone, nomi che stanno nella scheda) e acquisto di prova di un pacchetto con entrambe le barre sotto il massimo. Scenario di debug temporaneo, poi ripulito.
- [x] **4.6 Documenti e guide.** `PROJECT_CONTEXT.md` (sezione 4: tabella e regole; sezione 10: il punto passa tra gli approvati dopo il via libera), `CODE_MAP.md` (sezione 15 e test), `Docs/GIMP.md` e `references/gimp.md` della skill per quanto imparato.

## 5. Stato di avanzamento

Compiti 4.1–4.5 fatti: catalogo (3 pacchetti), effetto `Both` con numeri fluttuanti affiancati, pannello a sezione unica con righe, separatori e icone di riga (le cinque icone generate da Codex inserite e verificate in gioco nei tre tab), icona doppia `shield_health.png` creata in GIMP, test `shop_items` 8/8 e prova in gioco (acquisto del 100% con barre a 20 e 30: tornano a 100, il pacchetto diventa inutile). Su richiesta dell'utente le schede sono più piccole (larghezza minima 190, immagine 38, testo 13/11, pulsante 26) e l'icona di riga è centrata in verticale. Compito 4.6 (documenti e guide) fatto. In attesa dell'approvazione dell'utente dopo il playtest.
