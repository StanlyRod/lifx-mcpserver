# LIFX MCP Server

An MCP server that lets an AI assistant (like Claude or ChatGPT) to control LIFX smart bulbs. Ask Claude to "turn on the bedroom light" or "make the restroom light blue," and this server sends the matching command to your bulbs through the LIFX cloud API.

It currently controls two bulbs, **Bedroom** and **Restroom**, and can also act on every bulb on the account at once.

---

## How it works

```
Claude  ──(MCP)──▶  STA MCP Server  ──(HTTPS)──▶  LIFX Cloud API  ──▶  Your bulbs
```

1. Claude sees a list of tools this server offers, such as `turn_bedroom_light_on`.
2. When you ask for something, Claude calls the matching tool.
3. The server turns that into a web request to `api.lifx.com`, signed with your LIFX token.
4. LIFX changes the bulb, and the server sends back a short message saying whether it worked.

The project is split into three Python files:

| File | What it does |
|---|---|
| `lfx_controlers.py` | Does the real work. Builds the LIFX requests and sends them. Shared by both servers below. |
| `lfxlocalmcp.py` | **For local testing only.** Runs on your own computer and talks to Claude Desktop over standard input/output (stdio). Use it to try out changes before deploying them. |
| `lfxremotemcp.py` | **The cloud server.** This is the version that runs on Azure. It talks to Claude over HTTP on port `3131`, and it's the file the Docker image packages. |

Both server files offer the same tools, so a tool that works in local testing behaves the same way in the cloud. When you change a tool, update it in both files.

### Inside `lfx_controlers.py`

- **Token check at startup.** The server reads your LIFX token from the `LIFXKEY` environment variable (or a `.env` file). If it's missing or blank, the server stops right away with a clear error instead of starting up and failing on every request.
- **One shared connection to LIFX.** Instead of opening a new connection for every request, the server reuses one shared HTTP client. This makes repeated commands faster. The client allows up to 10 connections at once, keeps up to 5 open between requests for 30 seconds, and gives each request 20 seconds before timing out.
- **Clear results and safe logs.** Every request is logged with the bulb name and the result. The token never appears in the logs.

---

## Available tools

| Tool | What it does | Inputs |
|---|---|---|
| `turn_bedroom_light_on` | Turns the Bedroom bulb on | `duration` (optional) |
| `turn_bedroom_light_off` | Turns the Bedroom bulb off | `duration` (optional) |
| `turn_restroom_light_on` | Turns the Restroom bulb on | `duration` (optional) |
| `turn_restroom_light_off` | Turns the Restroom bulb off | `duration` (optional) |
| `toggle_sweep_all_bulbs` | Flips **every** bulb on the account. Lights that are on turn off, and lights that are off turn on. | `duration` (optional) |
| `set_bulb_brightness` | Sets how bright one bulb is | `intensity` (0–100), `bulb_name` |
| `set_bulb_color` | Changes the color of one bulb | `color`, `bulb_name` |

**About the inputs**

- `duration` is the fade time in seconds, from 0 to 100. The default is 0, which means instant.
- `intensity` is a percentage. `100` is full brightness and `0` is the dimmest. The server converts it to the 0.0–1.0 scale LIFX expects.
- `color` accepts anything LIFX understands, for example `"red"`, `"blue"`, `"#ff8800"`, `"kelvin:2700"`, or `"hue:120 saturation:1.0 brightness:1.0"`. Changing the color doesn't turn a bulb on, so a bulb that's off stays off.
- `bulb_name` must match the bulb's label in the LIFX app. The server capitalizes the first letter and lowercases the rest, so `"bedroom"` becomes `Bedroom`. A label like `LivingRoom` would not match, because it becomes `Livingroom`.

**What comes back**

Every tool returns a short sentence:

| Result | Message |
|---|---|
| It worked | `Successfully performed action on Bedroom bulb.` |
| LIFX rejected the request | `Failed to control Bedroom: HTTP 401` (the number tells you why, for example 401 = bad token, 404 = bulb label not found, 429 = too many requests) |
| LIFX took too long | `Failed to control Bedroom: timeout.` |
| Couldn't reach LIFX | `Failed to control Bedroom: network error.` |
| Anything else | `Unexpected error controlling Bedroom.` |

Errors are returned as text rather than crashing the server. Out-of-range inputs, such as a duration of 150, are rejected before any request is sent.

