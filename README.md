# glk-tinder
A generator for group matchings based on various constraints.

## Sample usage
```bash
python -m glk_tinder --input tests/data/input_file1.csv --output out.csv
```

```bash
python -m glk_tinder --input tests/data/input_file1.csv --output out.csv --constraints tests/data/constraints1.yaml
```


```bash
python -m glk_tinder --input tests/data/input_glk.csv --output out.csv
```
```bash
python -m glk_tinder --input tests/data/input_glk.csv --output out.csv --constraints tests/data/constraints_glk_gruppeneinteilung.yaml
```


## Structure Constraint File:

### Overview

The YAML file defines:

* The number of groups to create (`num_groups`)
* A list of constraints applied to a grouping/assignment problem

Each constraint has a `type` and optional parameters depending on that type.

---

### Top-level structure

```yaml
num_groups: <positive integer>

constraints:
  - type: <constraint type>
    priority: <low | medium | high>   # optional, defaults to "medium"
    ...
```

---

### Fields

#### `num_groups` (required)

* Type: `int`
* Must be `> 0`
* Represents the number of groups to partition the data into

Example:

```yaml
num_groups: 5
```

---

#### `constraints` (required)

* Type: `list of mappings`
* Each entry defines one constraint

---

### Constraint structure

Each constraint must contain:

```yaml
- type: <string>
  priority: <low | medium | high>   # optional, default = medium
  ...
```

#### Valid constraint types

| Type                  | Description                                      |
| --------------------- | ------------------------------------------------ |
| `balanced`            | Balance values of an attribute across groups     |
| `balanced group size` | Ensure equal group sizes                         |
| `at most n`           | Limit occurrences of a value per group           |
| `at least n`          | Require minimum occurrences of a value per group |

---

### Constraint definitions

---

#### 1. `balanced`

Ensures an attribute is evenly distributed across groups.

##### Required fields

```yaml
type: balanced
attribute: <column name from dataset>
```

##### Example

```yaml
- type: balanced
  attribute: Geschlecht
  priority: high
```

##### Rules

* `attribute` must exist in the dataset column names

---

#### 2. `balanced group size`

Ensures groups have equal size.

##### Required fields

```yaml
type: balanced group size
```

##### Optional fields

```yaml
priority: <low | medium | high>
```

##### Example

```yaml
- type: balanced group size
  priority: high
```

##### Notes

* No additional parameters required
* Target size is computed automatically as:

  ```
  number_of_rows / num_groups
  ```

---

#### 3. `at most n`

Limits how many rows match a condition.

##### Required fields

```yaml
type: at most n
attribute: <column name>
limit: <non-negative integer>
```

##### Optional fields

```yaml
value: <any value>   # default: null (None)
priority: <low | medium | high>
```

##### Example

```yaml
- type: at most n
  attribute: Geschlecht
  limit: 2
  value: male
  priority: low
```

##### Rules

* `attribute` must exist in dataset columns
* `limit` must be integer ≥ 0
* If `value` is omitted, it is interpreted as `null` (meaning all values depending on implementation)

---

#### 4. `at least n`

Requires a minimum number of matches.

##### Required fields

```yaml
type: at least n
attribute: <column name>
limit: <non-negative integer>
```

##### Optional fields

```yaml
value: <any value>   # default: null (None)
priority: <low | medium | high>
```

##### Example

```yaml
- type: at least n
  attribute: department
  limit: 2
  value: mathematics
  priority: medium
```

##### Rules

* `attribute` must exist in dataset columns
* `limit` must be integer ≥ 0
* If `value` is omitted, all values are considered (implementation-dependent behavior)

---

### Priority system

If omitted:

```yaml
priority: medium
```

Valid values:

| Priority | Meaning            |
| -------- | ------------------ |
| low      | weak constraint    |
| medium   | default importance |
| high     | strong constraint  |



## Validation rules summary

A YAML file is invalid if:

* `num_groups` is missing or not a positive integer
* `constraints` is missing or not a list
* `type` is not one of the allowed types
* required fields per constraint type are missing
* `attribute` is not in the provided dataset columns
* `limit` is not an integer ≥ 0
* `priority` is not `low | medium | high`
