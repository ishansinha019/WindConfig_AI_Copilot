# Availability Configuration Workflow — Milestones & Handoff

> **For any agent or developer picking this up:** read this file top to bottom
> before writing code. It is the source of truth for the availability
> configuration workflow. Work milestones **in order**, tick the checkboxes,
> and append to the **Progress Log** at the bottom when you finish a step.
> Do not skip the "Decisions" section — several defaults were chosen there and
> the user may have overridden them.

Baseline commit when this plan was written: `9c7c95b` (draft/publish engine with OCC).

---

## 1. What we are building (user's requirement)

A user selects a **contract**, creates one or more **availability configurations
(AV configs)** under it, edits them through a 4-step wizard, saves them as
**drafts**, and later **publishes** them.

```
Home page (contract cards, each with an AV config carousel)
   ├─ "+" on a card ──────────► empty Wizard (new) ──► first Save draft creates the AV config GUID
   ├─ mini card ⋮ ▸ Edit ─────► Wizard loaded by GUID ──► Save draft (new version) / Publish
   ├─ mini card ⋮ ▸ Delete ───► confirm ──► AV config (GUID) and all its versions removed
   └─ click mini card body ───► same as Edit
```

### AV config identity (user decision)

- Every AV config has its own **GUID** (`availability_configurations.id`, a UUID).
  It is unique across the system, so different AV configs under the same
  contract always have different GUIDs.
- The GUID is created by the backend on the **first Save draft**. Pressing "+"
  only opens an empty wizard; nothing is stored until the user saves.
- The GUID **never changes**. Later saves add new versions under the same GUID.
  Edit, delete, publish and history all use this GUID in the URL/API.
- Versions keep their own internal ids for history and diff, but users never
  need them to edit or delete.

### Home page layout (from the user's reference screenshot)

A responsive grid of **contract cards** (3 columns on wide screens, 2 on
medium, 1 on small). Each card contains:

| Area | Content | Source |
|---|---|---|
| Header | Contract name | `contracts.name` |
| Icon | Coloured document icon (colour varies per contract) | derived from contract (e.g. order reason) |
| Info rows (icon + label + value) | Order reason | `contracts.order_reason` (NEW) |
| | Sales document # | `contracts.sales_document_number` (NEW) |
| | Windfarm `<name>` \| turbines `# <count>` | wind farm name + turbine count |
| | Contract dates `<start> to <end>` + **Live / Expired** indicator | derived: Live if today is within the dates, else Expired |
| | Customer (several names joined with `\|`, may wrap) | `contracts.customer_names` (NEW, list) |
| Divider | | |
| AV config header | "Availability Configuration" + badge "⚙ N Configurations" + **"+"** button | count of AV configs; "+" opens an empty wizard for this contract |
| Carousel | One **mini card** per AV config, prev/next arrows (disabled at the ends), dot pagination | AV config summaries |

Each **mini card** shows:
- AV config name + **⋮ menu** with exactly two options: **Edit** (opens the
  wizard by GUID) and **Delete** (confirm dialog, then removes the AV config
  by GUID). Delete rule: see D14.
- Status (Draft / Published) | date range from the latest version (`Dates not set` if empty).
  The "±" icon in the reference screenshot is ignored.
- "Created on `<date>` by `<user>`".
- "Last updated on `<date>` by `<user>`".
- Clicking the card body opens the wizard for that config.

If a contract has no AV configs, the carousel area shows an empty state with
a "Create first configuration" button. When there are many configs (the
reference shows 51), the dots row would become unreadable, so show at most
~10 dots and switch to a "3 / 51" counter above that.

All names, customers, document numbers and users in seed data must be
**invented**. Do not copy any names or numbers from the reference screenshot.

### Wizard steps and fields

| Step | Field | Input component (shadcn/ui) | Notes |
|---|---|---|---|
| 1. Basic details | Contract name | read-only `Input` | from contract |
| | AV configuration name | `Input` | required |
| | Warranted calculation type | `Select` | `TBA` (Time-Based), `YBA` (Yield-Based), `RBA` (Revenue-Based) |
| | Start date / End date | `Popover` + `Calendar` (date picker) | end > start; **may be outside the contract dates** (contracts get renewed) |
| 2. Turbines | Turbines in scope | `Table` + `Checkbox` (select all, grouped by turbine group) | ~10 dummy turbines `T01..T10`, different per contract |
| 3. Formula & alarm categories | Formula | `Select` (filtered by calculation type) | synthetic formula catalog |
| | Alarm tree | custom tree built from `Collapsible` + `Checkbox` | Category ▸ Alarm; add/remove alarms |
| | Alarm → turbine assignment | per-alarm multi-select (`Popover` + `Command` + `Checkbox`) | only turbines chosen in step 2 |
| 4. Details | Park availability (%) | `Input type=number` | 0–100, defaults to contract target |
| | Wind parameters: Low wind variant | `Select` | synthetic options |
| | Wind parameters: High wind variant | `Select` | synthetic options |

