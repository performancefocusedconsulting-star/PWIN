/**
 * Lightweight YAML parser for skill config files.
 * Handles: scalars, lists, nested objects, multi-line strings (|, >).
 * Does NOT handle: anchors, aliases, flow sequences, complex types.
 */

export function parse(text) {
  const lines = text.split('\n');
  const result = {};
  let i = 0;

  function getIndent(line) {
    const match = line.match(/^(\s*)/);
    return match ? match[1].length : 0;
  }

  function parseValue(raw) {
    if (raw === '' || raw === 'null' || raw === '~') return null;
    if (raw === 'true') return true;
    if (raw === 'false') return false;
    if (/^-?\d+$/.test(raw)) return parseInt(raw, 10);
    if (/^-?\d+\.\d+$/.test(raw)) return parseFloat(raw);
    // Strip quotes
    if ((raw.startsWith('"') && raw.endsWith('"')) || (raw.startsWith("'") && raw.endsWith("'"))) {
      return raw.slice(1, -1);
    }
    return raw;
  }

  function parseBlock(baseIndent) {
    const obj = {};

    while (i < lines.length) {
      const line = lines[i];

      // Skip empty lines and comments
      if (line.trim() === '' || line.trim().startsWith('#')) {
        i++;
        continue;
      }

      const indent = getIndent(line);
      if (indent < baseIndent) break;
      if (indent > baseIndent) { i++; continue; } // skip unexpected indentation

      const trimmed = line.trim();

      // Key: value pair
      const kvMatch = trimmed.match(/^([a-zA-Z_][\w]*)\s*:\s*(.*)/);
      if (kvMatch) {
        const [, key, rawVal] = kvMatch;

        // Multi-line block scalar (| or >)
        if (rawVal === '|' || rawVal === '>') {
          i++;
          const blockLines = [];
          const joiner = rawVal === '|' ? '\n' : ' ';
          while (i < lines.length) {
            const bl = lines[i];
            if (bl.trim() === '') {
              if (rawVal === '|') blockLines.push('');
              i++;
              continue;
            }
            if (getIndent(bl) <= baseIndent) break;
            blockLines.push(bl.trim());
            i++;
          }
          obj[key] = blockLines.join(joiner).trim();
          continue;
        }

        // Inline list: [a, b, c]
        if (rawVal.startsWith('[') && rawVal.endsWith(']')) {
          const inner = rawVal.slice(1, -1);
          obj[key] = inner.split(',').map(s => parseValue(s.trim()));
          i++;
          continue;
        }

        // Value on same line
        if (rawVal !== '') {
          obj[key] = parseValue(rawVal);
          i++;
          continue;
        }

        // Value on next lines (nested object or list)
        i++;
        if (i < lines.length) {
          const nextLine = lines[i];
          if (nextLine.trim() === '' || getIndent(nextLine) <= baseIndent) {
            obj[key] = null;
            continue;
          }

          const nextIndent = getIndent(nextLine);
          if (nextLine.trim().startsWith('- ')) {
            // List
            obj[key] = parseList(nextIndent);
          } else {
            // Nested object
            obj[key] = parseBlock(nextIndent);
          }
        }
        continue;
      }

      i++;
    }

    return obj;
  }

  function parseList(baseIndent) {
    const arr = [];

    while (i < lines.length) {
      const line = lines[i];
      if (line.trim() === '' || line.trim().startsWith('#')) { i++; continue; }

      const indent = getIndent(line);
      if (indent < baseIndent) break;

      const trimmed = line.trim();
      if (trimmed.startsWith('- ')) {
        const val = trimmed.slice(2).trim();
        if (val === '') {
          // Multi-line list item (nested object)
          i++;
          if (i < lines.length && getIndent(lines[i]) > baseIndent) {
            arr.push(parseBlock(getIndent(lines[i])));
          }
        } else {
          arr.push(parseValue(val));
          i++;
        }
      } else {
        break;
      }
    }

    return arr;
  }

  return parseBlock(0);
}
