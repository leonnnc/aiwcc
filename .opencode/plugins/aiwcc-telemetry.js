import { Plugin } from "@opencode/plugin"

const BRIDGE_URL = "http://127.0.0.1:8765/api/telemetry"
const ALLOWED_EVENTS = new Set([
  "session.created",
  "session.execution.started",
  "session.execution.succeeded",
  "session.execution.failed",
  "session.tool.called",
  "session.tool.success",
  "session.tool.failed",
  "session.idle",
  "session.model.selected",
  "session.agent.selected",
  "session.shell.started",
  "session.shell.ended",
  "permission.asked",
  "permission.replied",
  "mcp.status.changed",
])

export default Plugin.define({
  id: "aiwcc-telemetry",
  setup(ctx) {
    const controller = new AbortController()

    const publish = async (type, created) => {
      try {
        await fetch(BRIDGE_URL, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ type, created }),
          signal: controller.signal,
        })
      } catch {
        // Bridge offline: telemetry is best-effort and must never block OpenCode.
      }
    }

    void publish("aiwcc.plugin.ready", Date.now())

    void (async () => {
      try {
        for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
          if (!ALLOWED_EVENTS.has(event.type)) continue
          await publish(event.type, event.created)
        }
      } catch (error) {
        if (!controller.signal.aborted) {
          console.warn("[AIWCC] Event subscription stopped:", error)
        }
      }
    })()

    return () => controller.abort()
  },
})