Wizard chrome: left step navigation (completion indicator per step), sticky
footer with **Save draft**, **Back/Next**, and a **Review & Publish** panel
showing backend readiness errors.

---

## 2. Honest assessment — how the new design connects to what exists

### What we can reuse as-is
- Contracts, wind farms, turbine groups, turbines, alarm categories, production
  periods (tables + seed + `GET /contracts/{id}` detail endpoint).
- The versioning ideas in
  [backend/app/services/configurations.py](../backend/app/services/configurations.py):
  JSONB snapshots, checksum, optimistic concurrency (`base_version` → 409),
  readiness validation before publish, immutable published versions,
  archive-on-republish, structural diff.
- TanStack Query setup and Tailwind theme tokens in the frontend.

### What must change (the real gaps)
1. **A2 implemented:** each AV config has a stable GUID under its contract and
   owns its versions. The existing contract-scoped configuration routes act
   only on the migrated `Default configuration` until they are replaced in A3.
2. **A1 complete:** shadcn/ui is initialized for Tailwind v3 with the `@/*`
   alias and planned UI primitives. Keep the existing Tailwind major version;
   future components should follow the generated `components.json` configuration.
3. **A1 complete:** React Router and form/date dependencies are installed. The
   app now separates the contract home page from contract detail. The home
   page's final card/carousel design remains A4.
4. **The snapshot is an untyped `dict[str, Any]`** with a shape
   (`formula_type`, `included_alarm_codes`, `variables`, …) that does not match
   the wizard. → Introduce a typed, versioned snapshot schema (`schema_version: 2`)
   in Pydantic (A3). Drafts may be partial; publish requires complete data.
5. **A2 implemented:** `GET /contracts/{id}` returns child `alarms` under
   each alarm category (`GRID`, `MAINT`, `WX`).
6. **A2 implemented:** fresh databases seed six synthetic contracts with
   contract-specific `T01`-style turbines (see 3.1a). An upgraded database
   keeps its original fleets so existing drafts still match them. No reset
   is required for an upgrade.
7. **Tests use SQLite** ([backend/tests/conftest.py](../backend/tests/conftest.py)),
   including a SQLite equivalent of the one-published-version index. Live
   PostgreSQL migration and index behavior still need separate verification.
8. **Calculation types confirmed by the user:** `TBA` = Time-Based Availability,
   `YBA` = Yield-Based Availability, `RBA` = Revenue-Based Availability.
   `NOWSI` is dropped. Formulas per type are synthetic examples.
9. **No tree component exists in shadcn/ui.** It must be composed manually;
   this is the riskiest UI piece (A6).
10. The frontend Docker image uses `npm ci`, so **`package-lock.json` must be
    committed** whenever dependencies are added.
11. **A2 implemented:** contract responses now include order reason, sales
    document number, and a list of customer names. The old `customer_name`
    response field is retained for the A1 pages.
12. **There are no users or login.** "Created by / Last updated by" needs a
    name. → Lightweight "acting user" (D10): the header has a user picker with
    invented names, the frontend sends it as an `X-User-Name` request header,
    and the backend stores it. This is not authentication.
13. **The home page would make one request per card** if each card loaded its
    own configs. → `GET /contracts` returns the card fields plus AV config
    summaries in one response (A3).

---

## 3. Target design

### 3.1 Data model

```
Contract 1 ──< WindFarm 1 ──< Turbine (code T01..Tnn, unique per wind farm;
                                        each contract has its own set)
Contract 1 ──< AlarmCategory 1 ──< Alarm            (NEW child table)
Contract 1 ──< AvailabilityConfiguration (NEW header)
                     1 ──< ConfigurationVersion (re-parented; JSONB snapshot)
```

`contracts` (changed, for the home-page card):
- add `order_reason` varchar(120), e.g. "Warranty", "Long-term service agreement".
- add `sales_document_number` varchar(20), unique, e.g. `9100000001`.
- replace `customer_name` with `customer_names` (JSON list of strings); the
  migration copies the old value into a one-item list.
- Live / Expired is **not stored**; it is computed from the dates and today.

`availability_configurations` (new):

| column | type | notes |
|---|---|---|
| id | UUID PK | |
| contract_id | UUID FK → contracts, cascade | |
| name | varchar(160) | denormalised from latest snapshot for listing; unique per contract |
| created_by / updated_by | varchar(120) | acting user name (D10) |
| created_at / updated_at | timestamptz | `TimestampMixin`; `updated_*` changes on every draft save |

