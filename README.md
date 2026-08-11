# Agent Readiness

**Know if your engineering environment is ready for AI coding agents. Fix the gaps. Prove what is ready.**

Agent Readiness is an open-source toolkit for measuring and improving how prepared software repositories are for AI-assisted and agentic engineering.

## Why Agent Readiness?

Giving engineers access to AI coding agents is easy.

Making an engineering environment ready for them is harder.

Agent Readiness evaluates the foundations agents depend on:

- Repository context
- Architecture guidance
- Testing
- Security controls
- Secrets protection
- Agent instructions
- MCP and tool governance
- Human review
- Observability
- Evidence and traceability

## The Agent Readiness Score

```text
Agent Readiness
──────────────────────────────

Repository Context       82  PASS
Architecture             74  WARN
Testing                  91  PASS
Security                 78  WARN
Secrets Protection      100  PASS
MCP / Tool Governance    45  WARN
Agent Instructions       85  PASS
Human Review             70  WARN
Observability            55  WARN
Evidence                 80  PASS

Overall Readiness: 76 / 100
Verdict: READY WITH CONDITIONS
```

Every score should be explainable by repository evidence and paired with actionable recommendations.

## Vision

Agent Readiness aims to help engineering teams move from:

**individual AI experimentation → repeatable agentic engineering**

without sacrificing architecture, security, quality, governance, or human accountability.

## Planned CLI

```bash
agent-readiness assess .
agent-readiness explain security
agent-readiness report . --format markdown
agent-readiness policy-check .
```

## Principles

**Evidence over assumptions.**  
Every assessment should be explainable.

**Vendor neutral.**  
No dependency on a particular AI coding agent or model.

**Engineering outcomes first.**  
The goal is better software delivery—not more generated code.

**Humans remain accountable.**  
AI-generated changes remain engineering changes.

## Status

🚧 **Early development — V0.1**

The initial scoring model and CLI are being developed in public.

Contributions, ideas, and practitioner feedback are welcome.

## License

Apache-2.0
