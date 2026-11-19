const { app, BrowserWindow, dialog, shell } = require("electron");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const net = require("node:net");

const APP_URL_HOST = "127.0.0.1";
const DEFAULT_PORT = 8765;
let bridgeProcess = null;
let mainWindow = null;
let bridgeLog = null;
let quitting = false;
let selectedPort = DEFAULT_PORT;

app.setName("AIWCC");
app.setAppUserModelId("com.aiwcc.desktop");

const isPackaged = app.isPackaged;
const projectRoot = isPackaged
  ? path.join(process.resourcesPath, "aiwcc")
  : path.resolve(__dirname, "..");
const bridgeScript = path.join(projectRoot, "bridge", "server.py");

function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    server.once("error", () => resolve(false));
    server.listen(port, APP_URL_HOST, () => server.close(() => resolve(true)));
  });
}

async function choosePort() {
  if (await checkPort(DEFAULT_PORT)) return DEFAULT_PORT;
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(0, APP_URL_HOST, () => {
      const port = server.address().port;
      server.close(() => resolve(port));
    });
  });
}

function healthCheck() {
  return new Promise((resolve) => {
    const req = http.get(
      { hostname: APP_URL_HOST, port: selectedPort, path: "/api/health", timeout: 1200 },
      (res) => {
        let body = "";
        res.setEncoding("utf8");
        res.on("data", (chunk) => (body += chunk));
        res.on("end", () => {
          try {
            const data = JSON.parse(body);
            resolve(res.statusCode === 200 && data.ok === true);
          } catch {
            resolve(false);
          }
        });
      }
    );
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForBridge(timeoutMs = 15000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await healthCheck()) return true;
    if (bridgeProcess && bridgeProcess.exitCode !== null) return false;
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  return false;
}

function startBridge() {
  if (!fs.existsSync(bridgeScript)) {
    throw new Error("No se encontró el servidor local: " + bridgeScript);
  }
  const python = process.platform === "win32" ? "python" : "python3";
  const logDir = path.join(app.getPath("userData"), "logs");
  fs.mkdirSync(logDir, { recursive: true });
  bridgeLog = fs.createWriteStream(path.join(logDir, "bridge.log"), { flags: "a" });
  bridgeProcess = spawn(python, [bridgeScript], {
    cwd: projectRoot,
    env: { ...process.env, AIWCC_PORT: String(selectedPort), PYTHONUNBUFFERED: "1" },
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true
  });
  bridgeProcess.stdout.pipe(bridgeLog);
  bridgeProcess.stderr.pipe(bridgeLog);
  bridgeProcess.on("error", (error) => {
    bridgeLog?.write("\n[AIWCC desktop] Bridge process error: " + error.message + "\n");
  });
  bridgeProcess.on("exit", (code, signal) => {
    bridgeLog?.write("\n[AIWCC desktop] Bridge exited: code=" + code + " signal=" + signal + "\n");
    bridgeProcess = null;
  });
}

function stopBridge() {
  if (!bridgeProcess) {
    bridgeLog?.end();
    bridgeLog = null;
    return;
  }
  const child = bridgeProcess;
  bridgeProcess = null;
  child.once("exit", () => {
    bridgeLog?.end();
    bridgeLog = null;
  });
  child.kill("SIGTERM");
  setTimeout(() => {
    if (child.exitCode === null && !child.killed) child.kill("SIGKILL");
  }, 2500).unref();
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1500,
    height: 950,
    minWidth: 1050,
    minHeight: 680,
    show: false,
    backgroundColor: "#080d16",
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true
    }
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("https://")) shell.openExternal(url);
    return { action: "deny" };
  });
  mainWindow.webContents.on("will-navigate", (event, url) => {
    const allowed = `http://${APP_URL_HOST}:${selectedPort}/`;
    if (!url.startsWith(allowed)) event.preventDefault();
  });
  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.on("closed", () => {
    mainWindow = null;
  });
  mainWindow.loadURL(`http://${APP_URL_HOST}:${selectedPort}/`);
}

app.whenReady().then(async () => {
  try {
    selectedPort = await choosePort();
    startBridge();
    const ready = await waitForBridge();
    if (!ready) throw new Error("AIWCC Bridge no respondió. Revisa el registro local.");
    createWindow();
  } catch (error) {
    dialog.showErrorBox("AIWCC no pudo iniciarse", error.message);
    app.quit();
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0 && !quitting) createWindow();
  });
});

app.on("before-quit", () => {
  quitting = true;
  stopBridge();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
