#!/usr/bin/env python3
"""Verify React tech-card TypeScript/TSX examples.

The React chapter intentionally contains a mix of complete components and short
snippet-style examples. This verifier extracts `ts`, `tsx`, and `typescript`
Markdown blocks, adds a tiny React type shim plus common placeholder values, and
runs TypeScript in strict mode. Snippets that start with `return` are wrapped in a
function body so list-rendering examples can still be type-checked.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REACT_DIR = ROOT / "tech-cards-handbook" / "chapters" / "react"
README = REACT_DIR / "README.md"
EXPECTED_CARD_COUNT = 42
TYPESCRIPT_VERSION = "5.9.3"

CODE_BLOCK_RE = re.compile(r"```(?:tsx|ts|typescript)\s*\n(.*?)\n```", re.DOTALL)

REACT_SHIM = r'''
export type ReactNode = unknown;
export type ErrorInfo = { componentStack?: string | null };
export type ComponentType<P = {}> = (props: P) => JSX.Element;
export class Component<P = {}, S = {}> {
  props: P;
  state: S;
  constructor(props: P);
  setState(next: Partial<S> | S): void;
  static getDerivedStateFromError?(error: unknown): unknown;
  componentDidCatch?(error: Error, errorInfo: ErrorInfo): void;
  render?(): ReactNode;
}
export function useState<T>(initial: T | (() => T)): [T, (next: T | ((current: T) => T)) => void];
export function useEffect(effect: () => void | (() => void), deps?: readonly unknown[]): void;
export function useMemo<T>(factory: () => T, deps: readonly unknown[]): T;
export function useCallback<T extends (...args: never[]) => unknown>(callback: T, deps: readonly unknown[]): T;
export function useDeferredValue<T>(value: T): T;
export function useTransition(): [boolean, (callback: () => void) => void];
export function useRef<T>(initial?: T): { current: T | undefined };
export function useReducer<S, A>(reducer: (state: S, action: A) => S, initialState: S): [S, (action: A) => void];
export function useId(): string;
export function useSyncExternalStore<T>(
  subscribe: (listener: () => void) => () => void,
  getSnapshot: () => T,
  getServerSnapshot?: () => T,
): T;
export type Context<T> = { Provider: (props: { value: T; children?: ReactNode }) => JSX.Element };
export function createContext<T>(defaultValue: T): Context<T>;
export function useContext<T>(context: Context<T>): T;
export function useActionState<S, P>(
  action: (previousState: S, payload: P) => S | Promise<S>,
  initialState: S,
  permalink?: string,
): [S, (payload: P) => void, boolean];
export function useOptimistic<S, V>(state: S, updateFn: (currentState: S, optimisticValue: V) => S): [S, (optimisticValue: V) => void];
export function Suspense(props: { fallback?: ReactNode; children?: ReactNode }): JSX.Element;
export function lazy<P>(loader: () => Promise<{ default: ComponentType<P> }>): ComponentType<P>;
export function memo<T extends (...args: never[]) => unknown>(component: T): T;
export type ProfilerOnRenderCallback = (
  id: string,
  phase: 'mount' | 'update' | 'nested-update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number,
) => void;
export function Profiler(props: { id: string; onRender: ProfilerOnRenderCallback; children?: ReactNode }): JSX.Element;
'''

JSX_RUNTIME_SHIM = r'''
export namespace JSX {
  interface Element {}
  interface IntrinsicAttributes { key?: string | number }
  interface IntrinsicElements { [elemName: string]: any }
}
export const jsx: unknown;
export const jsxs: unknown;
export const Fragment: unknown;
'''

REACT_DOM_SHIM = r'''
export function useFormStatus(): {
  pending: boolean;
  data: FormData | null;
  method: string | null;
  action: string | ((formData: FormData) => void | Promise<void>) | null;
};
'''

BASE_PRELUDE = r'''
export {};

declare global {
  namespace JSX {
    interface Element {}
    interface IntrinsicAttributes { key?: string | number }
    interface IntrinsicElements { [elemName: string]: any }
  }
}

declare const todos: Array<{ id: string; title: string; done: boolean }>;
declare const items: Array<{ id: string; title: string }>;
declare const query: string;
declare function TodoItem(props: { key?: string; todo: { id: string; title: string; done: boolean } }): JSX.Element;
declare function fetchData(): Promise<unknown>;
declare function setData(data: unknown): void;
declare const userId: string;
declare function setUser(user: unknown): void;
declare function setError(error: unknown): void;
declare function expensiveComputation(): unknown;
declare function saveDraft(): Promise<void>;
declare function showToast(message: string): void;
declare function reportRenderError(error: Error, errorInfo: unknown): void;
declare function RevenueChart(): JSX.Element;
declare function RecentOrders(): JSX.Element;
'''

HOOK_PRELUDE = r'''
declare function useState<T>(initial: T | (() => T)): [T, (next: T | ((current: T) => T)) => void];
declare function useEffect(effect: () => void | (() => void), deps?: readonly unknown[]): void;
declare function useMemo<T>(factory: () => T, deps: readonly unknown[]): T;
declare function useCallback<T extends (...args: never[]) => unknown>(callback: T, deps: readonly unknown[]): T;
declare function useDeferredValue<T>(value: T): T;
declare function useTransition(): [boolean, (callback: () => void) => void];
declare function useRef<T>(initial?: T): { current: T | undefined };
declare function useReducer<S, A>(reducer: (state: S, action: A) => S, initialState: S): [S, (action: A) => void];
declare function useId(): string;
declare function useSyncExternalStore<T>(
  subscribe: (listener: () => void) => () => void,
  getSnapshot: () => T,
  getServerSnapshot?: () => T,
): T;
declare function useActionState<S, P>(
  action: (previousState: S, payload: P) => S | Promise<S>,
  initialState: S,
  permalink?: string,
): [S, (payload: P) => void, boolean];
declare function useOptimistic<S, V>(state: S, updateFn: (currentState: S, optimisticValue: V) => S): [S, (optimisticValue: V) => void];
'''


@dataclass(frozen=True)
class CheckResult:
    card: str
    block_count: int
    command: str
    stdout: str
    stderr: str


def read_cards(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    cards: list[str] = []
    for match in re.finditer(r"\[`[^`]+`\]\(([^)]+\.md)\)", text):
        filename = match.group(1)
        if filename != "README.md" and filename not in cards:
            cards.append(filename)
    return cards


def extract_react_blocks(markdown: str) -> list[str]:
    return CODE_BLOCK_RE.findall(markdown)


def prepare_block(block: str, index: int) -> str:
    stripped = block.lstrip()
    if stripped.startswith("return ") or stripped.startswith("return(") or stripped.startswith("return\n"):
        block = f"function ReactCardReturnSnippet{index}() {{\n{block}\n}}"
    hook_prelude = "" if re.search(r"from\s+['\"]react['\"]", block) else HOOK_PRELUDE
    return f"{BASE_PRELUDE}\n{hook_prelude}\n{block}\n"


def write_react_shim(temp_dir: Path) -> None:
    react_dir = temp_dir / "node_modules" / "react"
    react_dir.mkdir(parents=True, exist_ok=True)
    (react_dir / "index.d.ts").write_text(REACT_SHIM, encoding="utf-8")
    runtime_dir = react_dir / "jsx-runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "index.d.ts").write_text(JSX_RUNTIME_SHIM, encoding="utf-8")
    react_dom_dir = temp_dir / "node_modules" / "react-dom"
    react_dom_dir.mkdir(parents=True, exist_ok=True)
    (react_dom_dir / "index.d.ts").write_text(REACT_DOM_SHIM, encoding="utf-8")


def command_text(command: list[str]) -> str:
    return " ".join(command)


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        combined = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
        raise RuntimeError(f"command failed: {command_text(command)}\n{combined}")
    return result


def verify_card(card: str, blocks: list[str], temp_dir: Path) -> CheckResult:
    stem = Path(card).stem
    commands: list[str] = []
    outputs: list[str] = []
    for index, block in enumerate(blocks, start=1):
        source = temp_dir / f"{stem}-{index}.tsx"
        source.write_text(prepare_block(block, index), encoding="utf-8")
        command = [
            "npx",
            "-y",
            "-p",
            f"typescript@{TYPESCRIPT_VERSION}",
            "tsc",
            "--noEmit",
            "--strict",
            "--jsx",
            "react-jsx",
            "--lib",
            "es2020,dom",
            "--moduleResolution",
            "node",
            "--module",
            "commonjs",
            "--skipLibCheck",
            source.name,
        ]
        result = run(command, cwd=temp_dir)
        commands.append(command_text(command))
        outputs.extend(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return CheckResult(
        card=card,
        block_count=len(blocks),
        command=" && ".join(commands),
        stdout="\n".join(outputs),
        stderr="",
    )


def verify() -> list[CheckResult]:
    if shutil.which("npx") is None:
        raise RuntimeError("npx is required to run TypeScript compiler checks")

    cards = read_cards(README)
    if len(cards) != EXPECTED_CARD_COUNT:
        raise RuntimeError(f"expected {EXPECTED_CARD_COUNT} React cards in README, found {len(cards)}")

    results: list[CheckResult] = []
    with tempfile.TemporaryDirectory(prefix="react-card-verify-") as directory:
        temp_dir = Path(directory)
        write_react_shim(temp_dir)
        for card in cards:
            card_path = REACT_DIR / card
            blocks = extract_react_blocks(card_path.read_text(encoding="utf-8"))
            if not blocks:
                raise RuntimeError(f"{card}: expected at least one ts/tsx/typescript code block, found 0")
            results.append(verify_card(card, blocks, temp_dir))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify React tech-card TypeScript/TSX examples.")
    parser.add_argument("--verbose", action="store_true", help="print captured compiler output")
    args = parser.parse_args()

    try:
        results = verify()
    except Exception as error:  # noqa: BLE001 - CLI should surface a concise failure.
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    total_blocks = sum(result.block_count for result in results)
    print(f"verified {len(results)} React cards with {total_blocks} code blocks")
    for result in results:
        print(f"ok: {result.card} :: blocks={result.block_count} :: {result.command}")
        if args.verbose:
            combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
            if combined:
                indented = "\n".join(f"    {line}" for line in combined.splitlines())
                print(indented)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
