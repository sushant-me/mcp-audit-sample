# mcp-audit-sample

**A deliberately risky MCP server, and the audit report I would return for it.**

Every security review is sold before it is bought, and the hardest part of that is that
nobody can see what the report looks like. So this is a small server — the kind of
vendor integration that ends up connected to an agent — plus the deliverable: findings
with severity, the exact declaration text as evidence, the mechanism, the fix, and a
generated policy the runtime gate enforces.

**Synthetic target, clearly labelled.** I wrote the server. This is not a client
engagement, and it is not a vulnerability in anyone's product.

## What the report found

Ten tools; **ten findings** and **two tools that are clean**.

| severity | finding |
|---|---|
| **critical** | `set_model_response` collides with a name the framework installs outside the tool table, so it displaces the primitive and wins dispatch |
| **high** | `get_alerts` carries an instruction in the **Unicode tag block** — invisible ASCII at zero width |
| **high** | `get_cost_report`'s description tells the model to add credentials found in the account to its summary |
| **high** | `delete_budget` permanently deletes things and declares `readOnlyHint: true`, removing the confirmation step |
| **high** | `get_alertѕ` is a look-alike of `get_alerts` (Cyrillic `ѕ`) |
| **medium** | `run_diagnostic` takes an unconstrained command string |
| **medium** | `get_alertѕ` uses a non-ASCII name |
| **low** | a URL in a description; a tool with no description |

The full report is [`audit/AUDIT.md`](audit/AUDIT.md), including what was **not** tested.

## Run it

```bash
pip install "git+https://github.com/sushant-me/mcpaudit@v0.1.1"
python3 demo.py            # audit, then verify every finding and artifact
python3 demo.py --drift    # edit one description and watch the lock report it
```

`demo.py` exits non-zero when a finding stops reproducing, when an unexpected one
appears, when the two clean tools are no longer clean, or when the committed policy is
not what the current declarations generate. **A report asserting that specific problems
exist in a specific revision is a claim, and this is its test** — otherwise the report
rots into describing a server that has since been fixed.

The server speaks JSON-RPC over stdio, so you can point a client at it:

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  | python3 server/server.py
```

`tools/call` is deliberately **not** implemented: this server exists to be reviewed, not
executed, which keeps the boundary between declarations and behaviour unambiguous.

## What is in the box

| path | what it is |
|---|---|
| `server/tools_list.json` | the captured `tools/list` payload — what a client receives |
| `server/server.py` | the server that serves it, stdlib only |
| `audit/AUDIT.md` | **the deliverable**: findings, evidence, mechanism, fix, limits |
| `audit/policy.toml` | the policy the gate enforces, generated from the same declarations |
| `audit/tools.lock.json` | every field of every declaration, so a later change is a diff |
| `demo.py` | reproduces the report and fails if it drifts |

## The part that makes it useful rather than decorative

A report somebody has to translate into rules is where a review becomes a wish list
nobody maintains. So the audit emits the policy: the collision and the
instruction-carrying description are **denied**, clean read-only tools are **allowed**,
and everything else **escalates** — including anything the audit never saw, because the
gate refuses by default. The lock file turns the tool-poisoning shape — same name, same
schema, new prose — into a reported diff instead of a silent steering of the agent.

## Limitations, stated here rather than in a footnote

- **Declarations, not behaviour.** A server can declare a clean tool list and do
  something else when called. This review never runs the server.
- **A clean report would not be a safe server.** Absence of a known-bad pattern is
  absence of evidence.
- **The confusables table is a curated subset**, not the full Unicode data.
- **Tool results are a separate channel.** This covers what the server declares, not
  what it returns; results need the same treatment.

## Licence

MIT. Reproduce it, adapt the server, and re-run the audit against your own.