`configuration_versions` also gets `created_by` so version history shows who saved each version.

`configuration_versions` (changed):
- add `availability_configuration_id` UUID FK (not null after backfill), cascade.
- A2 removes the redundant `contract_id` column; join through the AV config to
  scope versions to a contract. The old API still returns a derived `contract_id`.
- replace unique `(contract_id, version_number)` with
  `(availability_configuration_id, version_number)`.
- replace partial index `uq_published_contract_config` with
  `uq_published_av_config` on `(availability_configuration_id) WHERE status='published'`.

`alarms` (new): `id`, `alarm_category_id` FK, `code` (unique per category),
`name`, `description` nullable.

Config header **status is derived**, not stored: `published` if any version is
published, plus `has_unpublished_draft` if the latest version is newer than the
published one.

### 3.1a Turbine scoping invariant (must hold everywhere)

- Each contract has its **own** turbine set, reached only through
  `Contract → WindFarm → Turbine`. There is no global turbine picker.
- Sets vary in **count, models/ratings and grouping**
  (see D7), even though codes look alike (`T01` in contract A ≠ `T01` in contract B).
- An AV configuration may reference **only turbines of its own contract**:
  snapshot `turbine_ids` and every `alarm_assignments[].turbine_ids` must be a
  subset of the contract's turbine UUIDs.
- Turbines are always identified by **UUID** in storage and APIs; codes are for
  display only and are resolved through the owning contract's turbine list.
- Enforcement points:
  - **Save draft (A3):** reject foreign turbine UUIDs with `422`, even though
    drafts may be incomplete (this is invalid data, not missing data).
  - **Readiness/publish (A3):** the same rule is a blocking error (defence in depth).
  - **Step 2 UI (A6):** options come only from
    `GET /contracts/{contractId}` → `wind_farms[].turbines`; the wizard is opened
    under a contract route, so it can never show another contract's turbines.
  - **Step 3 UI (A6):** alarm assignment options are the turbines selected in step 2.

### 3.2 Snapshot schema v2 (stored in `configuration_versions.snapshot_data`)

**Save draft = one JSON document holding every input the user selected in all
four wizard steps** for that AV config (confirmed by the user). Rules:
- Each save stores the **full** wizard state, never a partial patch or delta, so
  any version can reload the wizard on its own (prepopulation) and be diffed.
- The **first** save creates the AV config and its GUID plus version 1. Every
  later save creates a new `configuration_versions` row (version number + 1,
  checksum of the JSON) under the same GUID.
- To save at all, the AV configuration name must be filled (the mini card and
  the "unique per contract" rule need it). Everything else may be empty.
- Drafts may have empty or `null` fields for steps not filled yet; publish
  requires the complete form (3.5).
- The contract name shown in Step 1 is read-only and comes from the contract,
  so it is not stored in the JSON. Turbines and alarms are stored by UUID.

```json
{
  "schema_version": 2,
  "basic_details": {
    "name": "North Ridge 2026 – Base TBA",
    "calculation_type": "TBA",
    "start_date": "2026-01-01",
    "end_date": "2026-12-31"
  },
  "turbine_ids": ["<uuid>", "..."],
  "formula_code": "TBA_STD",
  "alarm_assignments": [
    { "alarm_id": "<uuid>", "turbine_ids": ["<uuid>", "..."] }
  ],
  "details": {
    "park_availability_pct": 97.5,
    "low_wind_variant": "LW_EXCLUDE_BELOW_CUT_IN",
    "high_wind_variant": "HW_EXCLUDE_ABOVE_CUT_OUT"
  }
}
```

Pydantic: `AvailabilitySnapshotDraft` (every field optional) for saving and
`AvailabilitySnapshotComplete` (strict) used by readiness validation.

### 3.3 Catalogs (backend-owned constants, served to the UI)

Defined once in `backend/app/domain/catalog.py`, exposed via `GET /api/v1/catalog`
so the dropdowns and the validator share one list. All values are **synthetic**.

- Calculation types: `TBA` (Time-Based Availability), `YBA` (Yield-Based
  Availability), `RBA` (Revenue-Based Availability).
- Formulas (each tagged with a calculation type), e.g.
  `TBA_STD` "Available hours / Period hours",
  `TBA_EXCL` "(Period − Excluded − Unavailable) / (Period − Excluded)",
  `YBA_STD` "Actual yield / Potential yield",
  `YBA_LOSS` "1 − Lost yield / Potential yield",
  `RBA_STD` "Actual revenue / Potential revenue",
  `RBA_LOSS` "1 − Lost revenue / Potential revenue".
