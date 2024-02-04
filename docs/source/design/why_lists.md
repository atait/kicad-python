# Why does v4.2 use generators but v5.0 uses lists?

## The change

### Works in both
Suppose you have one thing selected, you can get it like
```python
for sel in pcb.selected_items:
    break
```

### Works in v4 only
```python
sel = next(pcb.selected_items)
```

### Works in v5 only
```python
sel = pcb.selected_items[0]
```

### Common pattern
The most common pattern I see is doing something to all the elements. This pattern works in both unchanged
```python
thin_tracks = []
for track in pcb.tracks:
    if track.width < 1:
        thin_tracks.append(track)
```

## Upsides
The biggest upside is understandability. Python generators are an advanced concept that are not intuitive to beginners. They are also not intuitive to many experts.

Another upside is that lists can be iterated multiple times and indexed.  There are many cases where you do multiple operations, and indexing does make sense after the iteration order is fixed. For example
```python
all_tracks = pcb.tracks
thin_tracks = all_tracks[t.width < 1 for t in all_tracks]
```
is iterating over `all_tracks` to find where a condition is met. Then, it is logical indexing - O(1). If all_tracks is a list, we can ensure that the second indexing step will have the same order as the first iteration pass.

In my experience, any kind of chain of operations on item sequences is accomplished by converting the generator to a list anyways. Returning list avoids having to do this conversion, which looks weird.

New comprehensions, specifically `+`:
```python
nets = [t.net_name for t in pcb.tracks + pcb.vias + pcb.zones]
```
whereas before it would be more idiosyncratic
```python
nets = [t.net_name for t in itertools.chain(pcb.tracks, pcb.vias, pcb.zones)]
```

## Potential downsides
`kigadgets` is all about wrapping dynamic native objects and storing no additional state. Lists are a form of state: taking a non-guaranteed order and fixing its order. `BOARD.GetTracks` iteration order is not guaranteed, so there is an argument for discouraging the user from thinking about indexing. It is pretty elegant IMHO.
> This argument does not cover cases where there is a benefit to *temporarily* fixing iteration order.
> This ordering of the list itself is the only state introduced. The list elements are still dynamic objects that reflect live changes to the native items.

When something like `pcb.tracks` is used, it is lazily wrapping the native objects. With lists, all that wrapping happens at once. You could save some wrapping if breaking the iteration after something is found.
> The time spent to wrap is completely negligible. If you have an extremely, extremely large board, then the wrapping latency is the same, just upfront instead of distributed through the iteration.
> In almost all cases I see, there is not much
> Just to reiterate, performance is a non-issue here compared to understandability

`kicad-python` has always used generators. This will break everyone's code. 
> The only interface really being broken is `next`. I have never seen anyone actually use that in real code. Above, the "common pattern" is used almost everywhere and still works.

Getting rid of `_FootprintList` breaks this pattern: `pcb.footprints['D1']`.
> This functionality already exists using `pcb.footprint_by_ref('D1')`.
> I will gladly get rid of the custom iterator/mapping monster class. This point should be under upsides.

If the board has additions/removals (internal or external), then a list retrieved from before might be stale.

Behavior in v4
```python
all_tracks = pcb.tracks
# additions or deletions
for x in all_tracks: pass  # Reflects the changes made in between
# additions or deletions
for x in all_tracks: pass  # Errors. We should get a fresh one after all
```

Behavior in v5
```python
all_tracks = pcb.tracks
# additions or deletions
for x in all_tracks: pass  # Reflects item changes, but not adds/deletes
# additions or deletions
for x in all_tracks: pass  # Iterates again
```

> I don't think this will cause confusion. Lists are understood to not spontaneously change size. In cases where add/remove are suspected, the programmer will know to get a fresh list when needed.
> The only thing that goes stale is additions/removals. The perceived states we really care about (within items) are still dynamic
