<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0 (web app requirements added)
Modified principles: II. CLI Interface → II. API-First (expanded for web apps)
Added sections: Web Application Architecture, API Design, Security Requirements, Frontend Requirements, Deployment Requirements
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section references constitution
  ✅ spec-template.md - No direct references, compatible
  ✅ tasks-template.md - No direct references, compatible
  ✅ checklist-template.md - No direct references, compatible
  ✅ agent-file-template.md - No direct references, compatible
Follow-up TODOs: None
-->

# Flexible Table Constitution

## Core Principles

### I. Library-First
Every feature starts as a standalone library. Libraries must be self-contained, independently testable, and documented. Clear purpose required - no organizational-only libraries. This ensures modularity, reusability, and maintainability.

### II. API-First
Every library exposes functionality via well-defined APIs. For web applications: RESTful API endpoints with JSON responses. For CLI tools: stdin/args → stdout, errors → stderr. Support JSON + human-readable formats. APIs must be versioned, documented, and independently testable. This enables scriptability, automation, and integration with other tools.

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. This ensures correctness, prevents regressions, and drives design clarity.

### IV. Integration Testing
Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas, API endpoints, Frontend-backend integration, Database interactions. Integration tests validate end-to-end behavior and catch integration issues early. For web apps: API contract tests and E2E tests are mandatory.

### V. Observability
Text I/O ensures debuggability. Structured logging required for all operations. Error messages must be clear, actionable, and include context. This enables effective debugging and monitoring in production.

### VI. Versioning & Breaking Changes
MAJOR.MINOR.PATCH format. Breaking changes require MAJOR version bump, migration guide, and deprecation notices. Backward compatibility preferred when possible. This protects users and enables safe upgrades.

### VII. Simplicity
Start simple, YAGNI principles. Avoid premature optimization. Prefer explicit over implicit. Complexity must be justified with clear rationale. This keeps the codebase maintainable and understandable.

## Technology Stack

**Backend**:
- **Python Version**: Python 3.11.8 (MUST be used for all development and runtime)
- **Web Framework**: Dash (Plotly) - Python-native web framework with integrated frontend/backend
- **Rationale**: Python 3.11.8 provides performance improvements, better error messages, and modern language features while maintaining stability. All code, tests, and tooling must target this specific version. Dash provides native table filtering capabilities (dash_table.DataTable) and eliminates the need for separate frontend/backend development, making it well-suited for data analysis applications.

**Frontend**:
- **Framework**: [TO BE SPECIFIED - e.g., React, Vue, Svelte, or vanilla JS]
- **Build Tool**: [TO BE SPECIFIED - e.g., Vite, Webpack]
- **State Management**: [TO BE SPECIFIED if needed]

**Database**: [TO BE SPECIFIED - e.g., PostgreSQL, SQLite, MongoDB]

**Dependencies**: Dependencies should be minimal and well-justified. Use standard library when possible. External dependencies require documentation of rationale and version pinning.

**Testing Framework**: 
- Backend: pytest (standard for Python projects)
- Frontend: [TO BE SPECIFIED - e.g., Jest, Vitest]
- E2E: [TO BE SPECIFIED - e.g., Playwright, Cypress]

**Code Quality**: Type hints required for all public APIs. Linting and formatting tools must be configured and enforced for both backend and frontend.

## Web Application Architecture

**Separation of Concerns**: Frontend and backend MUST be separated into distinct modules/directories. Backend provides API endpoints only. Frontend consumes APIs and handles presentation logic.

**API Communication**: All frontend-backend communication via RESTful API endpoints. No direct database access from frontend. API responses MUST be JSON format with consistent error structure.

**State Management**: Frontend state should be managed explicitly. Server state and client state must be clearly separated. Use appropriate state management patterns for application complexity.

**Routing**: Frontend routing handled client-side. Backend provides API endpoints, not HTML pages (unless serving static assets).

## API Design

**RESTful Principles**: APIs MUST follow REST conventions. Use appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE). Resource-based URLs (e.g., `/api/v1/users/{id}`).

**API Versioning**: All APIs MUST be versioned (e.g., `/api/v1/`, `/api/v2/`). Breaking changes require new version. Maintain backward compatibility for at least one previous version.

