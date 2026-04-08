---
name: CSV import UX guidance
description: Always inform users of required CSV structure before file upload — show column order, types, and examples
type: feedback
---

When building CSV import functionality, always show the user the expected file structure before opening the file picker. Use a modal with column order, data types, which fields are required/optional, and an example row.

**Why:** User feedback — "for the CSV upload functionality I feel it is important to inform the user the required structure." Users shouldn't have to guess the format.

**How to apply:** Any CSV/file import UI should present a structure guidance modal first, then proceed to file selection on confirm.
