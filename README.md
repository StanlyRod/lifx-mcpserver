# LIFX MCP Server

An MCP server that lets an AI assistant (like Claude or ChatGPT) control your LIFX smart bulbs. Ask your assistant to "turn on the bedroom light" or "make the restroom light blue," and this server sends the matching command to your bulbs through the LIFX cloud API.

You can run it on your own computer, or deploy it to any cloud service you like, such as AWS, Azure, Google Cloud, or Railway. Cloud hosting is optional.

The included tools control two bulbs labeled **Bedroom** and **Restroom**, and can also act on every bulb on your account at once. You can rename these or add your own bulbs (see [Adding a new bulb](#adding-a-new-bulb)).

---

## How it works

```
AI assistant  ──(MCP)──▶  LIFX MCP Server  ──(HTTPS)──▶  LIFX Cloud API  ──▶  Your bulbs
```

1. Your assistant sees a list of tools this server offers, such as `turn_bedroom_light_on`.
2. When you ask for something, your assistant calls the matching tool.
3. The server turns that into a web request to `api.lifx.com`, signed with your LIFX token.
4. LIFX changes the bulb, and the server sends back a short message saying whether it worked.

The project is split into three Python files:

| File | What it does |
|---|---|
| `lfx_controlers.py` | Does the real work. Builds the LIFX requests and sends them. Shared by both servers below. |
| `lfxlocalmcp.py` | Local version. Runs on your own computer and talks to your assistant app (for example Claude Desktop) over standard input/output (stdio). Good for personal use or for trying out changes. |
| `lfxremotemcp.py` | Web version. Talks to your assistant over HTTP on port `3131`. Use it when you want to host the server somewhere and connect to it by URL. It's the file the Docker image packages. |

Both server files offer the same tools, so a tool that works locally behaves the same way when hosted. When you change a tool, update it in both files.

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
| `get_all_lights_status` | Lists light IDs, names, connectivity, power, brightness, and color without changing any lights | `only_connected` (optional, defaults to `true`) |

**About the inputs**

- `duration` is the fade time in seconds, from 0 to 100. The default is 0, which means instant.
- `intensity` is a percentage. `100` is full brightness and `0` is the dimmest. The server converts it to the 0.0–1.0 scale LIFX expects.
- `color` accepts anything LIFX understands, for example `"red"`, `"blue"`, `"#ff8800"`, `"kelvin:2700"`, or `"hue:120 saturation:1.0 brightness:1.0"`. Changing the color doesn't turn a bulb on, so a bulb that's off stays off.
- `bulb_name` must match the bulb's label in the LIFX app. The server capitalizes the first letter and lowercases the rest, so `"bedroom"` becomes `Bedroom`. A label like `LivingRoom` would not match, because it becomes `Livingroom`.
- `only_connected` controls the status listing. The default, `true`, includes connected lights whether on or off. Set it to `false` to also include disconnected lights, whose reported states may be outdated.

**What comes back**

The tools that change lights return a short sentence:

| Result | Message |
|---|---|
| It worked | `Successfully performed action on Bedroom bulb.` |
| LIFX rejected the request | `Failed to control Bedroom: HTTP 401` (the number tells you why, for example 401 = bad token, 404 = bulb label not found, 429 = too many requests) |
| LIFX took too long | `Failed to control Bedroom: timeout.` |
| Couldn't reach LIFX | `Failed to control Bedroom: network error.` |
| Anything else | `Unexpected error controlling Bedroom.` |

Errors are returned as text rather than crashing the server. Out-of-range inputs, such as a duration of 150, are rejected before any request is sent.

`get_all_lights_status` returns a list of light records containing `id`, `name`, `connected`, `power`, `brightness_percent`, and `color`. The color includes an `approximate_name` alongside the original hue, saturation, and Kelvin values. The name is an estimate, and missing readings are returned as `null`. An off light can still report a nonzero brightness setting. Request failures are returned as MCP tool errors.

For example, ask your assistant "Which lights are on?" or "Show the brightness and color of all my connected lights." The status tool reads information without changing power, brightness, or color.

---

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for installing dependencies (or plain `pip` with `requirements.txt`)
- A LIFX account with your bulbs set up
- A LIFX personal access token. Create one at [cloud.lifx.com](https://cloud.lifx.com) under **Settings → Personal access tokens**.
- Docker, only if you want to run the server in a container or deploy it to the cloud

Main libraries: `mcp` v2 (the MCP framework, using `MCPServer`), `httpx` (sends the LIFX web requests), and `python-dotenv` (loads your token from a `.env` file). The SDK uses `httpx2` internally; both HTTP libraries are installed because the LIFX controller still uses `httpx`.

The dependency versions are locked in `uv.lock` and exported with hashes to `requirements.txt` for Docker:

| Package | Locked version |
|---|---|
| `mcp` | 2.3.0 |
| `requests` | 2.34.2 |
| `pydantic` | 2.14.1 |
| `python-dotenv` | 1.2.4 |
| `starlette` | 1.10.0 |
| `uvicorn` | 0.54.0 |
| `cryptography` | 50.0.2 |
| `urllib3` | 2.8.0 |

---

## Setup

Clone this repository and open the project folder, then:

1. Install the dependencies:

   ```bash
   uv sync --locked
   ```

2. Create a file named `.env` in the project folder and add your LIFX token:

   ```
   LIFXKEY=your_lifx_token_here
   ```

   Keep this file out of Git. Anyone with this token can control your lights.

---

## Running the tests

```bash
uv run --locked python -m unittest discover -s tests -v
```

These checks cover tool discovery, all eight tool calls, invalid arguments, and LIFX failures. They use fake credentials and mocked LIFX requests, and exercise stdio and Streamable HTTP with both legacy and current protocol negotiation. They do not control real lights.

After an intentional dependency update, refresh Docker's requirements with:

```bash
uv export --locked --no-emit-project -o requirements.txt
```

---

## Option 1: Run it on your computer (`lfxlocalmcp.py`)

This is the simplest way to start. Your assistant app launches the server on your own computer, so there's nothing to deploy.

Start it once to check that it runs:

```bash
uv run --locked lfxlocalmcp.py
```

It will sit and wait for messages. That's normal; your assistant app is what talks to it.

For example, to use it from Claude Desktop, add it to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lifx-mcpserver": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/project", "run", "--locked", "lfxlocalmcp.py"]
    }
  }
}
```

Replace `/full/path/to/project` with the folder where you cloned this project, then restart the app. The light tools will show up. Other MCP apps use a similar setting; give them the same command and folder.

---

## Option 2: Run it as a web server (`lfxremotemcp.py`)

Choose this when your assistant connects to servers by URL, or when you want the server always available from anywhere.

Start it directly:

```bash
uv run --locked lfxremotemcp.py
```

Or build and run it with Docker, which uses a Python 3.13 image:

```bash
docker build -t lifx-mcpserver .
docker run --rm -p 3131:3131 --env-file .env lifx-mcpserver
```

The server then listens at:

```
http://localhost:3131/mcp
```

Things to know about the web server:

- It listens on all network addresses (`0.0.0.0`) on port `3131`, at the `/mcp` path.
- It is stateless and replies with plain JSON, so each request stands alone. This suits cloud hosting, where the server may restart or scale at any time.
- The `.env` file is not copied into the Docker image. Wherever you run it, you need to give it `LIFXKEY` as an environment variable, or the server won't start.

---

## Deploying to the cloud (optional)

You can host the Docker image on any service that runs containers, for example AWS (App Runner, ECS), Azure (Container Apps), Google Cloud Run, Railway, Render, or Fly.io. The steps are about the same everywhere:

1. **Get the image to your provider.** Push it to a container registry (Docker Hub, GitHub Container Registry, or your provider's own), or let the provider build it straight from your repository.
2. **Set your token.** Add `LIFXKEY` as an environment variable or secret in your provider's settings.
3. **Point traffic to port `3131`.** Set the container's port to `3131` and keep the `/mcp` path. If your provider requires a different port, change the `port` value in `lfxremotemcp.py` to match.
4. **Turn on HTTPS and protect the URL.** The server has no login of its own. Your LIFX token protects LIFX, but anyone who finds your server's URL could control your lights. Use your provider's access controls, a private network, or an authentication proxy.
5. **Connect your assistant.** Add your public URL, ending in `/mcp` (for example `https://your-server.example.com/mcp`), as a custom connector in your assistant.