- Low wind variants: `LW_EXCLUDE_BELOW_CUT_IN`, `LW_COUNT_AS_AVAILABLE`, `LW_PRO_RATA_POWER_CURVE`.
- High wind variants: `HW_EXCLUDE_ABOVE_CUT_OUT`, `HW_COUNT_AS_UNAVAILABLE`, `HW_STORM_GRACE_WINDOW`.

### 3.4 API (all under `/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| GET | `/catalog` | calc types, formulas, wind variants |
| GET | `/users` | invented acting users for the header picker (D10) |
| GET | `/contracts` | **home page**: per contract the card fields (order reason, sales doc #, wind farm, turbine count, dates, `is_live`, customer names) + `availability_configurations: [summary]` (id, name, status, calculation type, start/end from latest version, created/updated at + by), newest updated first |
| GET | `/contracts/{cid}` | existing; extend alarm categories with child `alarms` |
| GET | `/contracts/{cid}/availability-configurations` | list headers + derived status, latest version no., updated_at |
| POST | `/contracts/{cid}/availability-configurations` | **first Save draft**: body = full draft JSON (3.2); creates the AV config, returns its GUID + version 1 |
| GET | `/contracts/{cid}/availability-configurations/{acid}` | header + latest version + published version |
| POST | `/contracts/{cid}/availability-configurations/{acid}/drafts` | save new draft version (OCC `base_version`) |
| GET | `.../{acid}/versions` and `.../{acid}/versions/{vid}` | history |
| GET | `.../{acid}/versions/{vid}/readiness` | deterministic validation |
| POST | `.../{acid}/versions/{vid}/publish` | publish (archives previous published of *this* config) |
| GET | `.../{acid}/diff?v_from=&v_to=` | structural diff for v2 shape |
| DELETE | `/contracts/{cid}/availability-configurations/{acid}` | delete the AV config by GUID with all its versions (rule D14); `404` if the GUID is not in this contract |

The old contract-scoped routes in
[backend/app/api/v1/configurations.py](../backend/app/api/v1/configurations.py)
are removed in A3 (and their tests rewritten), not kept in parallel.

### 3.5 Validation rules (readiness / publish blockers)

Blocking:
- name present and unique within the contract.
- calculation type in catalog.
- start and end dates present, end > start. Dates **may** be outside the
  contract dates (user decision: contracts get renewed).
- at least one turbine; all turbine ids belong to **this config's contract** (3.1a).
- formula present and matches calculation type.
- every **required** alarm category has ≥ 1 alarm included.
- every alarm id belongs to an alarm category of this config's contract.
- every alarm assignment references only turbines selected in step 2, and is non-empty.
- park availability present and 0–100.
- low and high wind variants present and in catalog.
- **no overlap** (confirmed by the user as blocking): another AV config of the
  same contract with a *published* version must not have a date range that
  intersects this one (inclusive) **and** share at least one turbine. The
  config's own previously published version is ignored, since republishing
  archives it. The error names the conflicting config, dates and turbine codes.

Warnings:
- turbines in scope that have no alarm assigned.

### 3.6 Frontend structure

```
src/
  components/ui/            # shadcn generated components
  lib/api.ts                # typed fetchers (extend)
  lib/utils.ts              # shadcn cn()
  features/av-config/
    schema.ts               # zod schema mirroring snapshot v2
    WizardLayout.tsx        # left step nav + footer actions
    steps/BasicDetailsStep.tsx
    steps/TurbinesStep.tsx
    steps/FormulaAlarmsStep.tsx
    steps/DetailsStep.tsx
    components/AlarmTree.tsx
    components/DatePicker.tsx
    ReviewPublishPanel.tsx
  features/contracts/
    ContractCard.tsx        # header, icon, info rows, Live/Expired
    AvConfigCarousel.tsx    # shadcn Carousel + arrows + dots / "n / N" counter
    AvConfigMiniCard.tsx    # name, ⋮ DropdownMenu (Edit / Delete), status, dates, created/updated by
    DeleteAvConfigDialog.tsx # confirm → DELETE by GUID
  components/ActingUserPicker.tsx     # header Select; stored in localStorage
  pages/
    HomePage.tsx                      # route "/" — grid of ContractCard
    ContractDetailPage.tsx            # route "/contracts/:contractId" (secondary: turbines/alarms reference)
    AvConfigWizardPage.tsx            # routes "/contracts/:contractId/configurations/new" (from "+")
                                      #    and "/contracts/:contractId/configurations/:configId" (GUID; Edit)
```

One `react-hook-form` instance spans all four steps; step query param `?step=1..4`.
"Save draft" always allowed (partial data OK); "Publish" enabled only when
backend readiness returns `is_valid: true`. Warn on navigation with unsaved changes.

---

## 4. Decisions (defaults chosen — user may override)

| # | Decision | Default chosen |
|---|---|---|
| D1 | Multiple AV configs published at once per contract? | **Yes**, one published version *per config*, but publishing is **blocked** if it overlaps another published config in both dates and turbines (user decision). |
| D2 | Save behaviour | Explicit **Save draft** button; each save = new version (history + diff). No autosave. |
| D3 | Meaning of "add/remove alarms" | Include/exclude alarms from the contract's seeded alarm catalog. Creating brand-new custom alarms is **out of scope** (stretch goal A9). |
| D4 | Default alarm assignment | Newly added alarm is assigned to **all** turbines selected in step 2; user can narrow. Removing a turbine in step 2 removes it from all assignments. |
| D5 | Editing a published config | Allowed: creates a new draft version on the same config; publishing it archives the old published version. |
| D6 | Park availability default | Prefilled from `contract.target_availability`, editable. |
| D7 | Turbine seed (different per contract) | On a fresh database: North Ridge `T01..T10`, two groups, `Demo N50` (5.0 MW); Coastal Plains `T01..T08`, two groups, `Demo C66` (6.6 MW). Remaining seed contracts have 6–10 turbines each with varying models. Same codes across contracts are separate rows/UUIDs. Upgraded databases retain the original seeded fleets. |
| D8 | Production periods | Not part of the 4-step wizard (user did not ask). Existing data stays; not validated. |
| D9 | Contract status | Becomes `published` once any of its AV configs is published (existing behaviour kept). Not shown on the home-page card; the card shows Live / Expired instead. |
| D10 | Created by / updated by | No login. Header "acting user" picker with ~4 invented names, saved in localStorage, sent as `X-User-Name`; backend falls back to `"Demo User"` if missing. |
| D11 | Carousel | shadcn `Carousel` (Embla). Mini cards ordered by last updated, newest first. Dots up to 10, otherwise a "n / N" counter. |
| D12 | Seed contracts | 6 invented contracts so the 3-column grid fills two rows: a mix of Live and Expired, different order reasons, 1–3 customers each, and 0 to ~12 AV configs (one with 0 for the empty state, one with many to exercise the carousel). Each has its own turbine set per D7. |
| D13 | Card click targets | Mini card body or ⋮ ▸ Edit → wizard by GUID. Contract name → contract detail page. "+" → empty wizard (`/configurations/new`). |
| D14 | Delete rule | Drafts (never published) can always be deleted. A config that currently has a **published** version cannot be deleted (Delete shown disabled with a tooltip) so a live configuration is never lost by accident. Delete removes the AV config and all its versions. |
| D15 | Leaving the new wizard without saving | Nothing is stored and no GUID exists; the unsaved-changes guard warns first. |

## 5. Open questions for the user
- Resolved: calculation types are TBA / YBA (Yield-Based) / RBA (Revenue-Based); NOWSI dropped.
- Resolved: overlapping published configs are **blocking**.
- Resolved: a draft save is one JSON document containing all wizard inputs (3.2).
- Resolved (user accepted default): calculation type does not change which fields appear; all types show the same fields.
- Should step-level "in_review" (existing status) be exposed in the UI, or keep only draft → published?
- Resolved: AV config dates may be outside the contract dates; expired contracts can get new configs.
- Resolved: the "±" icon is ignored.
- Resolved: ⋮ menu = Edit and Delete only; each AV config is identified by its own GUID, created on first Save draft.
- Resolved (user accepted D14 default): a **published** AV config cannot be deleted; only configs without a published version can be deleted.

---

## 6. Milestones

Each milestone must end with: code + tests passing, docs ticked, Progress Log
entry, and a commit. Verification commands are in section 7.

### Two-laptop development and verification

The current work laptop does **not** have Docker Desktop. The personal laptop
does and is the machine for Docker/PostgreSQL and full-stack integration checks.
Do not treat the absence of Docker on the work laptop as a reason to block
implementation; split verification as follows:

- **Work laptop (every milestone):** run the checks that do not need Docker:
  backend `uv run --extra dev pytest` (tests use in-memory SQLite), frontend `npm run lint`
  and `npm run build`, plus any available unit/type checks. Do not claim that
  these validate PostgreSQL migrations or full-stack behaviour.
- **Personal laptop (milestones that touch database, API integration, or UI
  flows):** pull the pushed commit, run Docker Compose and verify the actual
  PostgreSQL migration/seed/API/browser flow listed for that milestone below.
  Push any fixes and repeat the work-laptop checks.
- A milestone is **implemented** after its work-laptop checks pass, and
  **verified end-to-end** only after its personal-laptop checks pass. Record
  both states separately in the Progress Log. Never mark a Docker check passed
  when it has not been run.
- Push each coherent milestone so the personal laptop can pull the exact code
  under test. On that laptop, check `git status` first and preserve any local
  changes; do not reset or discard them as part of this workflow.

### A0 — Plan & handoff doc ✅
- [x] This file.

### A1 — Frontend foundation (shadcn/ui, routing, forms)
- [x] Add `@/*` path alias in `tsconfig.json` and `vite.config.ts`.
- [x] Init shadcn/ui for Tailwind v3 (`npx shadcn@2.3.0 init`), creating `components.json`, `src/lib/utils.ts`, CSS variables in `styles.css`, and `tailwindcss-animate`.
- [x] Add components: `button input label select popover calendar checkbox table card badge dialog collapsible command tabs separator form tooltip sonner skeleton alert carousel dropdown-menu`.
- [x] Install `react-router-dom react-hook-form zod @hookform/resolvers date-fns`.
- [x] Introduce routes: `/` → HomePage (existing contract cards moved from DashboardPage for now; redesigned in A4), `/contracts/:contractId` → ContractDetailPage (existing farm/turbine/alarm panels).
- [x] Remove the stale milestone sidebar in `App.tsx`; keep `HealthStatus` in header.
- **Work laptop done:** `npm run lint` and `npm run build` pass.
- **Personal laptop verified when:** with the app running, the home and contract-detail routes render and navigation works. **Not run yet** (requires the backend/Compose stack).

### A2 — Backend data model & seed
- [x] Add `AvailabilityConfiguration` and `Alarm` models. Re-parent `ConfigurationVersion` by config GUID and add `created_by`.
- [x] Add contract card fields: `order_reason`, `sales_document_number`, `customer_names`; keep the old API field for A1.
- [x] Add [migration 202611260001](../backend/alembic/versions/202611260001_add_availability_configurations.py). Attach existing versions to one `Default configuration` per contract without changing snapshot JSON, checksums, or version IDs. Enforce unique version numbers and at most one published version per config.
- [x] Seed six invented contracts, distinct turbine fleets and nested alarms, and a mix of v2 drafts and published configurations with demo author metadata. One contract has no configs and one has 12. Keep the legacy North Ridge v1 draft to exercise the existing A1 path.
- [x] Extend `GET /contracts/{id}` to nest `alarms`; test contract scoping, reseeding, the legacy API, and per-config uniqueness.
- **Work laptop done:** 17 SQLite-backed pytest tests passed; Alembic generated PostgreSQL SQL for fresh install, upgrade, and downgrade. Frontend lint and build passed.
- **Personal laptop verification pending:** execute the fresh install and upgrade from `202611220002` on PostgreSQL, verify legacy snapshots and seeded data, and exercise downgrade on a disposable DB (see section 7).

Downgrade flattens versions back to the contract, renumbering only collisions.
It retains snapshots and checksums, but drops A2-only config and alarm metadata
and retains only the first customer name. It refuses to downgrade when the
same contract has multiple published configurations rather than unpublishing one.

### A3 — Catalog, typed snapshot, AV config API, validation
- [ ] `app/domain/catalog.py` + `GET /catalog`; invented acting users + `GET /users`.
- [ ] Read `X-User-Name` (fallback `"Demo User"`) on create / save draft / publish and store it in `created_by` / `updated_by`.
- [ ] Extend `GET /contracts` with the home-page card fields, `is_live`, turbine count and AV config summaries (3.4), loaded without one query per contract.
- [ ] Pydantic snapshot v2 (draft + complete) in `app/schemas/availability_configuration.py`.
- [ ] Service `app/services/availability_configurations.py`: create/list/get/save-draft (OCC)/publish/diff/delete — port logic from `services/configurations.py`, then delete the old contract-scoped router/service.
- [ ] Rewrite readiness validation per section 3.5 (return field-path hints, e.g. `"step": 3, "field": "alarm_assignments"`, so the UI can jump to the step).
- [ ] Enforce turbine/alarm scoping (3.1a): save-draft returns `422` if any `turbine_ids` or `alarm_assignments[].turbine_ids` / `alarm_id` belongs to another contract.
- [ ] pytest: create config, save drafts + 409 conflict, save draft with another contract's turbine UUID → 422, saved JSON round-trips unchanged (all wizard inputs reload), `GET /contracts` card fields + summaries (Live vs Expired, config count, created/updated by from `X-User-Name`), first save returns a new GUID and two configs in one contract get different GUIDs, save without a name → 422, dates outside the contract dates accepted, readiness failures per rule, publish success, republish archives previous, two non-overlapping configs both published, overlapping config (shared turbine + intersecting dates) blocked from publishing, same turbines with non-intersecting dates allowed, delete rules (draft deleted with all versions → later GET by GUID is 404; config with a published version → 409; GUID from another contract → 404), diff.
- **Work laptop done when:** `uv run pytest` passes and OpenAPI exposes the new routes.
- **Personal laptop verified when:** migrations apply to PostgreSQL, seeded data is returned by the real API, and the endpoints work against PostgreSQL via `/docs` or the frontend.

### A4 — Home page: contract cards + AV config carousel
- [ ] `HomePage` grid of `ContractCard` exactly as in section 1 "Home page layout" (icon, info rows, Live/Expired, customers).
- [ ] "Availability Configuration" header with "⚙ N Configurations" badge and "+" button.
- [ ] `AvConfigCarousel` + `AvConfigMiniCard` (status, dates, created/updated on + by, ⋮ menu); arrows disabled at the ends; dots or "n / N" counter (D11); empty state.
- [ ] "+" navigates to `/contracts/:contractId/configurations/new` (the wizard itself is built in A5).
- [ ] ⋮ menu: **Edit** → wizard by GUID; **Delete** → `DeleteAvConfigDialog` → DELETE by GUID → card refreshes (disabled with tooltip if published, D14).
- [ ] `ActingUserPicker` in the header (D10).
- [ ] Loading skeletons and an error state if the API is down.
- **Work laptop done when:** `npm run lint` and `npm run build` pass.
- **Personal laptop verified when:** the home page shows seeded contract/config cards from the real API; carousel, empty state, edit, and draft deletion work in the browser.

### A5 — Wizard shell + Step 1 Basic details
- [ ] `AvConfigWizardPage` in two modes: **new** (`/configurations/new`, empty form, nothing stored) and **edit** (`/configurations/:configId`, loads the latest version JSON by GUID and fills every field).
- [ ] Left step nav with completion state; `?step=` routing; unsaved-changes guard (D15).
- [ ] Step 1 fields incl. `DatePicker` (Popover + Calendar); end > start; dates outside the contract are allowed. Show a small hint if they are outside, not an error.
- [ ] Save draft: in new mode POST to create → receive GUID → replace the URL with `/configurations/<GUID>` (no duplicate on a second click); in edit mode POST drafts with `base_version`; on 409 show "someone else saved" toast with reload option.
- **Work laptop done when:** frontend lint/build pass and backend tests cover first-save/GUID/version behavior.
- **Personal laptop verified when:** "+" → fill Step 1 → Save creates a mini card with a new GUID; a second config gets a different GUID; Edit reloads values; another save increments the version without changing the GUID.

### A6 — Step 2 Turbines + Step 3 Formula & Alarm tree
- [ ] Step 2 turbine table lists **only the current contract's turbines** (from `GET /contracts/{contractId}` via the route's `contractId`), grouped by turbine group, select all / per group. Selected values are stored as UUIDs; codes are display-only.
- [ ] Step 3 formula `Select` filtered by calculation type (reset if type changes).
- [ ] `AlarmTree`: categories collapsible, tri-state category checkbox, required categories badged.
- [ ] Per-alarm turbine assignment multi-select limited to step-2 turbines (D4 behaviour).
- **Work laptop done when:** frontend lint/build and focused backend tests for contract scoping/readiness pass.
- **Personal laptop verified when:** assignments round-trip through save/reload, readiness reports alarm rules, and different contracts show only their own turbine lists.

