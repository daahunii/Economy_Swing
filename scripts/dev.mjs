import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
if (existsSync(path.join(root, ".env.local")))
  process.loadEnvFile(path.join(root, ".env.local"));
const python = path.join(root, "apps/backend/.venv/bin/python");
const apiPort = Number(process.env.API_PORT || 8100);
const webPort = Number(process.env.PORT || 3100);
if (!existsSync(python)) {
  console.error(
    "Python 가상환경이 없습니다. README의 설치 절차를 먼저 진행해 주세요.",
  );
  process.exit(1);
}
async function checkPort(port) {
  await new Promise((resolve, reject) => {
    const server = createServer();
    server.once("error", () =>
      reject(
        new Error(
          `${port} 포트가 사용 중이거나 접근할 수 없습니다. API_PORT 또는 PORT를 확인해 주세요.`,
        ),
      ),
    );
    server.listen(port, "127.0.0.1", () => server.close(resolve));
  });
}
await checkPort(apiPort);
await checkPort(webPort);
const children = [
  spawn(
    python,
    [
      "-m",
      "uvicorn",
      "app:app",
      "--host",
      "127.0.0.1",
      "--port",
      String(apiPort),
    ],
    { cwd: path.join(root, "apps/backend"), stdio: "inherit" },
  ),
  spawn(
    process.execPath,
    [
      path.join(root, "node_modules/next/dist/bin/next"),
      "dev",
      "--webpack",
      "--hostname",
      "127.0.0.1",
      "--port",
      String(webPort),
    ],
    {
      cwd: path.join(root, "apps/web"),
      stdio: "inherit",
      env: {
        ...process.env,
        BACKEND_URL: process.env.BACKEND_URL || `http://127.0.0.1:${apiPort}`,
      },
    },
  ),
];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  children.forEach((child) => child.kill("SIGTERM"));
  const timer = setTimeout(() => {
    children.forEach((child) => child.kill("SIGKILL"));
    process.exit(code);
  }, 3000);
  timer.unref();
  Promise.all(
    children.map(
      (child) =>
        new Promise((resolve) =>
          child.exitCode !== null ? resolve() : child.once("exit", resolve),
        ),
    ),
  ).then(() => process.exit(code));
}
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());
children.forEach((child) => {
  child.on("error", (error) => {
    console.error(error.message);
    stop(1);
  });
  child.on("exit", (code) => {
    if (!stopping) stop(code || 1);
  });
});
console.log(
  `Economy Swing: http://127.0.0.1:${webPort} · API: http://127.0.0.1:${apiPort}/docs`,
);