If your provider "scales to zero" (shuts the server down when it isn't used), the first request after a quiet period may time out while it starts back up. Trying again usually works.

### Automatic deployment (optional)

You can deploy by hand, use your provider's built-in Git integration, or set up a CI/CD workflow.

This repository includes one example: a GitHub Actions workflow for Azure Container Apps at [`.github/workflows/deploy-azure.yml`](.github/workflows/deploy-azure.yml). On each push to `master`, it builds the image, pushes it to Docker Hub with two tags (`latest` and the commit ID), and updates an Azure Container App to the new version. If you use it, change `IMAGE_NAME`, `CONTAINER_APP_NAME`, and the branch to match your own setup, and make sure it passes your token to the app as `LIFXKEY`.

It needs these repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | What it is |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token |
| `AZURE_CREDENTIALS` | Service principal login for Azure (JSON) |
| `AZURE_RESOURCE_GROUP` | The resource group that holds the Container App |
| `LIFXKEY` | Your LIFX personal access token |

Using a different provider? Remove or replace this workflow with one for your platform.

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

3. Test it locally with `lfxlocalmcp.py`. If you also host the web server, redeploy it the way you normally do.

`set_bulb_brightness` and `set_bulb_color` already work with any bulb by name, so they need no changes.

---

## Troubleshooting

| Problem | Likely cause |
|---|---|
| Server stops right away with `LIFXKEY is required` | The token isn't set. Add it to `.env` locally, or set `LIFXKEY` in your hosting provider's settings. |
| `HTTP 401` | The LIFX token is wrong or has been revoked. Create a new one. |
| `HTTP 404` | No bulb has that label. Check the name in the LIFX app. |
| `HTTP 429` | Too many requests to LIFX in a short time. Wait a minute and try again. |
| Timeouts on the first request to a hosted server | The server was asleep (scaled to zero) and is starting up. Try again. |
| Assistant can't connect to a hosted server | Check that the URL ends in `/mcp`, the container port is `3131`, and the service is running. |

---

## Project files

```
├── lfx_controlers.py   # LIFX API calls (shared logic)
├── lfxlocalmcp.py      # Local server (stdio)
├── lfxremotemcp.py     # Web server (HTTP, port 3131)
├── Dockerfile          # Container image for the web server (Python 3.13)
├── pyproject.toml      # Project settings and dependencies
├── requirements.txt    # Pinned dependencies (exported by uv, used by Docker)
├── uv.lock             # Exact dependency versions for uv
├── tests/              # Automated checks (no real lights)
├── .github/workflows/  # Optional deployment example (Azure)
└── .env                # Your LIFX token (not committed)
```