### A7 — Step 4 Details + Review & Publish + history
- [ ] Park availability input (prefill D6), low/high wind variant selects.
- [ ] Review panel: read-only summary of all steps + readiness errors (click → jump to step).
- [ ] Publish button (disabled unless valid) → success toast, status badge updates.
- [ ] Version history drawer with diff between two versions.
- **Work laptop done when:** frontend lint/build and backend readiness/publish/overlap tests pass.
- **Personal laptop verified when:** full flow home page → "+" → four steps → save → publish works against PostgreSQL; overlapping publish is blocked and the mini card shows the updated status and timestamp.

### A8 — Tests, docs, cleanup
- [ ] Playwright e2e: happy path create→publish; blocked publish shows errors.
- [ ] Update `README.md` demo flow + endpoint list, `docs/ARCHITECTURE.md` data ownership, `docs/SESSION_NOTES.md`.
- [ ] Remove dead code from old contract-scoped configuration flow.
- **Work laptop done when:** pytest, frontend lint/build, and any non-browser test selectors pass.
- **Personal laptop verified when:** Playwright end-to-end tests pass against the Docker Compose stack.

### A9 — Stretch (only after A8)
- [ ] Custom alarm creation inside the tree.
- [ ] Clone an existing AV config.
- [ ] Hook into the AI milestone (summaries / "explain readiness errors") per `docs/PROJECT_ROADMAP.md` Milestone 7.

