#!/usr/bin/env node
"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const result = spawnSync("docker", ["compose", "run", "--rm", "tbox", ...process.argv.slice(2)], {
  cwd: root,
  stdio: "inherit",
  shell: process.platform === "win32",
});

if (result.error) {
  console.error("T-BOX requires Docker Desktop with Docker Compose available on PATH.");
  process.exitCode = 1;
} else {
  process.exitCode = result.status ?? 1;
}