**Request/Response Format**: 
- Request: JSON body for POST/PUT/PATCH, query parameters for filtering/pagination
- Response: Consistent JSON structure with `data`, `error`, `meta` fields
- Error responses: HTTP status codes + structured error messages

**Documentation**: All API endpoints MUST be documented (OpenAPI/Swagger preferred). Include request/response examples, error codes, and authentication requirements.

**Pagination**: List endpoints MUST support pagination. Default page size and maximum limits must be defined.

## Security Requirements

**Authentication & Authorization**: 
- All protected endpoints require authentication
- Use industry-standard authentication (e.g., JWT, OAuth2)
- Role-based access control (RBAC) for authorization
- Never expose sensitive credentials in frontend code

**Input Validation**: 
- All user inputs MUST be validated on backend (never trust frontend validation alone)
- Sanitize inputs to prevent injection attacks (SQL, XSS, etc.)
- Use parameterized queries for database operations

**HTTPS**: All production deployments MUST use HTTPS. Development may use HTTP for local testing only.

**Security Headers**: 
- Implement security headers (CORS, CSP, X-Frame-Options, etc.)
- CORS policy must be explicitly configured
- No wildcard CORS in production

**Sensitive Data**: 
- Never log sensitive information (passwords, tokens, PII)
- Use environment variables for secrets (never commit to repository)
- Encrypt sensitive data at rest and in transit

**Session Management**: 
- Secure session handling (httpOnly cookies, secure flag, sameSite)
- Implement CSRF protection
- Session timeout and refresh token strategy

## Frontend Requirements

**Responsive Design**: Applications MUST be responsive and work on mobile, tablet, and desktop viewports. Mobile-first approach preferred.

**Accessibility**: 
- Follow WCAG 2.1 Level AA guidelines minimum
- Semantic HTML, ARIA labels where needed
- Keyboard navigation support
- Screen reader compatibility

**Performance**:
- Initial page load < 3 seconds on 3G connection
- Lazy loading for images and code splitting for routes
- Minimize bundle size, optimize assets

**Browser Support**: [TO BE SPECIFIED - e.g., Latest 2 versions of Chrome, Firefox, Safari, Edge]

**Error Handling**: 
- User-friendly error messages (no technical stack traces to users)
- Graceful degradation when API calls fail
- Loading states and feedback for async operations

## Deployment Requirements

**Environment Separation**: 
- Development, Staging, Production environments MUST be separate
- Environment-specific configuration via environment variables
- No hardcoded environment-specific values

**CI/CD**: 
- Automated testing in CI pipeline (unit, integration, E2E)
- Automated deployment to staging
- Manual approval required for production deployment
- Rollback strategy must be defined

**Monitoring & Logging**: 
- Application logs aggregated and searchable
- Error tracking and alerting
- Performance monitoring (response times, error rates)
- Uptime monitoring

**Database Migrations**: 
- All schema changes via versioned migration scripts
- Migrations must be reversible
- Test migrations in staging before production

**Backup & Recovery**: 
- Regular automated backups for production data
- Backup restoration procedure documented and tested
- Recovery time objective (RTO) and recovery point objective (RPO) defined

## Development Workflow

**Branch Strategy**: Feature branches from main. Each feature branch corresponds to a specification in `specs/[###-feature-name]/`.

**Code Review**: All PRs must verify constitution compliance. Complexity must be justified. Tests must pass before merge.

**Documentation**: Every public API must have docstrings. README must be kept up-to-date. Breaking changes require migration guides.

**Testing Gates**: 
- Unit tests for all library functions and components
- Integration tests for API endpoints and contract changes
- E2E tests for critical user journeys
- All tests must pass before merge
- Test coverage should be maintained or improved (minimum 80% for backend, 70% for frontend)

**Frontend/Backend Coordination**: 
- API contracts defined before implementation
- Frontend and backend can be developed in parallel using contract mocks
- Contract changes require coordination and versioning

## Governance

This constitution supersedes all other practices. Amendments require:
- Documentation of rationale
- Approval process
- Migration plan if breaking changes
- Version bump according to semantic versioning

All PRs/reviews must verify compliance with constitution principles. Complexity must be justified in PR descriptions. Use `.specify/templates/` for consistent documentation structure.

**Version**: 1.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
