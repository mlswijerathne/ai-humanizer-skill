#!/usr/bin/env node
"use strict";

/**
 * ai-humanizer-skill installer.
 *
 * Copies the bundled skill into a Claude skills directory so Claude Code / the
 * Agent SDK can discover it. Cross-platform, zero dependencies.
 *
 * Usage:
 *   npx ai-humanizer-skill install            # install for current user (~/.claude/skills)
 *   npx ai-humanizer-skill install --project  # install into ./.claude/skills (this repo)
 *   npx ai-humanizer-skill install --dir DIR   # install into a custom skills dir
 *   npx ai-humanizer-skill uninstall           # remove it
 *   npx ai-humanizer-skill where               # print where it would install
 *   npx ai-humanizer-skill --help
 */

const fs = require("fs");
const os = require("os");
const path = require("path");

const SKILL_NAME = "ai-humanizer";
const PKG_SKILL_DIR = path.join(__dirname, "..", "skill");

function userSkillsDir() {
  return path.join(os.homedir(), ".claude", "skills");
}
function projectSkillsDir() {
  return path.join(process.cwd(), ".claude", "skills");
}

function parseArgs(argv) {
  const out = { cmd: argv[0], project: false, dir: null };
  for (let i = 1; i < argv.length; i++) {
    if (argv[i] === "--project") out.project = true;
    else if (argv[i] === "--dir") out.dir = argv[++i];
  }
  return out;
}

function targetSkillsDir(args) {
  if (args.dir) return path.resolve(args.dir);
  if (args.project) return projectSkillsDir();
  return userSkillsDir();
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

function help() {
  console.log(`
ai-humanizer-skill — install the AI Humanizer skill for Claude

Commands:
  install              Install for the current user (${userSkillsDir()})
  install --project    Install into ./.claude/skills (current directory)
  install --dir DIR    Install into a custom skills directory
  uninstall            Remove the installed skill
  where                Print the install destination without writing
  help                 Show this message

After installing, restart Claude Code (or reload skills) and run /ai-humanizer,
or just ask Claude to "humanize this text".
`);
}

function install(args) {
  const dest = path.join(targetSkillsDir(args), SKILL_NAME);
  if (!fs.existsSync(PKG_SKILL_DIR)) {
    console.error("error: bundled skill payload not found at " + PKG_SKILL_DIR);
    process.exit(1);
  }
  if (fs.existsSync(dest)) {
    console.log("Updating existing install at " + dest);
    fs.rmSync(dest, { recursive: true, force: true });
  }
  copyDir(PKG_SKILL_DIR, dest);
  console.log("Installed ai-humanizer skill to:\n  " + dest);
  console.log("\nNext: restart Claude Code, then run /ai-humanizer or ask Claude to humanize text.");
  console.log("The before/after scorer needs Python 3: python \"" + path.join(dest, "scripts", "score.py") + "\" file.txt");
}

function uninstall(args) {
  const dest = path.join(targetSkillsDir(args), SKILL_NAME);
  if (fs.existsSync(dest)) {
    fs.rmSync(dest, { recursive: true, force: true });
    console.log("Removed " + dest);
  } else {
    console.log("Nothing to remove at " + dest);
  }
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  switch (args.cmd) {
    case "install":
      install(args);
      break;
    case "uninstall":
      uninstall(args);
      break;
    case "where":
      console.log(path.join(targetSkillsDir(args), SKILL_NAME));
      break;
    case "help":
    case "--help":
    case "-h":
    case undefined:
      help();
      break;
    default:
      console.error('Unknown command: "' + args.cmd + '"');
      help();
      process.exit(1);
  }
}

main();