---

## 7. How to run & verify (Windows PowerShell)

```powershell
# Full stack
docker compose up --build

# Backend (from backend/)
uv sync
uv run alembic upgrade head
uv run python -m app.db.seed
uv run --extra dev pytest
uv run fastapi dev app/main.py

# Frontend (from frontend/)
npm install
npm run lint
npm run build
npm run dev
```

### Two-machine workflow

**Work laptop (no Docker Desktop):**

```powershell
# Backend (from backend/)
uv run --extra dev pytest

# Frontend (from frontend/)
npm ci
npm run lint
npm run build
```

These checks do not require Docker. Backend tests use in-memory SQLite, so
they do **not** prove PostgreSQL migrations or database-specific behaviour.
The frontend can be started for UI-only work, but API-backed flows require a
reachable backend and database.

**Personal laptop (Docker Desktop available):**

```powershell
git pull
git status --short
docker compose up --build
```

For A2, verify both paths without deleting the original database volume:

1. **Upgrade:** on a database at `202611220002`, capture an existing version's ID,
   snapshot, and checksum, then run `docker compose up --build` on A2.
   Check `docker compose exec backend alembic current` reports `202611260001`,
   confirm the version is unchanged under its default AV config, and verify
   that existing A1 pages still load.
2. **Fresh install:** stop the original stack with `docker compose down`
   (no `-v`), then start a separate project with
   `docker compose -p windconfig-a2-smoke up --build`. Check that the API
   lists six contracts and that North Ridge and Coastal Plains expose 10 and 8
   turbines with different IDs and nested alarms. Run the downgrade only on
   a disposable database.

