# Tasks: Advanced Table Filtering Web Application

**Input**: Design documents from `/specs/001-table-filter-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, but TDD is mandatory per Constitution. Test tasks are included to comply with Constitution requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (src/, src/components/, src/lib/, src/utils/, tests/, tests/unit/, tests/integration/, tests/fixtures/)
- [x] T002 Initialize Python 3.11.8 project with requirements.txt (dash>=2.14.0, pandas>=2.0.0, openpyxl>=3.1.0, pytest>=7.4.0)
- [x] T003 [P] Configure linting and formatting tools (black, flake8, mypy) in pyproject.toml or setup.cfg
- [x] T004 [P] Create README.md with project overview and installation instructions
- [x] T005 [P] Setup .gitignore for Python project (__pycache__, .venv, *.pyc, etc.)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create base utility modules in src/utils/validators.py (file validation functions)
- [x] T007 [P] Create base utility modules in src/utils/formatters.py (data formatting helpers)
- [x] T008 Configure logging infrastructure in src/utils/logging_config.py (structured logging setup)
- [x] T009 Create error handling utilities in src/utils/error_handlers.py (user-friendly error messages)
- [x] T010 [P] Setup test fixtures directory with sample files (tests/fixtures/sample.csv, tests/fixtures/sample.xlsx, tests/fixtures/sample.json)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Load and Display Table Data (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload table data files (CSV, Excel, JSON) and view them in a browser-based table interface. This is the foundation that enables all other functionality.

**Independent Test**: Can be fully tested by uploading a CSV file and verifying that the data appears correctly in a table format. This delivers the core value of viewing tabular data in a browser without requiring any filtering functionality.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T011 [P] [US1] Unit test for CSV parsing in tests/unit/test_data_parser.py (test_parse_csv_file)
- [x] T012 [P] [US1] Unit test for Excel parsing in tests/unit/test_data_parser.py (test_parse_excel_file)
- [x] T013 [P] [US1] Unit test for JSON parsing in tests/unit/test_data_parser.py (test_parse_json_file)
- [x] T014 [P] [US1] Unit test for column type detection in tests/unit/test_data_processor.py (test_detect_column_types)
- [x] T015 [P] [US1] Unit test for duplicate column name handling in tests/unit/test_data_processor.py (test_handle_duplicate_columns)
- [x] T016 [US1] Integration test for file upload flow in tests/integration/test_file_upload_flow.py (test_csv_upload_to_display)

### Implementation for User Story 1

- [x] T017 [P] [US1] Create data parser module in src/lib/data_parser.py (parse_csv, parse_excel, parse_json functions)
- [x] T018 [P] [US1] Create data processor module in src/lib/data_processor.py (detect_column_types, handle_duplicate_columns, convert_to_json_format functions)
- [x] T019 [P] [US1] Create file validator in src/utils/validators.py (validate_file_type, validate_file_size functions)
- [x] T020 [US1] Create upload component in src/components/upload_component.py (dcc.Upload component with drag-and-drop)
- [x] T021 [US1] Create table component in src/components/table_component.py (dash_table.DataTable wrapper with virtual scrolling)
- [x] T022 [US1] Implement file upload callback in src/app.py (upload_file callback: validate → parse → store → display)
- [x] T023 [US1] Add error handling for file upload failures in src/app.py (invalid type, size limit, parsing errors)
- [x] T024 [US1] Add logging for file upload events in src/app.py (structured logging for upload success/failure)
- [x] T025 [US1] Create main Dash app layout in src/app.py (upload component, table component, status display)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can upload CSV/Excel/JSON files and see them displayed in a table.

---

## Phase 4: User Story 2 - Basic Column Filtering (Priority: P2)

**Goal**: Enable users to filter table data by individual column values to quickly find specific rows. This enables basic data exploration and analysis.

**Independent Test**: Can be fully tested by loading a table, applying a filter to a column (e.g., "show only rows where Status = 'Active'"), and verifying that only matching rows are displayed. This delivers the ability to narrow down data to relevant subsets.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T026 [P] [US2] Unit test for text filter operations in tests/unit/test_filter_engine.py (test_text_equals, test_text_contains, test_text_starts_with, test_text_ends_with)
- [x] T027 [P] [US2] Unit test for numeric filter operations in tests/unit/test_filter_engine.py (test_numeric_equals, test_numeric_greater_than, test_numeric_less_than, test_numeric_between)
- [x] T028 [P] [US2] Unit test for date filter operations in tests/unit/test_filter_engine.py (test_date_equals, test_date_before, test_date_after, test_date_between)
- [x] T029 [US2] Integration test for single filter application in tests/integration/test_filter_application.py (test_apply_text_filter, test_apply_numeric_filter)

### Implementation for User Story 2

- [x] T030 [P] [US2] Create filter engine module in src/lib/filter_engine.py (apply_single_filter function with operator support)
- [x] T031 [P] [US2] Create filter UI component in src/components/filter_ui.py (column dropdown, operator dropdown, value input, apply button)
- [x] T032 [US2] Implement single column filter callback in src/app.py (apply_column_filter callback: retrieve data → apply filter → update display)
- [x] T033 [US2] Add filter state management in src/app.py (store FilterCondition in dcc.Store)
- [x] T034 [US2] Implement clear filter functionality in src/app.py (clear_filter callback: remove condition → restore original data)
- [x] T035 [US2] Add row count display update in src/app.py (show filtered rows count vs total rows)
- [x] T036 [US2] Add filter operator validation in src/lib/filter_engine.py (validate operator for column data type)
- [x] T037 [US2] Add null value handling in src/lib/filter_engine.py (exclude null values from matches unless explicitly filtered)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can upload files, view tables, and apply single column filters.

---

## Phase 5: User Story 3 - Advanced Multi-Column Filtering (Priority: P3)

**Goal**: Enable users to apply multiple filters across different columns simultaneously and combine them with logical operators (AND/OR) to perform complex data analysis. This fulfills the "自由自在" requirement.

**Independent Test**: Can be fully tested by loading a table, applying multiple filters to different columns (e.g., "Status = 'Active' AND Amount > 1000"), and verifying that only rows matching all conditions are displayed. This delivers the ability to perform complex data analysis without leaving the browser.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US3] Unit test for AND logic combination in tests/unit/test_filter_engine.py (test_multiple_filters_and_logic)
- [x] T039 [P] [US3] Unit test for OR logic combination in tests/unit/test_filter_engine.py (test_multiple_filters_or_logic)
- [x] T040 [US3] Integration test for multiple filter combination in tests/integration/test_filter_application.py (test_and_combination, test_or_combination)

### Implementation for User Story 3

- [x] T041 [US3] Extend filter engine for multiple filters in src/lib/filter_engine.py (apply_multiple_filters function with AND/OR logic)
- [x] T042 [US3] Add filter set management in src/app.py (FilterSet entity with conditions list and logic_operator)
- [x] T043 [US3] Extend filter UI for multiple filters in src/components/filter_ui.py (multiple filter rows, AND/OR radio buttons)
- [x] T044 [US3] Implement filter combination callback in src/app.py (apply_filter_combination callback: retrieve all conditions → apply with logic → update display)
- [x] T045 [US3] Add filter state persistence in src/app.py (maintain FilterSet in dcc.Store across interactions)
- [x] T046 [US3] Add "no results" message handling in src/app.py (display clear message when filters result in zero matches)
- [x] T047 [US3] Add filter condition limit validation in src/lib/filter_engine.py (maximum 10 conditions to prevent performance issues)
- [x] T048 [US3] Add immediate filter update on condition change in src/app.py (real-time updates when any filter condition changes)

**Checkpoint**: At this point, all user stories should now be independently functional. Users can upload files, view tables, apply single filters, and combine multiple filters with AND/OR logic.

---

## Phase 6: Additional Features (Cross-Story)

**Purpose**: Features that enhance multiple user stories

- [x] T049 [P] Implement export filtered results callback in src/app.py (export_filtered_data callback: retrieve filtered data → convert to CSV → trigger download)
- [x] T050 [P] Implement column visibility toggle callback in src/app.py (toggle_column_visibility callback: show/hide columns)
- [x] T051 [P] Add column sorting support in src/components/table_component.py (enable sort_action='native' in DataTable)
- [x] T052 Add virtual scrolling optimization in src/components/table_component.py (page_action='native' for datasets > 1,000 rows)
- [x] T053 Add performance monitoring in src/utils/logging_config.py (log filter operation times, file upload times)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Documentation updates in README.md (usage examples, API documentation)
- [x] T055 Code cleanup and refactoring (review all modules for consistency)
- [x] T056 [P] Performance optimization across all stories (optimize DataFrame operations, reduce callback frequency)
- [x] T057 [P] Additional unit tests in tests/unit/ (edge cases, error conditions)
- [x] T058 Security hardening (input sanitization review, error message review)
- [x] T059 Run quickstart.md validation (verify all steps work as documented)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Additional Features (Phase 6)**: Depends on User Story 2 completion (basic filtering required)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 completion (needs table display to filter)
- **User Story 3 (P3)**: Depends on User Story 2 completion (needs single filter functionality)

### Within Each User Story

- Tests (included per Constitution TDD requirement) MUST be written and FAIL before implementation
- Library modules (lib/) before components
- Components before callbacks
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T007, T010)
- Once Foundational phase completes, User Story 1 can start
- All tests for a user story marked [P] can run in parallel
- Library modules within a story marked [P] can run in parallel
- Additional Features (Phase 6) tasks marked [P] can run in parallel after US2 completion

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for CSV parsing in tests/unit/test_data_parser.py"
Task: "Unit test for Excel parsing in tests/unit/test_data_parser.py"
Task: "Unit test for JSON parsing in tests/unit/test_data_parser.py"
Task: "Unit test for column type detection in tests/unit/test_data_processor.py"
Task: "Unit test for duplicate column name handling in tests/unit/test_data_processor.py"

# Launch all library modules for User Story 1 together:
Task: "Create data parser module in src/lib/data_parser.py"
Task: "Create data processor module in src/lib/data_processor.py"
Task: "Create file validator in src/utils/validators.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add Additional Features → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (all tasks)
   - Developer B: Prepare for User Story 2 (review US1 completion)
3. Once User Story 1 is done:
   - Developer A: User Story 2
   - Developer B: User Story 3 (after US2)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Test tasks are included per Constitution TDD requirement, even though not explicitly requested in spec

