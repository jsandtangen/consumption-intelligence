## Core principles

### 1. Keep the implementation as simple as possible

Simplicity is the highest priority.

Always prefer the smallest amount of code that solves the problem correctly, securely, and reliably.

- Do not over-engineer.
- Do not introduce abstractions, classes, layers, helper functions, dependencies, configuration, or architecture unless they provide a clear benefit.
- Prefer existing code and existing dependencies over creating new systems.
- Avoid premature optimization and unnecessary flexibility for hypothetical future requirements.
- If two solutions achieve roughly the same result, choose the simpler one with less code and fewer moving parts.
- Reduce duplication when it genuinely simplifies the code, but do not create abstractions only to avoid a few repeated lines.
- Code should be easy to understand, modify, test, and debug.
- Security, correctness, and reliability must not be sacrificed just to reduce line count.

The goal is not literally the fewest possible lines. The goal is the **least complexity necessary to achieve the required functionality safely and correctly**.

Before adding code, ask:
1. Is this actually necessary?
2. Can the same result be achieved with existing code?
3. Is there a simpler solution?
4. Am I solving a real requirement or a hypothetical future problem?

### 2. Keep this file up to date

Treat `AGENTS.md` as living project knowledge.

Whenever you discover important information that will affect future development, update this file.

Examples include:
- important architectural decisions
- project conventions
- recurring constraints
- important commands or workflows
- known pitfalls
- security requirements
- decisions about dependencies or technologies
- important lessons learned while implementing or debugging

Only store information that is likely to remain useful in future tasks.

Do not add:
- temporary debugging details
- one-off observations
- obvious information that can easily be inferred from the code
- long explanations when a short rule is enough

When new information conflicts with existing information in this file, update or replace the outdated information instead of simply appending another rule.

Keep `AGENTS.md` concise, current, and useful.