Record the result in the Progress Log. `docker compose down -v` deletes the
selected project's local database volume; it is not required for A2.

Conventions to keep:
- Backend layering: `api/v1` router → `services` → `models`; Pydantic schemas in `schemas/`.
- Business rules live in the backend service layer; the UI only displays readiness results.
- All data is synthetic — never add real customer or proprietary data.
- Commit `package-lock.json` with any frontend dependency change.

---

## 8. Progress Log

Use `not run` until the check has actually happened. Update this log on both
machines as each check is completed; a pushed change is not by itself a
personal-laptop verification.

| Date | Milestone | Summary | Work laptop checks | Personal laptop Docker checks | Commit |
|---|---|---|---|---|---|
| 2026-11-25 | A0 | Plan and handoff document created. | N/A | N/A | (pending) |
| 2026-11-25 | A0 | User decisions: draft = full JSON of all wizard inputs; calc types TBA/YBA/RBA (NOWSI dropped); overlapping published configs block publish. | N/A | N/A | (pending) |
| 2026-11-25 | A0 | Home page design added from the user's reference screenshot: contract cards with info rows and an AV config carousel; new contract fields, acting user, extended `GET /contracts`; A4 rewritten. | N/A | N/A | (pending) |
| 2026-11-25 | A0 | User decisions: AV config dates may be outside contract dates; "±" icon ignored; ⋮ menu = Edit / Delete; each AV config gets its own GUID on first Save draft, used for edit and delete. New-config dialog removed ("+" opens an empty wizard). | N/A | N/A | (pending) |
| 2026-11-25 | A0 | Two-laptop workflow: work laptop has no Docker Desktop; use it for pytest/lint/build. Personal laptop runs Docker/PostgreSQL and full-stack checks. | N/A | N/A | (pending) |
| 2026-11-25 | A1 | Initialized shadcn/ui for Tailwind v3, installed routing/forms/date dependencies, added home/detail routes, preserved existing contract detail panels, and removed the milestone sidebar. | `npm run lint` and `npm run build` passed. | Not run; verify against Docker/API on personal laptop. | (pending) |
| 2026-11-25 | A1 | User accepted the defaults: calculation types share the same fields; published configurations cannot be deleted. | N/A | N/A | (pending) |
| 2026-11-26 | A2 | Added config GUIDs and per-config version storage, nested alarms, contract card fields, and six-contract synthetic seed data. Kept the A1 API compatible. | 17 pytest tests passed; frontend lint/build passed; Alembic SQL generated offline. | Not run; Docker engine unavailable. Verify actual PostgreSQL migration and seed on personal laptop. | (pending) |
