# CLI Reference

> Documentación completa de los comandos y flags disponibles en sidecar-tagger.

---

## Uso Básico

```bash
python cli/main.py <input> [options]
```

---

## Flags Disponibles

| Flag | Alias | Descripción | Default |
|------|-------|-------------|---------|
| `--level` | `-l` | Nivel de análisis predefinido | `standard` |
| `--layers` | - | Capas específicas (comma-separated, sobrescribe --level) | - |
| `--confidence-threshold` | - | Threshold shortcut Capa 1 (0.0-1.0) | `0.8` |
| `--similarity-threshold` | - | Threshold cache Capa 2 (0.0-1.0) | `0.9` |
| `--output-dir` | `-o` | Directorio de salida para sidecar.json | `.` |
| `--verbose` | `-v` | Habilitar logging detallado | `false` |
| `--overwrite` | - | Reemplazar sidecar.json existente | `false` |
| `--min-confidence` | `-m` | Filtrar metadata por confidence | `0.0` |

---

## Analysis Levels

Niveles predefinidos que enablean un conjunto de capas:

```bash
# minimal: Solo hash dedup ($0 cost, fastest)
python cli/main.py path --level minimal

# fast: Hash + OS metadata ($0 cost, ~100ms/file)
python cli/main.py path --level fast

# standard: Hash + OS + Semantic Cache (default, $0 cost)
python cli/main.py path --level standard

# deep: Pipeline completo con LLM (usa API)
python cli/main.py path --level deep
```

### Capas por Level

| Level | Capas | Costo |
|-------|-------|-------|
| minimal | 0 | $0 |
| fast | 0, 1 | $0 |
| standard | 0, 1, 2 | $0 |
| deep | 0, 1, 2, 3 | $ |

---

## Control Granular de Capas

Para testing específico de cada capa, usá `--layers` (sobrescribe `--level`):

```bash
# Solo Capa 0 (hash dedup)
python cli/main.py path --layers 0

# Capas 0 + 1 (hash + OS, sin embeddings, sin LLM)
python cli/main.py path --layers 0,1

# Capas 0 + 1 + 2 (hash + OS + embeddings, sin LLM)
python cli/main.py path --layers 0,1,2

# Solo Capa 3 (LLM solo - requiere archivo en cache)
python cli/main.py path --layers 3
```

---

## Thresholds Personalizados

```bash
# Lower confidence threshold para Layer 1 shortcut
python cli/main.py path --confidence-threshold 0.5

# Lower similarity threshold para Layer 2 cache
python cli/main.py path --similarity-threshold 0.7

# Combinar con capas granulares
python cli/main.py path --layers 0,1,2 --confidence-threshold 0.6
```

---

## Referencia de Capas

| Capa | Nombre | Descripción | Costo |
|------|--------|-------------|-------|
| 0 | Hash Gate | SHA-256 deduplication | $0 |
| 1 | Native + OS | EXIFTOOL + file system metadata | $0 |
| 2 | Embeddings | FastEmbed semantic cache | $0 |
| 3 | LLM + Hint | Gemini with clustering context | $ |

---

## Ejemplos Completos

```bash
# Scan básico con nivel default
python cli/main.py ./documentos

# Scan verbose con overwrite
python cli/main.py ./documentos --verbose --overwrite

# Análisis profundo con output personalizado
python cli/main.py ./documentos --level deep --output-dir ./output --verbose

# Solo hash dedup (para encontrar duplicados)
python cli/main.py ./documentos --layers 0

# Solo metadata básica (sin API)
python cli/main.py ./documentos --layers 0,1

# Testing de similarity threshold bajo
python cli/main.py ./documentos --layers 0,1,2 --similarity-threshold 0.7
```

---

## Shortcuts

- **Layer 1**: Si confidence >= threshold → return temprano (capas 2-3 saltadas)
- **Layer 2**: Si similarity >= threshold → return cacheado (capa 3 saltada)

---

## Archivos de Salida

- `sidecar.json` - Metadata consolidada
- `findings.md` - Reporte de análisis

Ambos se generan en `--output-dir` (default: directorio actual).
