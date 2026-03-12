# General Development Standards

## 🛠️ Environment & Tools

- **Docker Focus**: Always assume execution is within the Docker container environment
- **Justfile Centralization**: The `justfile` is the single source of truth for all environment management — setup, running services, testing, and formatting
- **Dependency Management**: Use `uv` exclusively for managing dependencies and virtual environments
- **Configuration**: All environment-specific settings must be managed through environment variables or config files, never hardcoded

## 💻 Code Quality & Style

### Necessity and Scope
- Do not refactor or change code outside the immediate scope of the assigned task
- Delete all code that is no longer necessary (dead code, unused imports, stale features)

### Typing/Static Analysis
- Always fix all mypy issues in code you modify before creating a Pull Request
- Command: `cd backend && uv run mypy app/`

### Automated Formatting
Before completing a task, run in order:
1. `cd backend && uv run ruff format app/ tests/`
2. `cd backend && uv run ruff check --fix app/ tests/`

### Import Style
- Imports must always be at the top of the file
- Order: standard library → third-party → local application modules

### Code Standards
- No hard-coded strings or numbers — use constants, enums, or configuration
- Use Object-Oriented patterns to avoid methods with too many parameters

## 🏗️ Architecture

### Module Pattern
Every feature module follows: **routes → features → adapters**

```
app/<module>/
├── routes.py      # Thin FastAPI endpoints — instantiate features, return responses
├── features.py    # Business logic — Command/Result pattern, extends BaseFeature
├── models.py      # Pydantic schemas (request bodies, response models)
├── exceptions.py  # Domain exceptions raised by features, caught by app exception handlers
└── adapters/
    └── <store>.py # Data access layer (ORM, in-memory store, external clients)
```

### Feature Pattern
```python
class CreateFooFeature(BaseFeature):
    class Command(BaseModel):
        field: str

    class Result(BaseModel):
        item: FooRecord

    async def handle(self, command: Command) -> Result:
        # business logic here
        return self.Result(item=...)
```

### Route Pattern
```python
@router.post("", response_model=DataResponse[FooRecord], status_code=201)
async def create_foo(
    body: CreateFooRequest,
    store: FooStore = Depends(get_store),
    client: SovereignBrainClient = Depends(get_mcp_client),
) -> DataResponse[FooRecord]:
    result = await CreateFooFeature(store=store, client=client).handle(
        CreateFooFeature.Command(field=body.field)
    )
    return DataResponse(data=result.item)
```

### Response Envelopes
All API responses use the shared envelope types from `app/common/models.py`:
- `DataResponse[T]` — single item
- `ListResponse[T]` — collection with total count
- `StatusResponse` — status-only confirmation
- `ErrorResponse` — error detail (used in exception handlers)

### Exception Handling
Domain exceptions are defined per module (`exceptions.py`) and registered as global handlers in `app/app.py`. Routes never catch exceptions directly.

### MCP Client
`app/mcp/client.py` wraps the sovereign-brain SSE endpoint. In Docker, the backend connects via the `sovereign-net` external network at `http://mcp-server:8000/sse`. Override with `MCP_URL` env var for local development.

## ✅ Testing Standards

### Coverage Requirement
- 100% coverage is required. The CI pipeline enforces `--cov-fail-under=100`
- Run locally: `cd backend && uv run pytest`

### Test Patterns

| Test Type | Focus | Approach |
|-----------|-------|----------|
| **Route tests** | HTTP contract — status codes, response shape | Dependency-inject mock store/client via `app.dependency_overrides` |
| **Feature tests** | Business logic | Call `feature.handle(Command(...))` directly with mocked dependencies |
| **Adapter tests** | Data layer behaviour | Test the store/adapter class directly |
| **MCP client tests** | External MCP calls | Patch `sse_client` and `ClientSession` |

## 🌳 Git Workflow

### Branching Convention
- `feat/<description>` — new feature
- `fix/<description>` — bug fix
- `refactor/<description>` — refactor / tech debt
- `chore/<description>` — tooling, docs, CI

### Commit Messages
Use conventional commits: `feat: add session review endpoint`, `fix: handle empty MCP response`

### Pull Requests
PR description must include:
- Summary of changes
- How to manually test
- Coverage evidence
