# CLI Reference

> Complete documentation of all available commands and flags in sidecar-tagger.

---

## Migration Notice

> **Breaking Change**: The CLI now uses subcommands. If you previously ran:
> ```bash
> python cli/main.py ./path
> ```
> You must now run:
> ```bash
> python cli/main.py process ./path
> ```

---

## Basic Usage

```bash
python cli/main.py <command> [options]
```

### Available Commands

| Command | Description |
|---------|-------------|
| `process` | Generate metadata sidecars for files |
| `clean` | Remove generated sidecar files |

---

## Process Command

Generate consolidated, semantically-enriched metadata for files.

```bash
python cli/main.py process <input> [options]
```

### Available Flags

| Flag | Alias | Description | Default |
|------|-------|-------------|---------|
| `--level` | `-l` | Predefined analysis level | `standard` |
| `--layers` | - | Specific layers (comma-separated, overrides --level) | - |
| `--confidence-threshold` | - | Layer 1 shortcut threshold (0.0-1.0) | `0.8` |
| `--similarity-threshold` | - | Layer 2 cache threshold (0.0-1.0) | `0.9` |
| `--output-dir` | `-o` | Output directory for sidecar.json | `.` |
| `--verbose` | `-v` | Enable detailed logging | `false` |
| `--overwrite` | - | Replace existing sidecar.json | `false` |
| `--min-confidence` | `-m` | Filter metadata by confidence | `0.0` |

### Analysis Levels

Predefined levels that enable a specific set of layers:

```bash
# minimal: Hash dedup only ($0 cost, fastest)
python cli/main.py process path --level minimal

# fast: Hash + OS metadata ($0 cost, ~100ms/file)
python cli/main.py process path --level fast

# standard: Hash + OS + Semantic Cache (default, $0 cost)
python cli/main.py process path --level standard

# deep: Full pipeline with LLM (uses API)
python cli/main.py process path --level deep
```

### Layers by Level

| Level | Layers | Cost |
|-------|--------|------|
| minimal | 0 | $0 |
| fast | 0, 1 | $0 |
| standard | 0, 1, 2 | $0 |
| deep | 0, 1, 2, 3 | $ |

### Granular Layer Control

For testing specific layers, use `--layers` (overrides `--level`):

```bash
# Layer 0 only (hash dedup)
python cli/main.py process path --layers 0

# Layers 0 + 1 (hash + OS, no embeddings, no LLM)
python cli/main.py process path --layers 0,1

# Layers 0 + 1 + 2 (hash + OS + embeddings, no LLM)
python cli/main.py process path --layers 0,1,2

# Layer 3 only (LLM only - requires file in cache)
python cli/main.py process path --layers 3
```

### Custom Thresholds

```bash
# Lower confidence threshold for Layer 1 shortcut
python cli/main.py process path --confidence-threshold 0.5

# Lower similarity threshold for Layer 2 cache
python cli/main.py process path --similarity-threshold 0.7

# Combine with granular layers
python cli/main.py process path --layers 0,1,2 --confidence-threshold 0.6
```

### Layer Reference

| Layer | Name | Description | Cost |
|-------|------|-------------|------|
| 0 | Hash Gate | SHA-256 deduplication | $0 |
| 1 | Native + OS | EXIFTOOL + file system metadata | $0 |
| 2 | Embeddings | FastEmbed semantic cache | $0 |
| 3 | LLM + Hint | Gemini with clustering context | $ |

### Shortcuts

- **Layer 1**: If confidence >= threshold → early return (layers 2-3 skipped)
- **Layer 2**: If similarity >= threshold → cached return (layer 3 skipped)

---

## Clean Command

Remove generated sidecar files (`sidecar.json`, `findings.md`) from a directory tree.

```bash
python cli/main.py clean [options]
```

### Available Flags

| Flag | Alias | Description | Default |
|------|-------|-------------|---------|
| `--path` | `-p` | Root directory to clean | `.` |
| `--dry-run` | `-n` | Show files that would be deleted without removing them | `false` |

### Examples

```bash
# Clean current directory
python cli/main.py clean

# Clean specific directory
python cli/main.py clean -p ./documents

# Preview what would be deleted
python cli/main.py clean -p ./documents --dry-run
```

### Output

The clean command prints a summary:

```
Clean complete:
  Files found:   4
  Files deleted: 4

All target files removed successfully.
```

In dry-run mode:

```
[DRY RUN] Found 4 file(s) to clean:
  - /path/to/sidecar.json
  - /path/to/findings.md

[DRY RUN] Summary: 4 file(s) would be deleted.
```

---

## Complete Examples

```bash
# Basic scan with default level
python cli/main.py process ./documents

# Verbose scan with overwrite
python cli/main.py process ./documents --verbose --overwrite

# Deep analysis with custom output
python cli/main.py process ./documents --level deep --output-dir ./output --verbose

# Hash dedup only (to find duplicates)
python cli/main.py process ./documents --layers 0

# Basic metadata only (no API)
python cli/main.py process ./documents --layers 0,1

# Testing low similarity threshold
python cli/main.py process ./documents --layers 0,1,2 --similarity-threshold 0.7

# Clean generated files
python cli/main.py clean -p ./documents

# Preview clean operation
python cli/main.py clean -p ./documents --dry-run
```

---

## Output Files

- `sidecar.json` - Consolidated metadata
- `findings.md` - Analysis report

Both are generated in `--output-dir` (default: current directory).
