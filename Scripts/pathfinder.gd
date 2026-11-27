class_name Pathfinder
extends Node
## Griglia A* con gli ostacoli statici (TileMap, negozio) per far aggirare gli ostacoli alle nemiche.
## Le altre nemiche non sono nella griglia: le evita enemy.gd con la separazione.

const CELL_SIZE := 40
const MARGIN := 400.0
## Ingombro del collider della nemica (enemy.tscn): la cella è bloccata se lì toccherebbe un ostacolo.
const PROBE_SIZE := Vector2(56, 48)
const PROBE_OFFSET := Vector2(0, 52)
const FREE_CELL_SEARCH_RADIUS := 8
## Un corpo fermo (nemica che attacca, Player) blocca per questo percorso le celle entro questo raggio dal suo centro.
const BLOCKER_RADIUS := 80.0
## Partenza dentro una cella bloccata: si provano le REACH_CANDIDATES celle libere più vicine, controllando il passaggio ogni REACH_STEP px
## con l'ingombro ridotto di REACH_SHRINK (un corpo appoggiato a un ostacolo lo sfiora senza compenetrarlo).
const REACH_CANDIDATES := 12
const REACH_STEP := 10.0
const REACH_SHRINK := 4.0
## Taglio del percorso: la nemica cambia waypoint a WAYPOINT_RADIUS (30 px) e non segue la linea con precisione, quindi il taglio
## deve passare con questo margine in più (px sull'ingombro) attorno agli ostacoli, non solo a filo.
const SMOOTH_MARGIN := 24.0

var grid := AStarGrid2D.new()
var _reach_queries := {}   # sonde dell'ingombro della nemica per margine (negativo = più stretta, positivo = più larga), create alla prima richiesta
var built := false

## Costruisce la griglia su `bounds` (coordinate globali). Fino alla fine `find_path` restituisce un percorso vuoto.
func build(bounds: Rect2) -> void:
	# I collider del TileMap entrano nello spazio fisico dopo il primo frame fisico.
	await get_tree().physics_frame
	await get_tree().physics_frame
	var region := bounds.grow(MARGIN)
	grid.region = Rect2i(Vector2i((region.position / CELL_SIZE).floor()), Vector2i((region.size / CELL_SIZE).ceil()))
	grid.cell_size = Vector2(CELL_SIZE, CELL_SIZE)
	grid.offset = grid.cell_size / 2.0
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	grid.update()

	var space := get_viewport().world_2d.direct_space_state
	var probe := RectangleShape2D.new()
	probe.size = PROBE_SIZE
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = probe
	for x in range(grid.region.position.x, grid.region.end.x):
		for y in range(grid.region.position.y, grid.region.end.y):
			var id := Vector2i(x, y)
			query.transform = Transform2D(0.0, grid.get_point_position(id) + PROBE_OFFSET)
			for hit in space.intersect_shape(query, 8):
				if not hit.collider is CharacterBody2D:
					grid.set_point_solid(id)
					break
	built = true

## Punti da seguire per andare da `from` a `to` (senza il punto di partenza). Vuoto se la griglia non è pronta o non c'è strada.
## `blockers`: posizioni di corpi fermi da aggirare, valide solo per questa ricerca.
func find_path(from: Vector2, to: Vector2, blockers := PackedVector2Array()) -> PackedVector2Array:
	if not built:
		return PackedVector2Array()
	var blocked: Array[Vector2i] = []
	var reach := ceili(BLOCKER_RADIUS / CELL_SIZE)
	for b in blockers:
		var center := _cell_of(b)
		for x in range(center.x - reach, center.x + reach + 1):
			for y in range(center.y - reach, center.y + reach + 1):
				var cell := Vector2i(x, y)
				if grid.is_in_boundsv(cell) and not grid.is_point_solid(cell) and grid.get_point_position(cell).distance_to(b) <= BLOCKER_RADIUS:
					grid.set_point_solid(cell)
					blocked.append(cell)
	var start := _start_cell(from)
	var goal := _nearest_free(_cell_of(to))
	var result := _smooth(from, grid.get_point_path(start, goal, true))
	for cell in blocked:
		grid.set_point_solid(cell, false)
	return result