---

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for installing dependencies (or plain `pip` with `requirements.txt`)
- A LIFX account with your bulbs set up
- A LIFX personal access token. Create one at [cloud.lifx.com](https://cloud.lifx.com) under **Settings → Personal access tokens**.

Main libraries: `mcp` (the MCP framework, using FastMCP), `httpx` (sends the web requests), and `python-dotenv` (loads your token from a `.env` file).

---

## Setup

1. Install the dependencies:

   ```bash
   uv sync
   ```

2. Create a file named `.env` in the project folder and add your LIFX token:

   ```
   LIFXKEY=your_lifx_token_here
   ```

   Keep this file out of Git. Anyone with this token can control your lights.

---

## Local testing (`lfxlocalmcp.py`)

`lfxlocalmcp.py` is for testing on your own computer only. Use it to check new tools or fixes with Claude Desktop before you deploy them to the cloud. It isn't meant for everyday use.

Start it to check that it runs:

```bash
uv run lfxlocalmcp.py
```

To use it from Claude Desktop, add it to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sta-mcpserver": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/project", "run", "lfxlocalmcp.py"]
    }
  }
}
```

Restart Claude Desktop, and the light tools will show up for testing.

---

## Running in the cloud (`lfxremotemcp.py`)

`lfxremotemcp.py` is the server that runs on Azure and that Claude connects to day to day. The `Dockerfile` packages it together with `lfx_controlers.py`, using a Python 3.13 image.

Before deploying, you can build and run the container on your computer to make sure it starts:

```bash
docker build -t stamcpserver-dockerimage .
docker run -p 3131:3131 -e LIFXKEY=your_lifx_token_here stamcpserver-dockerimage
```

The server then listens at:

```
http://localhost:3131/mcp
```

Things to know about the cloud server:

- It listens on all network addresses (`0.0.0.0`) on port `3131`.
- It is **stateless** and replies with plain JSON, so each request stands alone. This suits cloud hosting, where the server may restart or scale at any time.
- The `.env` file is **not** copied into the image. The Container App must have `LIFXKEY` set as an environment variable, or the server won't start.

### Azure Container Apps setup

1. Create a Container App from the Docker Hub image, with ingress turned on and the target port set to `3131`.
2. Set the `LIFXKEY` environment variable on the Container App.
3. Add the app's public URL, ending in `/mcp`, as a custom connector in Claude.

If Claude says the connector needs to reconnect, check that the Container App is running. If it is set to scale to zero, the first request after a quiet period may time out while it starts up. Trying again usually works.

---

## Automatic deployment (GitHub Actions)

Every push to the `master` branch deploys the cloud server automatically. The workflow:

1. Checks out the code.
2. Logs in to Docker Hub.
3. Builds the Docker image and pushes it with two tags: `latest` and the commit ID (`github.sha`).
4. Logs in to Azure.
5. Updates the `sta-test-mcpserver` Container App to the new image, using the commit ID tag so each deploy points to an exact version.

The workflow needs these repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | What it is |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token |
| `AZURE_CREDENTIALS` | Service principal login for Azure (JSON) |
| `AZURE_RESOURCE_GROUP` | The resource group that holds the Container App |
| `LIFXKEY` | Your LIFX personal access token |

---

## Adding a new bulb

1. Make sure the bulb has a clear label in the LIFX app, for example `Kitchen`.
2. Add on and off tools for it in **both** `lfxlocalmcp.py` and `lfxremotemcp.py`:

   ```python
   @mcp.tool()
   async def turn_kitchen_light_on(duration: int = 0) -> str:
       """Turn the kitchen LIFX light ON."""
       return await stc.bulb_on("Kitchen", duration)
   ```

3. Test it locally with `lfxlocalmcp.py`, then push to `master` so GitHub Actions deploys it to the cloud.

`set_bulb_brightness` and `set_bulb_color` already work with any bulb by name, so they need no changes.

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Server stops right away with `LIFXKEY is required` | The token isn't set. Add it to `.env` locally, or set `LIFXKEY` on the Container App. |
| `HTTP 401` | The LIFX token is wrong or has been revoked. Create a new one. |
| `HTTP 404` | No bulb has that label. Check the name in the LIFX app. |
| `HTTP 429` | Too many requests to LIFX in a short time. Wait a minute and try again. |
| Timeouts on the first request | The Container App was asleep (scaled to zero) and is starting up. Try again. |

---

## Project files

```
├── lfx_controlers.py   # LIFX API calls (shared logic)
├── lfxlocalmcp.py      # Local testing only (stdio)
├── lfxremotemcp.py     # Cloud server on Azure (HTTP, port 3131)
├── Dockerfile          # Container image for the cloud server (Python 3.13)
├── pyproject.toml      # Project settings and dependencies
├── requirements.txt    # Pinned dependencies (exported by uv, used by Docker)
├── uv.lock             # Exact dependency versions for uv
├── .github/workflows/  # GitHub Actions deployment workflow
└── .env                # Your LIFX token (not committed)
```