func _cell_of(point: Vector2) -> Vector2i:
	return Vector2i((point / CELL_SIZE).floor())

## Cella da cui parte il percorso: la propria se libera. Un corpo appoggiato a un ostacolo può trovarsi in una cella che la griglia dà per
## bloccata (la griglia è a passo 40, il collider no): allora serve la cella libera più vicina che il corpo raggiunge in linea retta, non
## quella dall'altra parte dell'ostacolo (la nemica ci si schiaccerebbe contro).
func _start_cell(from: Vector2) -> Vector2i:
	var cell := _cell_of(from).clamp(grid.region.position, grid.region.end - Vector2i.ONE)
	if not grid.is_point_solid(cell):
		return cell
	var candidates: Array[Vector2i] = []
	for dx in range(-FREE_CELL_SEARCH_RADIUS, FREE_CELL_SEARCH_RADIUS + 1):
		for dy in range(-FREE_CELL_SEARCH_RADIUS, FREE_CELL_SEARCH_RADIUS + 1):
			var candidate := cell + Vector2i(dx, dy)
			if grid.is_in_boundsv(candidate) and not grid.is_point_solid(candidate):
				candidates.append(candidate)
	candidates.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return grid.get_point_position(a).distance_squared_to(from) < grid.get_point_position(b).distance_squared_to(from))
	for candidate in candidates.slice(0, REACH_CANDIDATES):
		if _can_walk(from, grid.get_point_position(candidate)):
			return candidate
	return _nearest_free(cell)

## Il corpo della nemica va da `from` a `to` in linea retta senza toccare ostacoli (come in `build`: i CharacterBody2D non contano).
func _can_walk(from: Vector2, to: Vector2, margin := -REACH_SHRINK) -> bool:
	var space := get_viewport().world_2d.direct_space_state
	if not _reach_queries.has(margin):
		var probe := RectangleShape2D.new()
		probe.size = PROBE_SIZE + Vector2.ONE * margin
		var made := PhysicsShapeQueryParameters2D.new()
		made.shape = probe
		_reach_queries[margin] = made
	var query: PhysicsShapeQueryParameters2D = _reach_queries[margin]
	var steps := maxi(ceili(from.distance_to(to) / REACH_STEP), 1)
	for s in range(steps + 1):
		query.transform = Transform2D(0.0, from.lerp(to, float(s) / steps) + PROBE_OFFSET)
		for hit in space.intersect_shape(query, 8):
			if not hit.collider is CharacterBody2D:
				return false
	return true

## Cella libera più vicina (anelli concentrici); se l'area è tutta bloccata restituisce la cella data.
func _nearest_free(cell: Vector2i) -> Vector2i:
	cell = cell.clamp(grid.region.position, grid.region.end - Vector2i.ONE)
	for r in range(FREE_CELL_SEARCH_RADIUS + 1):
		for dx in range(-r, r + 1):
			for dy in range(-r, r + 1):
				if maxi(absi(dx), absi(dy)) != r:
					continue
				var candidate := cell + Vector2i(dx, dy)
				if grid.is_in_boundsv(candidate) and not grid.is_point_solid(candidate):
					return candidate
	return cell

## Toglie i punti intermedi: da ogni punto va diritto al più lontano raggiungibile in linea retta. La griglia a passo 40 lascia passare
## tagli che il corpo (56 px) non riesce a fare (corridoi stretti tra un prop e l'altro): il taglio va confermato anche con la fisica.
func _smooth(from: Vector2, points: PackedVector2Array) -> PackedVector2Array:
	var result := PackedVector2Array()
	var current := from
	var i := 0
	while i < points.size():
		var far := i
		for j in range(points.size() - 1, i, -1):
			if _is_clear(current, points[j]) and _can_walk(current, points[j], SMOOTH_MARGIN):
				far = j
				break
		result.append(points[far])
		current = points[far]
		i = far + 1
	return result

func _is_clear(a: Vector2, b: Vector2) -> bool:
	var steps := ceili(a.distance_to(b) / (CELL_SIZE * 0.5))
	for s in range(1, steps + 1):
		var id := _cell_of(a.lerp(b, float(s) / steps))
		if not grid.is_in_boundsv(id) or grid.is_point_solid(id):
			return false
	return true
